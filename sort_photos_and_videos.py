import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from tkinter.filedialog import askdirectory

from PIL import Image
from PIL.ExifTags import IFD
from pillow_heif import register_heif_opener

from config import (
    DATE_PREFIX,
    IMAGE_EXTENSIONS,
    INITIALDIR,
    MANUAL_SELECTION,
    MONTHS_FR,
    ORIGIN,
    PHOTOS_DESTINATION,
    VIDEO_EXTENSIONS,
    VIDEOS_DESTINATION,
)

register_heif_opener()


# utils
def select_folder(title: str):
    path = askdirectory(initialdir=INITIALDIR, title=title)
    if path:
        return Path(path)  # convert string to Path
    else:
        return None


def validate_folder(folder: Path, name: str):
    if folder is None:
        raise SystemExit(f"{name} has not been selected.")

    if not folder.is_dir():
        raise SystemExit(f"{name} is not a valid directory.")


def detect_file_name_date_collisions(folder):
    """Detect potential file conflicts before sorting.

    If files from different source subfolders share the same name
    and date, the second file scanned may be skipped during sorting,
    even if the files are different pictures.

    This function helps identify this issue before sorting begins.
    """

    processed_files = set()

    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames[:] = [
            d for d in dirnames if d != "archives"
        ]  # avoid archives from being visited

        for filename in filenames:
            file = MediaFile(dirpath, filename)
            file_key = (file.name, file.date)

            if file_key in processed_files:
                print(
                    f"File name/date conflict detected: '{file.name}' (date: {file.date}). \n"
                    "Files with both the same name and date could be skipped during sorting. \n"
                    "Please rename or remove one of the conflicting files."
                )
                return True

            processed_files.add(file_key)

    return False


