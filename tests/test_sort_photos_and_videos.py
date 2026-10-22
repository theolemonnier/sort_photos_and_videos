from pathlib import Path

import pytest

import sort_photos_and_videos


def test_get_file_type(tmp_path):
    file = sort_photos_and_videos.MediaFile(str(tmp_path), "2026-10-22_photo.jpg")
    assert file.type == "image"

    file = sort_photos_and_videos.MediaFile(str(tmp_path), "2026-10-22_video.mp4")
    assert file.type == "video"

    file = sort_photos_and_videos.MediaFile(str(tmp_path), "document.txt")
    assert file.type == "unsuported"


def test_is_valid_date(tmp_path):
    file = sort_photos_and_videos.MediaFile(str(tmp_path), "2026-10-22_photo.jpg")

    assert file.is_valid_date("2026-10-22") is True
    assert file.is_valid_date("2026-13-40") is False
    assert file.is_valid_date("invalid") is False


def test_get_destination(tmp_path):
    photos = tmp_path / "photos"
    videos = tmp_path / "videos"

    file = sort_photos_and_videos.MediaFile(
        str(tmp_path),
        "2026-10-22_photo.jpg",
        photos=photos,
        videos=videos,
    )

    assert file.destination is not None
    assert str(photos) in file.destination
    assert "2026" in file.destination
    assert "2026-10-22_photo.jpg" in file.destination


def test_copy_without_overwriting(tmp_path):
    source = tmp_path / "2026-10-22_photo.jpg"
    source.write_text("test image")  # source file must exist fot shutil.copy2() to work

    file = sort_photos_and_videos.MediaFile(
        str(tmp_path),
        source.name,
        photos=tmp_path / "photos",
        videos=tmp_path / "videos",
    )

    assert file.copy_without_overwriting() == "copied"
    assert Path(file.destination).exists()

    # The second copy must not overwrite the existing file
    assert file.copy_without_overwriting() == "already_exist"


def test_validate_folder(tmp_path):
    sort_photos_and_videos.validate_folder(tmp_path, "test_folder")

    with pytest.raises(SystemExit):
        sort_photos_and_videos.validate_folder(None, "test_folder")

    with pytest.raises(SystemExit):
        sort_photos_and_videos.validate_folder(tmp_path / "missing", "test_folder")


def test_stats():
    stats = sort_photos_and_videos.Stats()

    class FakeFile:
        type = "image"
        date = "2026-10-22"

    stats.record(FakeFile(), "copied")

    assert stats.total_files == 1
    assert stats.num_photos == 1
    assert stats.photos_sorted == 1
