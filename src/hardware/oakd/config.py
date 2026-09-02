"""Configuration for OAK-D."""

from typing import Final

# color camera (CAM_A) output resolution.
RGB_WIDTH: Final[int] = 1280
RGB_HEIGHT: Final[int] = 720

# left (CAM_B) and right (CAM_C) mono cameras output resolution
MONO_WIDTH: Final[int] = 640
MONO_HEIGHT: Final[int] = 400

# sync happens on the on device to avoid host latency
SYNC_ON_HOST: Final[bool] = False

# sync time threshold
SYNC_TIME_THRESHOLD: Final[int] = 50  # milliseconds

# IMU sensor report rate in Hz
IMU_REPORT_RATE: Final[int] = 100

# IMU batch settings
IMU_BATCH_REPORT_THRESHOLD: Final[int] = 1
IMU_MAX_BATCH_REPORTS: Final[int] = 10
