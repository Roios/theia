# Architecture overview

## Design principles

Theia is built on three core principles:

1. **Hardware abstraction**: All hardware-specific code is isolated behind a clean interface
2. **Modularity**: Components are independent and loosely coupled
3. **Type safety**: Extensive use of Python type hints for correctness and IDE support

## Layered architecture

```
┌────────────────────────┐
│   Application layer    │
│  (theia)               │
└──────────────┬─────────┘
               │
┌──────────────▼───────────┐
│   Abstraction layer      │
│  (common)                │
└──────────────┬───────────┘
               │
┌──────────────▼─────────────────────┐
│   Hardware implementation layer    │
│  (hardware)                        │
└────────────────────────────────────┘
               │
               ├──► OAK-D stereo camera
               └──► OpenCV webcam
```

## Module organization

### `common/` - Shared abstractions

This layer contains all hardware-agnostic code that can be used by any implementation.

#### `common.data_models`
- `Vector3`: A 3D vector with x, y, z components
- `IMUData`: Container for accelerometer, gyroscope, and magnetometer readings
- `Metaframe`: A synchronized set of frames captured at one instant from multiple sensors

All data models are **frozen dataclasses**, making them immutable and hashable.

#### `common.generic_camera`
- `Camera`: Abstract base class defining the camera interface
  - `__enter__()` / `__exit__()`: Context manager for resource management
  - `start()`: Begin streaming frames
  - `stop()`: Stop streaming frames
  - `is_running()`: Check if actively streaming
  - `get_frames()`: Block until the next synchronized frame set is available

Any hardware implementation must extend `Camera` and provide all abstract methods.

### `hardware/` - Hardware-specific implementations

This layer contains production implementations for specific camera hardware.

#### `hardware.oakd/`

**`config.py`**
- Hardware configuration constants
- Resolution settings for RGB and mono cameras
- Synchronization parameters
- IMU sensor configuration

**`camera.py`**
- `OakDCamera`: Implements the `Camera` interface for OAK-D stereo cameras
- Manages the DepthAI pipeline and device lifecycle
- Handles frame synchronization across RGB, stereo, depth, and IMU streams
- Performs coordinate transformations (e.g., DepthAI IMU coordinates to standard 3D vectors)

**Key implementation details:**
- Uses DepthAI's `Sync` node for on-device frame synchronization (lower latency)
- Configurable per-stream enabling (control power consumption and bandwidth)
- Automatic IMU batch processing to extract the latest sensor data
- Proper resource cleanup in `__exit__()` even when exceptions occur

#### `hardware.webcam/`

**`camera.py`**
- `WebcamCamera`: Implements the `Camera` interface using OpenCV's
     `VideoCapture`
- Produces one color frame in `Metaframe.rgb`
- Leaves stereo, depth, and IMU fields as `None`

### `theia/` - Application layer

User-facing tools and utilities.

#### `cli.py`
- `display_streams`: Click command that orchestrates camera streaming and display
- Command-line argument parsing for stream control (`--no-rgb`, `--no-left`, etc.)
- Logging setup for observability

#### `display_streams.py`
- `display_camera_streams()`: Core function that handles real-time stream visualization
- OpenCV window management and rendering
- Frame normalization and colorization (especially for depth maps using jet colormap)
- Graceful shutdown on user input (Q or ESC)

## Data flow

### Typical execution flow

```
User command
    │
    └──► CLI (theia.cli.display_streams)
         │
         └──► Selected camera backend.__enter__()
              │
              └──► Hardware-specific setup
                   ├── Open the OAK-D pipeline
                   └── Open the OpenCV webcam
              │
              └──► camera.start()
                   │
                   └──► Pipeline.start()
                        │
                        └──► DepthAI Device begins streaming
                             │
                             └──► display_camera_streams()
                                  │
                                  └──► Loop:
                                       ├── camera.get_frames() [BLOCKING]
                                       │   └── Sync node delivers synchronized message group
                                       │
                                       ├── Extract individual frames
                                       ├── Normalize/colorize
                                       └── Display with OpenCV
                             │
                             └──► User presses Q/ESC
                                  │
                                  └──► camera.stop()
                                  └──► camera.__exit__()
                                       └──► Pipeline cleanup & device release
```

### Frame synchronization

Theia synchronizes frames on the OAK-D device itself (not the host) to minimize latency:

1. **Device-side sync**: Each camera and IMU node sends frames to the Sync node
2. **Threshold check**: Sync compares timestamps across all streams
3. **Bundling**: Frames within `SYNC_TIME_THRESHOLD` (50ms) are bundled together
4. **Output**: A single synchronized `Metaframe` is delivered to the host

This is more reliable than host-side synchronization because:
- No network or OS latency jitter affects synchronization
- Timestamps are from the device's monotonic clock
- Reduces CPU usage on the host

## Stream configuration

The `OakDCamera` constructor allows fine-grained control over which streams to enable:

```python
camera = OakDCamera(
    enable_rgb=True,  # Color camera
    enable_left=True,  # Left mono camera (for stereo)
    enable_right=True,  # Right mono camera (for stereo)
    enable_depth=True,  # Computed stereo depth map
    enable_imu=True,  # Inertial measurement unit
)
```

Each disabled stream:
- Reduces power consumption
- Lowers bandwidth usage
- Improves latency for remaining streams
- Appears as `None` in the returned `Metaframe`

## Error handling

### Context manager pattern

All hardware resources follow Python's context manager protocol:

```python
with camera:  # __enter__: Acquire resources
    camera.start()
    # Use camera
    camera.stop()
# __exit__: Release resources (even if exception occurred)
```

This ensures:
- USB device is properly released
- Pipeline is cleanly stopped
- No resource leaks

### Logging

Comprehensive logging at INFO and WARNING levels:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Starting OAK-D...")
logger.warning("Depth requires left and right cameras; enabling them.")
logger.error("Failed to build OAK-D pipeline: %s", exc)
```

## Extending the architecture

### Adding a new Camera backend

To support a different camera (e.g., Intel RealSense, Zed), create a new implementation:

1. Create `hardware/{device}/camera.py`
2. Implement the `Camera` interface:
   ```python
   class MyCamera(Camera):
       def __enter__(self) -> "MyCamera": ...
       def __exit__(self, ...): ...
       def start(self) -> None: ...
       def stop(self) -> None: ...
       def is_running(self) -> bool: ...
       def get_frames(self) -> Metaframe: ...
   ```
3. Update imports in `theia.cli` and `theia.display_streams`
4. Application code remains unchanged

### Adding a new data model

New sensor data (e.g., thermal imaging) can be added to `common.data_models`:

```python
@dataclass(frozen=True)
class Metaframe:
    timestamp: datetime
    rgb: np.ndarray | None = None
    # ... existing fields ...
    thermal: np.ndarray | None = None  # NEW
```

All implementations and applications can then use this new field.
