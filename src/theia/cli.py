"""Application entry point for Theia CLI commands."""

import logging

import click

from hardware.oakd.camera import OakDCamera
from theia.display_streams import display_camera_streams

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@click.command("display-streams")
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
    no_rgb: bool, no_left: bool, no_right: bool, no_depth: bool
) -> None:
    """Display camera streams in a GUI window.

    Args:
        no_rgb: If True, disable the RGB stream.
        no_left: If True, disable the left stereo stream.
        no_right: If True, disable the right stereo stream.
        no_depth: If True, disable the depth stream.
    """
    camera = OakDCamera()
    display_camera_streams(
        camera=camera,
        display_rgb=not no_rgb,
        display_left=not no_left,
        display_right=not no_right,
        display_depth=not no_depth,
    )
