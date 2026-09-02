# Installation guide

## Prerequisites

- Python 3.12 or higher
- OAK-D camera (1st generation or compatible)
- UV package manager

## Development installation

If you want to contribute or develop on Theia:

```bash
# Clone the repository
git clone https://github.com/Roios/theia.git
cd theia

# Install with UV
uv sync --all-groups
```

### What's included:

- **dev**: Ruff (code linting and formatting)
- **docs**: MkDocs and Material theme (documentation building)


## Hardware setup

### OAK-D Camera

1. **Connect your OAK-D camera** via USB-C to your computer
2. **Verify the camera is detected** by running:

```bash
python -c "import depthai; print(depthai.Device().getConnectedDevices())"
```

If successful, you should see information about your connected OAK-D device.
