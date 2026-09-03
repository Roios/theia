"""Camera calibration module for OAK-D device."""

import depthai as dai
import numpy as np

from common.data_models import CameraCalibration, CameraIntrinsics

_DEFAULT_RGB_WIDTH = 1920
_DEFAULT_RGB_HEIGHT = 1080
_DEFAULT_MONO_WIDTH = 640
_DEFAULT_MONO_HEIGHT = 400


def get_camera_intrinsics_and_extrinsics() -> CameraCalibration:
    """Get camera intrinsics and extrinsics from the OAK-D device.

    Returns:
        CameraCalibration containing intrinsics and extrinsics for RGB, left, and right cameras.
    """
    with dai.Device() as device:
        calibData = device.readCalibration()

        # rgb
        intrinsic_rgb = np.array(
            calibData.getCameraIntrinsics(
                dai.CameraBoardSocket.CAM_A, _DEFAULT_RGB_WIDTH, _DEFAULT_RGB_HEIGHT
            )
        )
        distortion_rgb = calibData.getDistortionCoefficients(
            dai.CameraBoardSocket.CAM_A
        )

        rgb_calibration = CameraIntrinsics(
            intrinsic=intrinsic_rgb, distortion=distortion_rgb
        )

        # left
        intrinsic_left = np.array(
            calibData.getCameraIntrinsics(
                dai.CameraBoardSocket.CAM_B, _DEFAULT_MONO_WIDTH, _DEFAULT_MONO_HEIGHT
            )
        )
        distortion_left = calibData.getDistortionCoefficients(
            dai.CameraBoardSocket.CAM_B
        )

        # right
        intrinsic_right = np.array(
            calibData.getCameraIntrinsics(
                dai.CameraBoardSocket.CAM_C, _DEFAULT_MONO_WIDTH, _DEFAULT_MONO_HEIGHT
            )
        )
        distortion_right = calibData.getDistortionCoefficients(
            dai.CameraBoardSocket.CAM_C
        )

        # extrinsic between left and right cameras
        extrinsic = np.array(
            calibData.getCameraExtrinsics(
                dai.CameraBoardSocket.CAM_B, dai.CameraBoardSocket.CAM_C
            )
        )

    return CameraCalibration(
        rgb=rgb_calibration,
        left=CameraIntrinsics(intrinsic=intrinsic_left, distortion=distortion_left),
        right=CameraIntrinsics(intrinsic=intrinsic_right, distortion=distortion_right),
        extrinsic_left_to_right=extrinsic,
    )
