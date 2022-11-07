# Changelog

Notable changes of thymiodirect. Release versions refer to [https://pypi.org/project/thymiodirect/].

## [Unreleased] - 2022-11-07 - Joel L.

- Add "modern" `pip install .` instructions to readme
- Add type hints for various methods and fields
- Restructure modules in a way that allows referencing the classes both directly without installation and as installed package
- Add `with` capabilities to Tyhmio for more robust connection teardown handling and cancellation handling
- Handle encoding errors during serial port discovery
- Handle various exceptions e.g. during shutdown
- Add various constants for sensor access
- Add new observer API (`ThymioObserver`) for simplified variable observer implementations without global data and redundancies
- Add `SingleSerialThymioRunner` to get started with very minimal boilerplate for the common scenario of one thyimo connected via USB dongle or cable
- Code cleanup

## [Unreleased] - 2021-05-17 - Nicolas Despres

- Code cleanup
- Progress callback during connection
- Prevent proxy shutdown from being called twice
- New method `thymio.device_names()` to get a dictionary of node_ids and their respective device names
- New method `thymio.device_name(node_id)` to get the device name of a certai node

## [Unreleased] - 2020-11-26

- Clean teardown of event loops upon termination.
- Implementation overview in readme.md.
- Assembler documentation revised and converted to markdown.
- New method `thymiodirect.thymio_serial_ports.ThymioSerialPort.get_ports()` to get the serial ports a Thymio is connected to.

## [0.1.2] - 2020-11-17

### Added

- Callback for communication error notification.
- Support to restrict the refresh of variable data to the span covering a set of variables.
- Changelog.

## [0.1.1] - 2020-08-31

### Added

- Markdown documentation.

## [0.1.0] - 2020-08-27

### Added

- First release on PyPI.
