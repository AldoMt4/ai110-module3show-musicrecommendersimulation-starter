import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a song and its audio attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's music taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """OOP recommender that scores and ranks songs against a UserProfile."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        """Calculate a weighted numeric score for a song against user preferences."""
        score = 0.0
        if song.genre == user.favorite_genre:
            score += 2.0
        if song.mood == user.favorite_mood:
            score += 1.5
        # Proximity score: full point when energy exactly matches, 0 at opposite ends
        score += 1.0 * (1.0 - abs(song.energy - user.target_energy))
        # Acoustic preference bonus/penalty
        if user.likes_acoustic:
            score += 0.5 * song.acousticness
        else:
            score -= 0.25 * song.acousticness
        return score

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs sorted by descending relevance score."""
        return sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation for why a song was recommended."""
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"genre match: {song.genre} (+2.0)")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood match: {song.mood} (+1.5)")
        energy_sim = 1.0 - abs(song.energy - user.target_energy)
        reasons.append(f"energy proximity: {energy_sim:.2f} (+{energy_sim:.2f})")
        if user.likes_acoustic:
            bonus = 0.5 * song.acousticness
            reasons.append(f"acoustic bonus: {song.acousticness:.2f} (+{bonus:.2f})")
        else:
            penalty = 0.25 * song.acousticness
            reasons.append(f"acoustic penalty: {song.acousticness:.2f} (-{penalty:.2f})")
        return "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file, converting numeric fields to float/int."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a single song against user preferences; returns (score, reasons)."""
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs.get("genre", ""):
        score += 2.0
        reasons.append(f"genre match: {song['genre']} (+2.0)")

    if song["mood"] == user_prefs.get("mood", ""):
        score += 1.5
        reasons.append(f"mood match: {song['mood']} (+1.5)")

    target_energy = user_prefs.get("energy", 0.5)
    energy_sim = 1.0 - abs(song["energy"] - target_energy)
    score += energy_sim
    reasons.append(f"energy proximity: {energy_sim:.2f} (+{energy_sim:.2f})")

    if "valence" in user_prefs:
        valence_sim = 1.0 - abs(song["valence"] - user_prefs["valence"])
        pts = round(0.5 * valence_sim, 2)
        score += pts
        reasons.append(f"valence proximity: {valence_sim:.2f} (+{pts:.2f})")

    if "danceability" in user_prefs:
        dance_sim = 1.0 - abs(song["danceability"] - user_prefs["danceability"])
        pts = round(0.5 * dance_sim, 2)
        score += pts
        reasons.append(f"danceability proximity: {dance_sim:.2f} (+{pts:.2f})")

    return score, reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """Score all songs and return the top-k as (song, score, explanation) tuples."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons)
        scored.append((song, score, explanation))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
