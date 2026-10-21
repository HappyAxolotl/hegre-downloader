from helper import duration_to_seconds, convert_size, strip_query, extract_css_url
import pytest


def test_duration_to_seconds_hhmmss():
    """Test duration to seconds conversion for the format hh:mm:ss"""
    duration_string = "69:42:23"
    expected_numer_of_seconds = 250943

    result_in_seconds = duration_to_seconds(duration_string)

    assert result_in_seconds == expected_numer_of_seconds


def test_duration_to_seconds_mmss():
    """Test duration to seconds conversion for the format mm:ss"""
    duration_string = "42:23"
    expected_numer_of_seconds = 2543

    result_in_seconds = duration_to_seconds(duration_string)

    assert result_in_seconds == expected_numer_of_seconds


def test_duration_to_seconds_ss():
    """Test duration to seconds conversion for the format ss"""
    duration_string = "23"
    expected_numer_of_seconds = 23

    result_in_seconds = duration_to_seconds(duration_string)

    assert result_in_seconds == expected_numer_of_seconds


def test_duration_to_seconds_invalid_str():
    """Test duration to seconds conversion failure for an invalid input string"""
    duration_string = "foobar"

    with pytest.raises(ValueError):
        duration_to_seconds(duration_string)


def test_duration_to_seconds_hhmmss_custom_delimiter():
    """Test duration to seconds conversion for the format hh:mm:ss with a custom delimiter"""
    duration_string = "69-42-23"
    expected_numer_of_seconds = 250943

    result_in_seconds = duration_to_seconds(duration_string, delimiter="-")

    assert result_in_seconds == expected_numer_of_seconds


def test_convert_size():
    """Test conversion from byte to a human readable string"""
    bytes = 42
    expected_b_string = f"42.0 B"

    kbytes = 4200
    expected_kb_string = f"4.1 KB"

    mbytes = 4200000
    expected_mb_string = f"4.01 MB"

    gbytes = 4200000000
    expected_gb_string = f"3.91 GB"

    tbytes = 4200000000000
    expected_tb_string = f"3.82 TB"

    assert convert_size(bytes) == expected_b_string
    assert convert_size(kbytes) == expected_kb_string, "Byte to KiB"
    assert convert_size(mbytes) == expected_mb_string, "Byte to MiB"
    assert convert_size(gbytes) == expected_gb_string, "Byte to GiB"
    assert convert_size(tbytes) == expected_tb_string, "Byte to TiB"


def test_strip_query():
    """Test removal of URL parameters, also for URLs that have none"""
    assert (
        strip_query("https://hegre.tld/a/file.mp4?v=1&d=x")
        == "https://hegre.tld/a/file.mp4"
    )
    assert strip_query("https://hegre.tld/a/file.zip") == "https://hegre.tld/a/file.zip"


def test_extract_css_url():
    """Test extraction of URLs from quoted and unquoted CSS url() expressions"""
    expected = "https://hegre.tld/image.jpg"

    assert (
        extract_css_url("background-image: url('https://hegre.tld/image.jpg?v=1')")
        == expected
    )
    assert (
        extract_css_url("background-image: url(https://hegre.tld/image.jpg)")
        == expected
    )
    assert extract_css_url("color: red") is None
    assert extract_css_url(None) is None
