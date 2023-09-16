from hegre_downloader.model.hegre_object import HegreObject
from hegre_downloader.model.object_type import ObjectType

import pytest

RES_480 = 480
HIGHEST_RES = 2160

MOCK_RESOLUTIONS = {
    240: "https://hegre.tld/dl/video-240p.mp4",
    360: "https://hegre.tld/dl/video-360p.mp4",
    RES_480: "https://hegre.tld/dl/video-480p.mp4",
    720: "https://hegre.tld/dl/video-720p.mp4",
    1080: "https://hegre.tld/dl/video-1080p.mp4",
    HIGHEST_RES: "https://hegre.tld/dl/video-2160p.mp4",
}


def test_archive_id():
    """Tests the creation of archive IDs for HegreObjects"""
    hegre_object = HegreObject(url="", type=ObjectType.FILM)
    hegre_object.code = "1234"

    expected_archive_id = "films 1234"

    assert hegre_object.archive_id() == expected_archive_id


def test_get_highest_res_download_url():
    """Test retreival of download URL for the highest available resolution"""
    hegre_object = HegreObject(url="", type=ObjectType.FILM)
    hegre_object.downloads = MOCK_RESOLUTIONS

    assert hegre_object.get_highest_res_download_url() == (
        HIGHEST_RES,
        MOCK_RESOLUTIONS[HIGHEST_RES],
    )


def test_get_download_url_for_res_existing():
    """Test retreival of download URL for a specific resolution that is available"""
    hegre_object = HegreObject(url="", type=ObjectType.FILM)
    hegre_object.downloads = MOCK_RESOLUTIONS

    assert hegre_object.get_download_url_for_res(RES_480) == (
        RES_480,
        MOCK_RESOLUTIONS[RES_480],
    )


def test_get_download_url_for_res_non_existing():
    """Test failure of retreival of download URL for a specific resolution that is not available"""
    hegre_object = HegreObject(url="", type=ObjectType.FILM)
    hegre_object.downloads = MOCK_RESOLUTIONS

    with pytest.raises(KeyError):
        hegre_object.get_download_url_for_res(144)


def test_get_download_url_for_res_no_res():
    """Test retreival of download URL defaults to highest available resolution if no resolution is specified"""
    hegre_object = HegreObject(url="", type=ObjectType.FILM)
    hegre_object.downloads = MOCK_RESOLUTIONS

    assert hegre_object.get_download_url_for_res() == (
        HIGHEST_RES,
        MOCK_RESOLUTIONS[HIGHEST_RES],
    )
