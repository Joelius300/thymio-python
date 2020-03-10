# Communication with Thymio via serial port or tcp
# Author: Yves Piguet, EPFL

import asyncio
import threading
import time

from thymio.connection import Connection


class Thymio:
    """Helper object for communicating with one or several Thymios connected to
    a single port.
    """

    class _ThymioProxy:

        def __init__(self, thymio):
            self.thymio = thymio
            self.connection = None
            self.loop = asyncio.get_event_loop()
            self.nodes = set()

        def run(self):

            async def on_connection_changed(node_id, connected):
                if connected:
                    self.nodes.add(node_id)
                    if self.thymio.on_connect_cb:
                        self.thymio.on_connect_cb(node_id)
                else:
                    self.nodes.remove(node_id)
                    if self.thymio.on_disconnect_cb:
                        self.thymio.on_disconnect_cb(node_id)

            async def on_variables_received(node_id):
                if node_id in self.thymio.variable_observers:
                    variable_observer = self.thymio.variable_observers[node_id]
                    variable_observer(node_id)

            self.connection = Connection.serial(discover_rate=self.thymio.discover_rate,
                                                refreshing_rate=self.thymio.refreshing_rate,
                                                loop=self.loop)
            self.connection.on_connection_changed = on_connection_changed
            self.connection.on_variables_received = on_variables_received

            self.loop.run_forever()

    def __init__(self,
                 on_connect=None,
                 on_disconnect=None,
                 refreshing_rate=0.1,
                 discover_rate=2,
                 loop=None):
        self.on_connect_cb = on_connect
        self.on_disconnect_cb = on_disconnect
        self.refreshing_rate = refreshing_rate
        self.discover_rate = discover_rate
        self.loop = loop or asyncio.get_event_loop()
        self.thymio_proxy = None
        self.variable_observers = {}

    def connect(self):
        """Connect to Thymio or dongle.
        """
        def thymio_thread():
            asyncio.set_event_loop(asyncio.new_event_loop())
            self.thymio_proxy = self._ThymioProxy(self)
            self.thymio_proxy.run()
        self.thread = threading.Thread(target=thymio_thread)
        self.thread.start()
        while self.thymio_proxy is None or len(self.thymio_proxy.nodes) == 0:
            time.sleep(0.1)

    def nodes(self):
        """Get set of ids of node currentlty connected.
        """
        return self.thymio_proxy.nodes if self.thymio_proxy else set()

    def first_node(self):
        """Get id of first node connected.
        """
        return next(iter(self.nodes()))

    def variables(self, node_id):
        """Get list of variable names.
        """
        node = self.thymio_proxy.connection.remote_nodes[node_id]
        return node.named_variables

    def variable_size(self, node_id, var_name):
        """Get the size of a variable.
        """
        node = self.thymio_proxy.connection.remote_nodes[node_id]
        return node.var_size[var_name]

    def variable_offset(self, node_id, var_name):
        """Get the offset (address) of a variable.
        """
        node = self.thymio_proxy.connection.remote_nodes[node_id]
        return node.var_offset[var_name]

    def __getitem__(self, key):
        class Node:
            def __init__(self_node, node_id):
                self_node.node_id = node_id
            def __getitem__(self_node, name):
                try:
                    val = self.thymio_proxy.connection.get_var_array(self_node.node_id, name)
                    return val if len(val) != 1 else val[0]
                except KeyError:
                    raise KeyError(name)
            def __setitem__(self_node, name, val):
                try:
                    if isinstance(val, list):
                        self.thymio_proxy.connection.set_var_array(self_node.node_id, name, val)
                    else:
                        self.thymio_proxy.connection.set_var(self_node.node_id, name, val)
                except KeyError:
                    raise KeyError(name)

        return Node(key)

    def set_variable_observer(self, node_id, observer):
        self.variable_observers[node_id] = observer