"""Application entry point for Theia CLI commands."""

import logging

import click

from hardware.oakd.camera import OakDCamera
from hardware.webcam.camera import WebcamCamera
from theia.display_streams import display_camera_streams

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@click.command("display-streams")
@click.option(
    "--camera",
    "camera_type",
    type=click.Choice(["oakd", "webcam"]),
    default="oakd",
    show_default=True,
    help="Camera hardware to use.",
)
@click.option(
    "--webcam-index",
    type=int,
    default=0,
    show_default=True,
    help="OpenCV device index when using a webcam.",
)
@click.option(
    "--no-rgb",
    is_flag=True,
    default=False,
    help="Disable RGB stream",
)
@click.option(
    "--no-left",
    is_flag=True,
    default=False,
    help="Disable left stereo stream",
)
@click.option(
    "--no-right",
    is_flag=True,
    default=False,
    help="Disable right stereo stream",
)
@click.option(
    "--no-depth",
    is_flag=True,
    default=False,
    help="Disable depth stream",
)
def display_streams(
    camera_type: str,
    webcam_index: int,
    no_rgb: bool,
    no_left: bool,
    no_right: bool,
    no_depth: bool,
) -> None:
    """Display camera streams in a GUI window.

    Args:
        camera_type: Camera hardware to use.
        webcam_index: OpenCV device index when using a webcam.
        no_rgb: If True, disable the RGB stream.
        no_left: If True, disable the left stereo stream.
        no_right: If True, disable the right stereo stream.
        no_depth: If True, disable the depth stream.
    """
    if camera_type == "webcam":
        camera = WebcamCamera(device_index=webcam_index)
        display_left = False
        display_right = False
        display_depth = False
    else:
        camera = OakDCamera()
        display_left = not no_left
        display_right = not no_right
        display_depth = not no_depth

    display_camera_streams(
        camera=camera,
        display_rgb=not no_rgb,
        display_left=display_left,
        display_right=display_right,
        display_depth=display_depth,
    )
