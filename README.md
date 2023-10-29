# hegre downloader
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Downloader and metadata extractor for `hegre.com`, written in python. This tool can only download content if you provide account details with a valid subsription.

**Disclaimer**: This is my first real python project, so there's probably a lot of room for improvements. Also it is mainly developed for my personal purpose of downloading videos.

## 🪛 Setup
- Make sure that you have git and python >= 3.10 installed
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
usage: downloader [-h] -d PATH [-r HEIGHT_IN_PX] [-p NUM_OF_TASKS] [--sort SORT] [--retries RETRIES] [--no-thumb] [--no-meta] [--no-subtitles] [--no-download] [--subtitles SUBTITLES] [--screengrabs] [--trailer] URL [URL ...]

Downloader and metadata extractor for hegre.com

You can specify one or more URLs that will be downloaded. The following URLs are supported:
- Single movie:
    https://www.hegre.com/films/title-of-the-film
    https://www.hegre.com/massage/title-of-the-massage-film
    https://www.hegre.com/sexed/title-of-the-sexed-film
- All movies:
    https://www.hegre.com/movies
- Single gallery:
    https://www.hegre.com/photos/title-of-the-gallery
- All galleries:
    https://www.hegre.com/photos
- All movies and galleries of a model:
    https://www.hegre.com/models/name-of-model

positional arguments:
  URL                   Hegre URL(s) to download

options:
  -h, --help            show this help message and exit
  -d PATH               Destination folder
  -r HEIGHT_IN_PX       Preferred resolution for movies (height in pixels, e.g. 480, 2160). If this argument is omitted or the requested resolution is not available, the highest available resolution is selcetd.
  -p NUM_OF_TASKS       Number of parallel tasks. Defaults to 1.
  --sort SORT           Sorting when downloading all movies/galleries. Defaults to 'most_recent'. Valid values are 'most_recent', 'most_viewed', 'top_rated'.
  --retries RETRIES     Number of retries for failed downloads. Defaults to 2. Set to 0 to disable retries.
  --no-thumb            Do not download thumbnails
  --no-meta             Do not create metadata file
  --no-subtitles        Do not download subtitles
  --no-download         Do not download the actual file (movie or gallery)
  --subtitles SUBTITLES
                        Language(s) of subtitles that should be downloaded. Will only download available languages. Defaults to 'english'. Multiple langauges must separated by comma (e.g. 'english,german,japanese').
  --screengrabs         Download screengrabs
  --trailer             Download trailer
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
- Rewrite download status display in downloader:
  - Separate progress bar for each task i.e. show progress of subtasks such as trailer, screengrabs and subtitle download
  - Show filesize while downloading
- Custom filenames with format strings
- Separation between resolution of galleries (`px`) and movies (`p`) (`-r` flag)
- Subtitle files should match the schema `{movie_name}.{language_code}.ext`
- More robustness on errors (e.g. HTTP 404)
- Exit gracefully on SIGINT (`Ctrl+C`)
- Load configration via dynaconf (what should be a parameter, what should be loaded via file (only secrets?))
- Logout (end session)
- Documentation
- Unit testing