class MediaFile:
    def __init__(self, dirpath, filename, **outputs):
        self.name = filename
        self.path = os.path.join(dirpath, filename)
        self.type = self.get_file_type()
        self.date = self.get_file_date()
        self.destination = self.get_destination(**outputs)

    def get_file_type(self):
        """Return file type according to file extension"""
        extension = Path(self.name).suffix
        if (
            extension.lower() in IMAGE_EXTENSIONS
        ):  # .lower(): converts extension to lower case
            file_type = "image"
        elif extension.lower() in VIDEO_EXTENSIONS:
            file_type = "video"
        else:
            file_type = "unsuported"
        return file_type

    def is_valid_date(self, date_string: str):
        """Check whether date_string represents a valid date in YYYY-MM-DD format"""
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def get_image_date(self):
        """Return image date of creation as YYYY-MM-DD, or None"""
        with Image.open(self.path) as img:
            exif = img.getexif()  # objet qui permet d'acceder au métadonnées
            exif_ifd = exif.get_ifd(
                IFD.Exif
            )  # IFD.Exif = répertoire qui contient les infos au format exif
            date_taken = exif_ifd.get(36867)  # DateTimeOriginal

            if date_taken:
                date = date_taken.split()[0].replace(
                    ":", "-"
                )  # retrieve date from DateTime
            else:
                date = None

            return date

    def get_video_date(self):
        """Return video date creation as YYYY-MM-DD, or None"""
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-show_entries",
                "format_tags=creation_time",
                "-of",
                "json",
                str(self.path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        metadata = json.loads(result.stdout)
        date_taken = metadata.get("format", {}).get("tags", {}).get("creation_time")

        if date_taken:
            date = date_taken.split("T")[0]
        else:
            date = None

        return date

    def get_file_date(self):
        """Return file (image or video) creation date, or None"""

        match = DATE_PREFIX.match(self.name)
        if match:
            if self.type == "image" or self.type == "video":
                date = match.group(1)
                if self.is_valid_date(date) == False:
                    date = None
            else:
                date = None

        elif self.type == "image":
            date = self.get_image_date()

        elif self.type == "video":
            date = self.get_video_date()

        else:
            print(f"{self.path}: file type not supported")
            date = None

        return date

    def get_destination(self, **outputs):
        """Return destination path where the file should be copied, based on its type, date and filename"""
        if not outputs:
            return None

        photos_destination = outputs["photos"]
        videos_destination = outputs["videos"]

        if self.type == "image":
            destination_root = photos_destination

        elif self.type == "video":
            destination_root = videos_destination

        else:
            return None

        # destination folder
        if self.date:
            year = self.date.split("-")[0]
            month = self.date.split("-")[1]
            month_index = int(month) - 1
            month_in_french = MONTHS_FR[month_index]
            month_folder = f"{month} - {month_in_french}"
            destination_folder = os.path.join(destination_root, year, month_folder)

        else:
            destination_folder = os.path.join(destination_root, "no_date")

        # destination_filename
        match = DATE_PREFIX.match(self.name)
        if match:
            destination_filename = self.name
        elif self.date:
            destination_filename = f"{self.date}_{self.name}"
        else:
            destination_filename = self.name

        # destination
        destination = os.path.join(destination_folder, destination_filename)

        return destination

    def copy_without_overwriting(self):
        """Copy the file to its destination without overwriting existing files.

        Creates the destination folder if it does not exist. Skips the copy if the
        file type is unsupported or if a file already exists at the destination.

        Returns:
            str: A status indicating the result of the operation:
                'unsupported_file' if the file type is unsupported,
                'already_exist' if a file already exists at the destination,
                'copied' if the file was successfully copied.
        """
        if self.destination == None:
            # print(f"Skipped (file type not supported): {self.path}")
            return "unsupported_file"

        else:
            destination_folder = os.path.dirname(self.destination)
            os.makedirs(destination_folder, exist_ok=True)

            if os.path.exists(self.destination):
                # print(f"Skipped (already exists): {self.destination}")
                return "already_exist"
            else:
                shutil.copy2(self.path, self.destination)
                # print(f"copied: {self.destination}")
                return "copied"


class Stats:
    def __init__(self):
        self.total_files = 0
        self.num_photos = 0
        self.num_videos = 0
        self.num_unsupported_files = 0

        self.photos_sorted = 0
        self.photos_without_date = 0
        self.photos_skipped = 0

        self.videos_sorted = 0
        self.videos_without_date = 0
        self.videos_skipped = 0

        self.errors = 0

    def record(self, file: MediaFile, result):
        """

        Args:
            file (MediaFile): The file that was processed.
            result (str): The outcome of the copy operation ('copied',
            'already_exist', or 'unsupported_file'). Any other value is counted
            as an error.
        """
        self.total_files += 1

        if file.type == "image":
            self.num_photos += 1
            if result == "copied":
                if file.date is None:
                    self.photos_without_date += 1
                else:
                    self.photos_sorted += 1
            else:
                self.photos_skipped += 1

        elif file.type == "video":
            self.num_videos += 1
            if result == "copied":
                if file.date is None:
                    self.videos_without_date += 1
                else:
                    self.videos_sorted += 1
            else:
                self.videos_skipped += 1

        else:
            self.num_unsupported_files += 1

    def display(self):
        """Display a summary of the file sorting operation."""

        total_sorted = self.photos_sorted + self.videos_sorted
        total_without_date = self.photos_without_date + self.videos_without_date
        total_skipped = self.photos_skipped + self.videos_skipped

        print("\n~~~ Summary ~~~")
        print(f"Images: {self.num_photos} total")
        print(f"    Copied by date:      {self.photos_sorted}")
        print(f"    Copied to no_date:   {self.photos_without_date}")
        print(f"    Skipped:             {self.photos_skipped}")

        print(f"\nVideos: {self.num_videos} total")
        print(f"    Copied by date:      {self.videos_sorted}")
        print(f"    Copied to no_date:   {self.videos_without_date}")
        print(f"    Skipped:             {self.videos_skipped}")

        print("-" * 26)
        print(f"Total files processed:   {self.total_files}")
        print(f"Total copied by date:    {total_sorted}")
        print(f"Total copied to no_date: {total_without_date}")
        print(f"Total skipped:           {total_skipped}")
        print(f"Unsupported file types:  {self.num_unsupported_files}")


def main():

    # select and validate folder
    if MANUAL_SELECTION:
        origin = select_folder(title="Select origin folder")
        photos_destination = select_folder(title="Select Photos destination")
        videos_destination = select_folder(title="Select Videos destination")

    else:
        origin = ORIGIN
        photos_destination = PHOTOS_DESTINATION
        videos_destination = VIDEOS_DESTINATION

    validate_folder(origin, "origin")
    validate_folder(photos_destination, "photos_destination")
    validate_folder(videos_destination, "videos_destination")

    if detect_file_name_date_collisions(origin):
        raise SystemExit

    outputs = {"photos": photos_destination, "videos": videos_destination}

    statistics = Stats()

    # goes recursviley through all files in the source folder
    for dirpath, dirnames, filenames in os.walk(origin):
        dirnames[:] = [
            d for d in dirnames if d != "archives"
        ]  # avoid archives from being visited

        for filename in filenames:
            file = MediaFile(dirpath=dirpath, filename=filename, **outputs)

            result = file.copy_without_overwriting()

            statistics.record(file=file, result=result)

    statistics.display()


if __name__ == "__main__":
    main()
