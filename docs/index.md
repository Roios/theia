# Theia

A simple, modular perception project designed to work with the multiple sensors. Theia provides a clean hardware abstraction layer and comprehensive tools for capturing and displaying synchronized multi-modal sensor data.

> This is a playground project for now.

## Overview

Theia is built around the concept of a **hardware-agnostic camera interface**, allowing you to:

- Capture synchronized RGB, stereo depth, and IMU data from sensors.
- Display camera streams in real-time with full control over which streams to enable/disable
- Build perception applications on top of a reliable, tested foundation

The project tries to follow best practices in:
- Hardware abstraction and modularity
- Sensor synchronization and timing
- Stream management and display
- Type-safe Python development

## Key components

- **Data models** (`common.data_models`): Strongly-typed representations of camera frames and sensor data
- **Camera abstraction** (`common.generic_camera`): Hardware-agnostic `Camera` interface
- **OAK-D implementation** (`hardware.oakd`): Production-ready implementation for OAK-D stereo cameras
- **Display system** (`theia.display_streams`): Real-time stream visualization with OpenCV
- **CLI tools** (`theia.cli`): Command-line interface for quick access to features

## Supported devices

At the moment, Theia supports:
- OAK-D stereo camera (tested with the first generation) [link]([!](https://shop.luxonis.com/products/oak-d))



## Quick start

### Installation

In the repo's root:

```bash
uv sync
```

### Display camera streams

```bash
uv run display_streams
```

Use command-line flags to control which streams are displayed:

```bash
uv run display_streams --no-rgb --no-left --no-right
```

See [Installation](installation.md) for setup instructions.

## Architecture

Theia is organized into three main layers:

1. **Common layer**: Data models and hardware-agnostic abstractions
2. **Hardware layer**: Device-specific implementations (e.g., OAK-D)
3. **Application layer**: CLI tools and real applications

See [Architecture](architecture.md) for an in-depth explanation of the design.


## Dependencies

- Python ≥ 3.12
- DepthAI 3.9.0+ (OAK-D SDK)
- OpenCV 5.0.0+
- NumPy 2.5.2+
- Click 8.5.0+ (CLI framework)

## Development

Theia uses modern Python tooling:

- **Dependency management**: UV (`uv`)
- **Code quality**: Ruff (`ruff`)
- **Documentation**: MkDocs with Material theme
- **Build backend**: UV build

## Next steps

- [Installation guide](installation.md) - Get started with Theia
- [Architecture](architecture.md) - Understand the system design

## License

Apache License - See [LICENSE](../LICENSE) for details

## Author

[Roios](https://github.com/Roios)
