from datetime import date

from bs4 import BeautifulSoup
import pytest

from model.movie import HegreMovie
from model.gallery import HegreGallery
from model.object_type import ObjectType
from exceptions import HegreError

# Minimal markup that mirrors the structure of the current (2026) hegre.com pages
FILM_PAGE = """
<div class="record-toolbar">
  <a class="record-model" href="/models/jane-doe" title="Jane Doe"></a>
  <div class="title"><h1 class="translated-text">Some Film</h1></div>
</div>
<div class="video-player-wrapper" style="background-image: url('https://pp.hegre.com/films/some-film/some-film-board-image-3840x.jpg?v=1')">
  <div class="video-inner">
    <script>
      $(function() {
        new VideoPlayer($('#video-player'), {"key":"x","resolutions":[
          {"label":"4K","sources":{"default":[{"mp4":"https://c.hegre.com/films/some-film/some-film-2160p.mp4?v=1"},{"flash":"https://c.hegre.com/x.mp4"}]},"type":2160},
          {"label":"1080p","sources":{"default":[{"mp4":"https://c.hegre.com/films/some-film/some-film-1080p.mp4"}]},"type":1080}
        ],"clip":{"subtitles":null}});
      });
    </script>
  </div>
</div>
<div class="video-stills"><a href="https://cc.hegre.com/films/some-film/some-film.zip">stills</a></div>
<div class="comments-wrapper" data-id="1162"></div>
<div class="massage-copy translated-text"><p>A description.</p></div>
<ul class="format-details">
  <li><span>Runtime:</span><strong>13:08 Minutes</strong></li>
  <li><span>Format:</span><ul class="format-list"><li><strong>4K Ultra HD 2160p (1.3 GB)</strong></li></ul></li>
</ul>
<div class="approved-tags"><a class="tag">brunette</a><a class="tag">water</a></div>
<div class="trailer"><a href="https://public.hegre.com/films/some-film/some-film-trailer-2160p.mp4?d=attachment&amp;v=1"><strong>4K Ultra HD 2160p</strong></a></div>
<div class="trailer"><a href="https://public.hegre.com/films/some-film/some-film-trailer-1080p.mp4"><strong>Full HD 1080p</strong></a></div>
"""

GALLERY_PAGE = """
<a class="record-model" href="/models/jane-doe" title="Jane Doe"></a>
<div class="title"><h1 class="translated-text">Some Gallery</h1></div>
<div class="comments-wrapper" data-id="6702"></div>
<div class="date">May 1, 2024</div>
<div class="approved-tags"><a class="tag">water</a></div>
<div class="gallery-zips">
  <a class="members-only" href="https://cc.hegre.com/galleries/some-gallery/zips/some-gallery-14000px.zip?v=1">14000px</a>
  <a class="members-only" href="https://cc.hegre.com/galleries/some-gallery/zips/some-gallery-640px.zip">640px</a>
</div>
<div class="record-content"><div class="non-members" style="background-image: url(https://pp.hegre.com/galleries/some-gallery/some-gallery-board-image-3840x.jpg)"></div></div>
"""


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def test_film_page_without_date_and_subtitles():
    """Films are parsed although the page has no date and the subtitles are null"""
    movie = HegreMovie.from_film_page(
        "https://www.hegre.com/films/some-film", _soup(FILM_PAGE)
    )

    assert movie.type == ObjectType.FILM
    assert movie.title == "Some Film"
    assert movie.code == 1162
    assert movie.date is None
    assert movie.duration == 13 * 60 + 8
    assert movie.description == "A description."
    assert movie.subtitles == {}
    assert movie.tags == ["Brunette", "Water"]
    assert [m.name for m in movie.models] == ["Jane Doe"]
    assert (
        movie.cover_url
        == "https://pp.hegre.com/films/some-film/some-film-board-image-3840x.jpg"
    )
    assert movie.screengrabs_url == "https://cc.hegre.com/films/some-film/some-film.zip"
    assert movie.downloads == {
        2160: "https://c.hegre.com/films/some-film/some-film-2160p.mp4",
        1080: "https://c.hegre.com/films/some-film/some-film-1080p.mp4",
    }
    assert movie.trailers == {
        2160: "https://public.hegre.com/films/some-film/some-film-trailer-2160p.mp4",
        1080: "https://public.hegre.com/films/some-film/some-film-trailer-1080p.mp4",
    }
    assert not movie.has_only_trailers()


def test_film_page_logged_out_has_only_trailers():
    """Without a subscription the video player only contains trailer URLs"""
    page = FILM_PAGE.replace("some-film-2160p.mp4", "some-film-trailer-2160p.mp4")
    page = page.replace("some-film-1080p.mp4", "some-film-trailer-1080p.mp4")

    movie = HegreMovie.from_film_page(
        "https://www.hegre.com/films/some-film", _soup(page)
    )

    assert movie.has_only_trailers()


def test_film_page_with_changed_layout_raises_hegre_error():
    """A page without the expected elements raises a HegreError instead of crashing"""
    with pytest.raises(HegreError):
        HegreMovie.from_film_page(
            "https://www.hegre.com/films/some-film", _soup("<html></html>")
        )


def test_gallery_page():
    """Galleries are parsed, including the date if the page still shows it"""
    gallery = HegreGallery.from_gallery_page(
        "https://www.hegre.com/photos/some-gallery", _soup(GALLERY_PAGE)
    )

    assert gallery.title == "Some Gallery"
    assert gallery.code == 6702
    assert gallery.date == date(2024, 5, 1)
    assert gallery.tags == ["Water"]
    assert gallery.downloads == {
        14000: "https://cc.hegre.com/galleries/some-gallery/zips/some-gallery-14000px.zip",
        640: "https://cc.hegre.com/galleries/some-gallery/zips/some-gallery-640px.zip",
    }
    assert (
        gallery.cover_url
        == "https://pp.hegre.com/galleries/some-gallery/some-gallery-board-image-3840x.jpg"
    )
