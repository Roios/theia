"""Hardware-agnostic camera abstraction."""

from abc import ABC, abstractmethod
from types import TracebackType

from common.data_models import Metaframe


class Camera(ABC):
    """Hardware-agnostic interface for a stereo depth camera.

    Any camera backend (e.g. OAK-D) plugs into the rest of the project by
    implementing this interface, so swapping hardware only means writing a
    new implementation, not touching the application code.

    Implementations are expected to be used as a context manager, e.g.::

        with camera:
            camera.start()
            while camera.is_running():
                frames = camera.get_frames()
            camera.stop()

    ``__exit__`` must release every hardware resource acquired by
    ``__enter__``/``start``, even when an exception was raised anywhere
    inside the ``with`` block.
    """

    @abstractmethod
    def __enter__(self) -> "Camera":
        """Acquire the camera and prepare it to start streaming."""
        raise NotImplementedError

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Release the camera, regardless of whether an error occurred."""
        raise NotImplementedError

    @abstractmethod
    def start(self) -> None:
        """Start streaming frames from the camera."""
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """Stop streaming frames from the camera."""
        raise NotImplementedError

    @abstractmethod
    def is_running(self) -> bool:
        """Return whether the camera is currently streaming."""
        raise NotImplementedError

    @abstractmethod
    def get_frames(self) -> Metaframe:
        """Block until the next synchronized set of frames is available."""
        raise NotImplementedError
