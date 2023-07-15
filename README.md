# hegre downloader
Downloader for `hegre.com`, written in python. This tool can only download videos if you provide account details with a valid subsription.

## Setup
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

## Usage
This tool does not have a CLI interface yet. It will start to download all movies into the folder `./downloads`, with subfolders for each year.
```sh
# Linux
python3 hegre-downloader/downloader.py

# Windows / macOS
python hegre-downloader/downloader.py
```

## Development
Complete the setup steps above. After that, install development dependencies and the pre-commit hook for the formatter:
```sh
pip install -r requirements-dev.txt
pre-commit install
```

## TODOS
- CLI interface:
    - no arguments: download all movies
    - link to model: download all movies of model
    - link to movie: download this single movie
    - `-r` preferred resolution (e.g. 1920, 2160)
    - `-d` destination folder
    - `-r` number of retries
    - `--no-thumb` do not download thumbnail
    - `--no-meta` do not create metadata file
- Update progress in "Fetching movies" (e.g. `250/1025`)
- Parallel downloads ([example](https://github.com/Textualize/rich/blob/master/examples/downloader.py))
- Custom filenames with format strings
- Support for gallery downloads
