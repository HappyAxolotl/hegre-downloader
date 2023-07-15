from dotenv import load_dotenv
import os
import sys

from hegre import Hegre
from exceptions import HegreError

from rich.progress import Progress
from rich.console import Console

load_dotenv()
console = Console()

username = os.environ.get("username")
password = os.environ.get("password")

if not username or not password:
    console.print("[red]Please provide username and password!")
    sys.exit(1)

hegre = Hegre()
try:
    with console.status("Logging in"):
        hegre.login(username, password)

    console.print("[green]:heavy_check_mark: Login successful[/]")
except HegreError as e:
    console.print(f"[red]:x: {e}")
    sys.exit(1)

total = hegre.get_total_movie_count()
movies = []

with Progress() as p1:
    task = p1.add_task("[green]Fetch all movies...", total=total)
    movies = hegre.get_movies(progress=p1, task_id=task)

console.print(f"[green]:heavy_check_mark: Fetched {len(movies)} movies[/]")

with Progress() as p2:
    for movie in movies:
        hegre.fetch_movie_details(movie)

        dest_folder = f"./downloads/{movie.date.year}"
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder, exist_ok=True)

        hegre.download_movie(movie, os.path.abspath(dest_folder), progress=p2)
