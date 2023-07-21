# hegre downloader
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Downloader and metadata extractor for `hegre.com`, written in python. This tool can only download videos if you provide account details with a valid subsription.

**Disclaimer**: This is my first real python project, so there's probably a lot of room for improvements. Also it is mainly developed for my personal purpose of downloading videos, hence the (current) lack of a gallery download option.

## 🪛 Setup
- Make sure that you have git and python 3.11 installed
- Clone this repository
- Create a copy of `.env.dist` and name it `.env`
- Fill in your hegre.com account credentials in `.env`
- Optional: Create a virtual environment:
```sh
# setup venv
python3 -m venv --upgrade-deps .venv

# switch to venv 
# Linux
source .venv/bin/activate

# Windows (powershell)
.venv\Scripts\Activate.ps1
```
- Install requirements:
```sh
pip install -r requirements.txt
```

## 🧑‍💻 Usage as CLI tool
```
usage: downloader [-h] -d PATH [-r HEIGHT_IN_PX] [--sort SORT] [--retries RETRIES] [--no-thumb] [--no-meta] [--no-subtitles] [--no-download] [--subtitles SUBTITLES] [URL ...]

Downloader for hegre.com

You can specify one or more URLs that will be downloaded. If you do not provide a URL, it will download all movies. The following URLs are supported:
- All movies:
    https://www.hegre.com/movies
- Single movie of type film:
    https://www.hegre.com/films/title-of-the-film
    https://www.hegre.com/films/69
- Single movie of type massage:
    https://www.hegre.com/massage/title-of-the-massage-film
    https://www.hegre.com/massage/69
- Single movie of type sexed:
    https://www.hegre.com/sexed/title-of-the-sexed-film
    https://www.hegre.com/sexed/69

positional arguments:
  URL                   Hegre URL(s) to download. If none is specified, defaults to https://www.hegre.com/movies

options:
  -h, --help            show this help message and exit
  -d PATH               Destination folder
  -r HEIGHT_IN_PX       Preferred resolution for movies (height in pixels, e.g. 480, 2160). If this argument is omitted or the requested resolution is not available, the highest available resolution is selcetd.
  --sort SORT           Sorting when downloading all movies/galleries. Defaults to 'most_recent'. Valid values are 'most_recent', 'most_viewed', 'top_rated'.
  --retries RETRIES     Number of retries for failed downloads. Defaults to 2. Set to 0 to disable retries.
  --no-thumb            Do not download thumbnails
  --no-meta             Do not create metadata file
  --no-subtitles        Do not download subtitles
  --no-download         Do not download the actual file (movie or gallery)
  --subtitles SUBTITLES
                        Language(s) of subtitles that should be downloaded. Will only download available languages. Defaults to 'english'. Multiple langauges must separated by comma (e.g. 'english,german,japanese').
```

## 📖 Usage as library
*coming soon*

## 👷 Development
Complete the setup steps above. After that, install development dependencies and the pre-commit hook for the formatter:
```sh
pip install -r requirements-dev.txt
pre-commit install
```

## 💡 Ideas
- Download screengrabs (ZIP file includes poster and board image)
- Parallel downloads ([example](https://github.com/Textualize/rich/blob/master/examples/downloader.py))
- Show filesize while downloading
- Save downloaded scene codes (similar to the [`--download-archive` flag from youtube-dlp](https://github.com/yt-dlp/yt-dlp#video-selection))
- Custom filenames with format strings
- Support for gallery downloads
- More robustness on errors (e.g. HTTP 404)
- Exit gracefully on SIGINT (`Ctrl+C`)
- Load configration via dynaconf (what should be a parameter, what should be loaded via file (only secrets?))
- Include trailer URLs in metadata
- Documentation
- Unit testing
