"""OAK-D camera implementation."""

import logging
from datetime import UTC, datetime, timedelta
from types import TracebackType
from typing import Self

import depthai as dai

from common.data_models import IMUData, Metaframe, Vector3
from common.generic_camera import Camera
from hardware.oakd.config import (
    IMU_BATCH_REPORT_THRESHOLD,
    IMU_MAX_BATCH_REPORTS,
    IMU_REPORT_RATE,
    MONO_HEIGHT,
    MONO_WIDTH,
    RGB_HEIGHT,
    RGB_WIDTH,
    SYNC_ON_HOST,
    SYNC_TIME_THRESHOLD,
)

logger = logging.getLogger(__name__)


class OakDCamera(Camera):
    """Camera implementation for the OAK-D stereo camera."""

    _pipeline: dai.Pipeline
    _sync_queue: dai.MessageQueue | None
    _depth_queue: dai.MessageQueue | None

    def __init__(
        self,
        enable_rgb: bool = True,
        enable_left: bool = True,
        enable_right: bool = True,
        enable_depth: bool = True,
        enable_imu: bool = True,
    ) -> None:
        """Configure which streams the pipeline will produce.

        Args:
            enable_rgb: Whether to build and stream the color camera.
            enable_left: Whether to build and stream the left mono camera.
            enable_right: Whether to build and stream the right mono camera.
            enable_depth: Whether to compute and stream the stereo depth
                map. Requires the left and right cameras, which are
                enabled automatically (with a warning) if not requested.
            enable_imu: Whether to enable the IMU.
        """
        if enable_depth and not (enable_left and enable_right):
            logger.warning(
                "enable_depth requires enable_left and enable_right; "
                "enabling them both."
            )
            enable_left = True
            enable_right = True

        self._enable_rgb = enable_rgb
        self._enable_left = enable_left
        self._enable_right = enable_right
        self._enable_depth = enable_depth
        self._enable_imu = enable_imu

        self._sync_queue = None
        self._depth_queue = None

    def __enter__(self) -> Self:
        """Open the pipeline and build the requested nodes."""
        pipeline = dai.Pipeline()

        try:
            self._pipeline = pipeline.__enter__()
            self._build_pipeline()
        except BaseException as exc:
            logger.error("Failed to build OAK-D pipeline: %s", exc)
            pipeline.__exit__(type(exc), exc, exc.__traceback__)
            raise

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Stop the pipeline and release the device."""
        try:
            if self._pipeline.isRunning():
                self._pipeline.stop()
        finally:
            self._pipeline.__exit__(exc_type, exc_value, traceback)

    def _build_pipeline(self) -> None:
        """Create the nodes and output queues for enabled streams."""
        left_output = None
        right_output = None

        # run cameras as synchronized as possible
        sync = self._pipeline.create(dai.node.Sync)
        sync.setRunOnHost(SYNC_ON_HOST)
        sync.setSyncThreshold(timedelta(milliseconds=SYNC_TIME_THRESHOLD))

        if self._enable_rgb:
            rgb = self._pipeline.create(dai.node.Camera).build(
                dai.CameraBoardSocket.CAM_A
            )
            rgb_output = rgb.requestOutput(
                (RGB_WIDTH, RGB_HEIGHT),
                type=dai.ImgFrame.Type.BGR888p,
            )
            rgb_output.link(sync.inputs["rgb"])

        if self._enable_left:
            left = self._pipeline.create(dai.node.Camera).build(
                dai.CameraBoardSocket.CAM_B
            )
            left_output = left.requestOutput(
                (MONO_WIDTH, MONO_HEIGHT),
                type=dai.ImgFrame.Type.GRAY8,
            )
            left_output.link(sync.inputs["left"])

        if self._enable_right:
            right = self._pipeline.create(dai.node.Camera).build(
                dai.CameraBoardSocket.CAM_C
            )
            right_output = right.requestOutput(
                (MONO_WIDTH, MONO_HEIGHT),
                type=dai.ImgFrame.Type.GRAY8,
            )
            right_output.link(sync.inputs["right"])

        if self._enable_depth:
            # depth needs left and right cameras
            if left_output is None:
                raise ValueError(
                    "Left camera output is required for depth computation."
                )
            elif right_output is None:
                raise ValueError(
                    "Right camera output is required for depth computation."
                )

            stereo = self._pipeline.create(dai.node.StereoDepth)
            left_output.link(stereo.left)
            right_output.link(stereo.right)

            self._depth_queue = stereo.depth.createOutputQueue()

        if self._enable_imu:
            imu = self._pipeline.create(dai.node.IMU)
            imu.enableIMUSensor(
                [
                    dai.IMUSensor.ACCELEROMETER_RAW,
                    dai.IMUSensor.GYROSCOPE_RAW,
                    dai.IMUSensor.MAGNETOMETER_RAW,
                ],
                IMU_REPORT_RATE,
            )
            imu.setBatchReportThreshold(IMU_BATCH_REPORT_THRESHOLD)
            imu.setMaxBatchReports(IMU_MAX_BATCH_REPORTS)
            imu.out.link(sync.inputs["imu"])

        # create output queue from sync node
        self._sync_queue = sync.out.createOutputQueue()

    def start(self) -> None:
        """Start the pipeline so frames begin flowing."""
        logger.info("Starting OAK-D...")
        self._pipeline.start()

    def stop(self) -> None:
        """Stop the pipeline."""
        self._pipeline.stop()

    def is_running(self) -> bool:
        """Return whether the pipeline is currently running.

        Returns:
            True if the pipeline is running, False otherwise.
        """
        return self._pipeline.isRunning()

    def get_frames(self) -> Metaframe:
        """Block until the next synchronized frame is available.

        Returns:
            A Metaframe from the sync node, timestamped at the
            moment frames were synchronized, with a None value for every
            stream that was not enabled.
        """
        # get synchronized message group from sync node
        message_group = self._sync_queue.get()

        # extract individual frames from the message group
        rgb_frame = None
        if self._enable_rgb:
            rgb_msg = message_group["rgb"]
            rgb_frame = rgb_msg.getCvFrame() if rgb_msg else None

        left_frame = None
        if self._enable_left:
            left_msg = message_group["left"]
            left_frame = left_msg.getCvFrame() if left_msg else None

        right_frame = None
        if self._enable_right:
            right_msg = message_group["right"]
            right_frame = right_msg.getCvFrame() if right_msg else None

        depth_frame = None
        if self._enable_depth:
            depth_msg = self._depth_queue.get()
            depth_frame = depth_msg.getFrame() if depth_msg else None

        imu_data = None
        if self._enable_imu:
            imu_msg = message_group["imu"]
            if imu_msg and len(imu_msg.packets) > 0:
                # Get the latest IMU packet from the batch
                pkt = imu_msg.packets[-1]
                accelerometer = None
                gyroscope = None
                magnetometer = None

                if pkt.acceleroMeter:
                    accelerometer = Vector3(
                        x=pkt.acceleroMeter.x,
                        y=pkt.acceleroMeter.y,
                        z=pkt.acceleroMeter.z,
                    )
                if pkt.gyroscope:
                    gyroscope = Vector3(
                        x=pkt.gyroscope.x,
                        y=pkt.gyroscope.y,
                        z=pkt.gyroscope.z,
                    )
                if pkt.magneticField:
                    magnetometer = Vector3(
                        x=pkt.magneticField.x,
                        y=pkt.magneticField.y,
                        z=pkt.magneticField.z,
                    )

                imu_data = IMUData(
                    accelerometer=accelerometer,
                    gyroscope=gyroscope,
                    magnetometer=magnetometer,
                )

        return Metaframe(
            timestamp=datetime.fromtimestamp(
                message_group.getTimestamp().total_seconds(), tz=UTC
            ),
            rgb=rgb_frame,
            left=left_frame,
            right=right_frame,
            depth=depth_frame,
            imu=imu_data,
        )
