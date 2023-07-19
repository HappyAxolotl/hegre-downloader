# hegre downloader
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Downloader for `hegre.com`, written in python. This tool can only download videos if you provide account details with a valid subsription.

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

## 📖 Usage
This tool does not have a CLI interface yet. It will start to download all movies into the folder `./downloads`, with subfolders for each year.
```sh
# Linux
python3 hegre-downloader/downloader.py

# Windows / macOS
python hegre-downloader/downloader.py
```

## 👷 Development
Complete the setup steps above. After that, install development dependencies and the pre-commit hook for the formatter:
```sh
pip install -r requirements-dev.txt
pre-commit install
```

## 💡 Ideas
- Movies: parse download URLs wirh urllib for a safer removal of parameters
- Parallel downloads ([example](https://github.com/Textualize/rich/blob/master/examples/downloader.py))
- Custom filenames with format strings
- Show filesize while downloading
- Support for gallery downloads
- Subtitles (only on sexed videos?)
- Save downloaded scene codes (similar to the [`--download-archive` flag from youtube-dlp](https://github.com/yt-dlp/yt-dlp#video-selection))
- Load configration via dynaconf (what should be a parameter, what should be loaded via file (only secrets?))
- Documentation
- Unit testing
