import os

from PyQt6.QtGui import QIcon, QPixmap

from ..constants.paths.icons import INTERNAL_ICONS_FOLDER


def get_image_file(icon_filename: str) -> str:
    """Get the full filepath to an icon in the application's internal icon folder."""
    return os.path.join(INTERNAL_ICONS_FOLDER, icon_filename)


def make_icon(icon_filename: str) -> QIcon:
    """
    Create a QIcon from an icon file in the application's internal icons folder.

    Parameters
    ----------
    icon_filename
        The icon filename inside the icons folder WITH the file extension.

    Returns
    -------
    A `QIcon` of the icon file.
    """
    return QIcon(get_image_file(icon_filename))


def make_pixmap(image_filename: str) -> QPixmap:
    """
    Create a QPixmap from an image file in the application's internal icons folder.

    Parameters
    ----------
    image_filename
        The image filename inside the icons folder WITH the file extension.
    Returns
    -------
    A `QPixmap` of the image file.
    """
    return QPixmap(get_image_file(image_filename))
