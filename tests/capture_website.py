from hegre_downloader.hegre import Hegre

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="capture_website",
        description="Capture a website in a machine-readable format, including metadata on how the website was fetched",
    )
    parser.add_argument(
        "urls",
        metavar="URL",
        nargs="+",
        help="Hegre URL(s) to download",
        action="store",
    )
    hegre = Hegre()
