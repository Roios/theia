"""Stream and display the camera data."""

import logging

import cv2

from common.generic_camera import Camera

logger = logging.getLogger(__name__)


def display_camera_streams(
    camera: Camera,
    display_rgb: bool = True,
    display_left: bool = True,
    display_right: bool = True,
    display_depth: bool = True,
) -> None:
    """Stream whichever views the given Camera implementation provides.

    Args:
        camera: Any Camera implementation to stream from.
        display_rgb: Whether to display the RGB view.
        display_left: Whether to display the left view.
        display_right: Whether to display the right view.
        display_depth: Whether to display the depth view.
    """
    with camera:
        camera.start()

        logger.info("Streaming.")
        logger.info("Press Q or ESC to quit.")

        while camera.is_running():
            frames = camera.get_frames()

            streams_count = 0
            if display_rgb:
                if frames.rgb is not None:
                    streams_count += 1
                    cv2.imshow("RGB", frames.rgb)
                else:
                    logger.warning("RGB frame is None.")

            if display_left:
                if frames.left is not None:
                    streams_count += 1
                    cv2.imshow("Left", frames.left)
                else:
                    logger.warning("Left frame is None.")

            if display_right:
                if frames.right is not None:
                    streams_count += 1
                    cv2.imshow("Right", frames.right)
                else:
                    logger.warning("Right frame is None.")

            if display_depth:
                if frames.depth is not None:
                    streams_count += 1
                    # depth is raw distance data
                    # normalizing  to 0-255 for display
                    depth_vis = cv2.normalize(
                        frames.depth,
                        None,
                        0,
                        255,
                        cv2.NORM_MINMAX,
                        dtype=cv2.CV_8U,
                    )

                    depth_color = cv2.applyColorMap(
                        depth_vis,
                        cv2.COLORMAP_JET,
                    )

                    cv2.imshow("Stereo depth", depth_color)
                else:
                    logger.warning("Depth frame is None.")

            if streams_count == 0:
                logger.warning("No streams to display. Exiting.")
                break

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q") or key == 27:
                break

        camera.stop()

    cv2.destroyAllWindows()
