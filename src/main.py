"""
Command line runner for the Music Recommender Simulation.

Run with:  python -m src.main
"""

import os
import sys

# Allow running from repo root without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from recommender import load_songs, recommend_songs


PROFILES = {
    "High-Energy Pop Fan": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "valence": 0.80,
        "danceability": 0.80,
    },
    "Chill Lofi Studier": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "valence": 0.58,
        "danceability": 0.60,
    },
    "Intense Rock Headbanger": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "valence": 0.45,
        "danceability": 0.65,
    },
    "Adversarial (Chill Genre + High Energy)": {
        "genre": "ambient",
        "mood": "intense",
        "energy": 0.90,
        "valence": 0.50,
        "danceability": 0.50,
    },
}


def print_separator(char: str = "-", width: int = 60) -> None:
    print(char * width)


def run_profile(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    print_separator("=")
    print(f"  Profile: {name}")
    print(f"  Prefs:   genre={user_prefs['genre']}, mood={user_prefs['mood']}, "
          f"energy={user_prefs['energy']}")
    print_separator("=")

    recommendations = recommend_songs(user_prefs, songs, k=k)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"  #{rank}  {song['title']} by {song['artist']}")
        print(f"       Genre: {song['genre']} | Mood: {song['mood']} | "
              f"Energy: {song['energy']:.2f}")
        print(f"       Score: {score:.2f}")
        print(f"       Why:   {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print()

    for profile_name, user_prefs in PROFILES.items():
        run_profile(profile_name, user_prefs, songs, k=5)


if __name__ == "__main__":
    main()
