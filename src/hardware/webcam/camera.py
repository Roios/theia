"""Webcam camera implementation."""

import logging
from datetime import UTC, datetime
from types import TracebackType
from typing import Self

import cv2

from common.data_models import Metaframe
from common.generic_camera import Camera
from hardware.webcam.config import RGB_HEIGHT, RGB_WIDTH

logger = logging.getLogger(__name__)


class WebcamCamera(Camera):
    """Camera implementation for a webcam exposed through OpenCV."""

    def __init__(self, device_index: int = 0) -> None:
        """Configure which webcam device to use.

        Args:
            device_index: OpenCV device index, usually 0 for the default
                webcam.
        """
        self._device_index = device_index
        self._capture: cv2.VideoCapture | None = None
        self._running = False

        self._apply_resize = RGB_WIDTH > 0 and RGB_HEIGHT > 0

    def __enter__(self) -> Self:
        """Open the webcam device."""
        capture = cv2.VideoCapture(self._device_index)
        if not capture.isOpened():
            capture.release()
            raise RuntimeError(f"Unable to open webcam device {self._device_index}.")

        self._capture = capture
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Stop streaming and release the webcam device."""
        self._running = False
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def start(self) -> None:
        """Start reading frames from the webcam."""
        logger.info("Starting webcam...")
        if self._capture is None or not self._capture.isOpened():
            raise RuntimeError("Webcam must be opened before starting.")
        self._running = True

    def stop(self) -> None:
        """Stop reading frames from the webcam."""
        logger.info("Stopping webcam...")
        self._running = False

    def is_running(self) -> bool:
        """Return whether the webcam is currently streaming."""
        return self._running and self._capture is not None and self._capture.isOpened()

    def get_frames(self) -> Metaframe:
        """Read the next webcam frame.

        Returns:
            A Metaframe containing the webcam's color frame in rgb.
        """
        if not self.is_running() or self._capture is None:
            raise RuntimeError("Webcam must be started before reading frames.")

        success, frame = self._capture.read()
        if not success:
            raise RuntimeError("Failed to read a frame from the webcam.")

        if self._apply_resize:
            frame = cv2.resize(frame, (RGB_WIDTH, RGB_HEIGHT))

        return Metaframe(timestamp=datetime.now(tz=UTC), rgb=frame)
