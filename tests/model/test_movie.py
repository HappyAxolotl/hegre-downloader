from hegre_downloader.model.movie import HegreMovie

import json
import pytest

RES_480 = 480
HIGHEST_RES = 2160
MOCK_TRAILER_RESOLUTIONS = {
    240: "https://hegre.tld/dl/trailer-240p.mp4",
    360: "https://hegre.tld/dl/trailer-360p.mp4",
    RES_480: "https://hegre.tld/dl/trailer-480p.mp4",
    720: "https://hegre.tld/dl/trailer-720p.mp4",
    1080: "https://hegre.tld/dl/trailer-1080p.mp4",
    HIGHEST_RES: "https://hegre.tld/dl/trailer-2160p.mp4",
}

ENGLISH_SUB_URL = "https://hegre.tld/video-en.vtt"
FRENCH_SUB_URL = "https://hegre.tld/video-fr.vtt"
JAPANESE_SUB_URL = "https://hegre.tld/video-jp.vtt"
MOCK_SUBTITLES = {
    "english": ENGLISH_SUB_URL,
    "french": FRENCH_SUB_URL,
    "japanese": JAPANESE_SUB_URL,
}

VIDEO_PLAYER_METADATA_WITH_LOGIN = json.dumps(
    {
        "key": "$469394428291165",
        "swf": "/flowplayer/flowplayer.swf",
        "embed": False,
        "ratio": 0.5625,
        "resolutions": [
            {
                "label": "4K",
                "sources": {
                    "default": [
                        {
                            "mp4": "https://c.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-2160p.mp4?v=1692049636"
                        },
                        {
                            "flash": "https://c.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-2160p.mp4?v=1692049636"
                        },
                    ],
                    "voiceover": None,
                },
                "type": 2160,
            },
            {
                "label": "1080p",
                "sources": {
                    "default": [
                        {
                            "mp4": "https://c.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-1080p.mp4?v=1692049636"
                        },
                        {
                            "flash": "https://c.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-1080p.mp4?v=1692049636"
                        },
                    ],
                    "voiceover": None,
                },
                "type": 1080,
            },
            {
                "label": "720p",
                "sources": {
                    "default": [
                        {
                            "mp4": "https://c.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-720p.mp4?v=1692049636"
                        },
                        {
                            "flash": "https://c.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-720p.mp4?v=1692049636"
                        },
                    ],
                    "voiceover": None,
                },
                "type": 720,
            },
            {
                "label": "480p",
                "sources": {
                    "default": [
                        {
                            "mp4": "https://c.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-480p.mp4?v=1692049636"
                        },
                        {
                            "flash": "https://c.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-480p.mp4?v=1692049636"
                        },
                    ],
                    "voiceover": None,
                },
                "type": 480,
            },
        ],
        "keyboard": True,
        "autoplay": False,
        "loop": False,
        "preload": "auto",
        "time": 0,
        "native_fullscreen": True,
        "no_fullscreen_control": False,
        "share": False,
        "clip": {
            "subtitles": [
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-en.vtt?v=1692028729",
                    "label": "English",
                    "default": True,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-de.vtt?v=1692028729",
                    "label": "German",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-es.vtt?v=1692028729",
                    "label": "Spanish",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-fr.vtt?v=1692028729",
                    "label": "French",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-jp.vtt?v=1692028729",
                    "label": "Japanese",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-pt.vtt?v=1692028729",
                    "label": "Portuguese",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-it.vtt?v=1692028729",
                    "label": "Italian",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-nl.vtt?v=1692028729",
                    "label": "Dutch",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-pl.vtt?v=1692028729",
                    "label": "Polish",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-ko.vtt?v=1692028729",
                    "label": "Korean",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-fi.vtt?v=1692028729",
                    "label": "Finnish",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-sv.vtt?v=1692028729",
                    "label": "Swedish",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-no.vtt?v=1692028729",
                    "label": "Norwegian",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-iw.vtt?v=1692028729",
                    "label": "Hebrew",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-lv.vtt?v=1692028729",
                    "label": "Latvian",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-lt.vtt?v=1692028729",
                    "label": "Lithuanian",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-ar.vtt?v=1692028729",
                    "label": "Arabic",
                    "default": False,
                },
                {
                    "src": "https://p.hegre.com/films/lorem-ipsum-dolor-sit-amet/lorem-ipsum-dolor-sit-amet-zh.vtt?v=1692028729",
                    "label": "Chinese",
                    "default": False,
                },
            ]
        },
    }
)

# raw string that is embedded into the HTML (use selector ".video-inner > script")
VIDEO_PLAYER_RAW_SCRIPT_WITH_LOGIN = (
    "`$(function() { new VideoPlayer($('#video-player-films-lorem-ipsum-dolor-sit-amet'), "
    + VIDEO_PLAYER_METADATA_WITH_LOGIN
    + ");`"
)


def test_extract_downloads_subtitles_from_video_player_with_login():
    """Tests the extraction of download URLs and subtitle URLs from a movie page when the user is logged in"""
    movie = HegreMovie(url="")
    movie._extract_downloads_subtitles_from_video_player(
        VIDEO_PLAYER_RAW_SCRIPT_WITH_LOGIN
    )

    assert movie.downloads.keys() == {480, 720, 1080, 2160}
    assert len(movie.subtitles) == 18, "Subtitles are availabe in 18 languages"


def test_get_subtitle_download_urls():
    """Test retreival of download URLs for subtitles"""
    movie = HegreMovie(url="")
    movie.subtitles = MOCK_SUBTITLES

    urls = movie.get_subtitle_download_urls(["english", "japanese"])
    assert urls == [ENGLISH_SUB_URL, JAPANESE_SUB_URL]
    assert FRENCH_SUB_URL not in urls


def test_get_subtitle_download_urls_non_exsting_lang():
    """Test that non existing/invalid languages are ignored"""
    movie = HegreMovie(url="")
    movie.subtitles = MOCK_SUBTITLES

    urls = movie.get_subtitle_download_urls(["foobar", "german"])
    assert len(urls) == 0


def test_get_highest_res_trailer_download_url():
    """Test retreival of download URL for the highest available trailer resolution"""
    movie = HegreMovie(url="")
    movie.trailers = MOCK_TRAILER_RESOLUTIONS

    assert movie.get_highest_res_trailer_download_url() == (
        HIGHEST_RES,
        MOCK_TRAILER_RESOLUTIONS[HIGHEST_RES],
    )


def test_get_trailer_download_url_for_res_existing():
    """Test retreival of download URL for a specific trailer resolution that is available"""
    movie = HegreMovie(url="")
    movie.trailers = MOCK_TRAILER_RESOLUTIONS

    assert movie.get_trailer_download_url_for_res(RES_480) == (
        RES_480,
        MOCK_TRAILER_RESOLUTIONS[RES_480],
    )


def test_get_trailer_download_url_for_res_non_existing():
    """Test failure of retreival of download URL for a specific trailer resolution that is not available"""
    movie = HegreMovie(url="")
    movie.trailers = MOCK_TRAILER_RESOLUTIONS

    with pytest.raises(KeyError):
        movie.get_trailer_download_url_for_res(144)


def test_get_trailer_download_url_for_res_no_res():
    """Test retreival of download URL defaults to highest available trailer resolution if no resolution is specified"""
    movie = HegreMovie(url="")
    movie.trailers = MOCK_TRAILER_RESOLUTIONS

    assert movie.get_trailer_download_url_for_res() == (
        HIGHEST_RES,
        MOCK_TRAILER_RESOLUTIONS[HIGHEST_RES],
    )
