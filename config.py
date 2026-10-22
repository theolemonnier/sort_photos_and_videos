import re
from pathlib import Path

# folder selection (inputs, and photos / videos output directories )
INITIALDIR = str(Path.home())

MANUAL_SELECTION = False

ORIGIN = Path("/path/to/source")

PHOTOS_DESTINATION = Path("/path/to/photos")

VIDEOS_DESTINATION = Path("/path/to/videos")


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
    ".heic",
    ".heif",
    ".avif",
    ".dng",
    ".raw",
    ".cr2",
    ".cr3",
    ".nef",
    ".arw",
    ".orf",
    ".rw2",
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".wmv",
    ".flv",
    ".webm",
    ".m4v",
    ".mpg",
    ".mpeg",
    ".3gp",
    ".mts",
    ".m2ts",
    ".mxf",
    ".vob",
}

MONTHS_FR = [
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]

DATE_PREFIX = re.compile(
    r"^(\d{4}-\d{2}-\d{2})_"
)  # useful to check if filename starts with YYYY-MM-DD_
