"""Data models used throughout the project."""

from dataclasses import dataclass
from datetime import datetime

import numpy as np


@dataclass(frozen=True)
class Vector3:
    """A 3D vector."""

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class IMUData:
    """Inertial measurement unit data.

    Attributes:
        accelerometer: Acceleration in m/s^2, or None if not enabled.
        gyroscope: Angular velocity in rad/s, or None if not enabled.
        magnetometer: Magnetic field in Tesla, or None if not enabled.
    """

    accelerometer: Vector3 | None = None
    gyroscope: Vector3 | None = None
    magnetometer: Vector3 | None = None


@dataclass(frozen=True)
class Metaframe:
    """A synchronized set of frames captured from a device at one instant.

    Attributes:
        timestamp: When this set of frames was captured.
        rgb: Color image, or None if not provide it.
        left: Left mono image, or None if not provided.
        right: Right mono image, or None if not provided.
        depth: Depth map, or None if not provided.
        imu: IMU data, or None if not provided.

    A field is None when that stream is not produced by the camera
    (e.g. it was disabled, or the camera does not support it).
    """

    timestamp: datetime
    # image data
    rgb: np.ndarray | None = None
    left: np.ndarray | None = None
    right: np.ndarray | None = None
    depth: np.ndarray | None = None
    # IMU data
    imu: IMUData | None = None
