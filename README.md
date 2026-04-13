# Music Recommender Simulation

## Project Summary

This project simulates how a basic music recommendation engine works. Given a user's taste profile (favorite genre, mood, and energy level), the system scores every song in a catalog using a weighted formula and returns the top matches with plain-language explanations.

Unlike collaborative filtering (which relies on what millions of other users listen to), this version uses **content-based filtering**: it compares the attributes of each song directly against what the user says they like. Real platforms like Spotify combine both approaches, but content-based filtering is a great starting point because the logic is transparent and easy to reason about.

---

## How The System Works

### Real-World Context

Streaming platforms like Spotify build "taste profiles" by tracking every skip, replay, and playlist add. They use collaborative filtering to say "people like you also love this song" and content-based filtering to say "this song has the same tempo, energy, and key as the ones you play on repeat." The Spotify Wrapped model blends both signals and continuously retrains on hundreds of millions of users.

Our simulation focuses on the content-based side because we can see every calculation.

### Features Used

Each `Song` in `data/songs.csv` has these attributes:

| Feature | Type | Description |
|---|---|---|
| `genre` | categorical | Musical style (pop, lofi, rock, etc.) |
| `mood` | categorical | Emotional tone (happy, chill, intense, etc.) |
| `energy` | float 0–1 | Intensity and activity level |
| `tempo_bpm` | float | Beats per minute |
| `valence` | float 0–1 | Musical positivity |
| `danceability` | float 0–1 | How suitable for dancing |
| `acousticness` | float 0–1 | Acoustic vs. electronic character |

### User Profile

A `UserProfile` stores:
- `favorite_genre` — the genre to match against
- `favorite_mood` — the mood to match against
- `target_energy` — preferred intensity level (0.0–1.0)
- `likes_acoustic` — boolean that flips the acoustic bonus/penalty

For the functional CLI (in `main.py`), profiles can also include `valence` and `danceability` targets.

### Algorithm Recipe (Scoring Rule)

For each song, `score_song()` computes:

```
score = 0
if song.genre == user.genre:        score += 2.0   (genre match)
if song.mood  == user.mood:         score += 1.5   (mood match)
score += 1.0 * (1 - |song.energy - user.energy|)   (energy proximity)
score += 0.5 * (1 - |song.valence - user.valence|)  (valence proximity, optional)
score += 0.5 * (1 - |song.dance - user.dance|)      (danceability proximity, optional)
```

Genre is worth the most (+2.0) because it is the broadest signal of musical identity. Mood comes next (+1.5) because emotional context strongly shapes what we want to hear. Numeric features like energy contribute up to +1.0 based on how close the song is to the user's target — a song at the exact preferred energy gets the full point; a song at the opposite extreme gets zero.

### Ranking Rule

`recommend_songs()` calls `score_song()` for every song in the catalog, collects all `(song, score, explanation)` tuples, sorts them by score in descending order, and returns the top `k`.

### Data Flow

```
User Preferences (genre, mood, energy, ...)
          │
          ▼
  For each song in songs.csv
          │
          ├─ genre match? +2.0
          ├─ mood match?  +1.5
          ├─ energy gap → proximity score (+0–1.0)
          ├─ valence gap → proximity score (+0–0.5)
          └─ danceability gap → proximity score (+0–0.5)
          │
          ▼
   Sort all (song, score) pairs descending
          │
          ▼
   Top-K Recommendations with explanations
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the recommender:

   ```bash
   python3 -m src.main
   ```

### Running Tests

```bash
pytest
```

---

## Experiments You Tried

### Experiment 1 — Weight Shift (Genre 2.0 → 0.5)

When genre weight was reduced to 0.5, mood and energy dominated the rankings. The "Chill Lofi Studier" profile started recommending ambient and world-music tracks ahead of actual lofi songs because their chill mood and matching energy mattered more than the exact genre label. This shows that genre is acting as a strong anchor — lower its weight and the system becomes more adventurous but less predictable.

### Experiment 2 — Adversarial Profile (ambient genre + high energy + intense mood)

A profile asking for `genre=ambient` but `mood=intense, energy=0.90` exposed a tension in the scoring: the only ambient song in the catalog (Spacewalk Thoughts) has very low energy (0.28), so it earned the genre bonus (+2.0) but was penalized heavily on energy proximity. Meanwhile, high-energy intense songs (Storm Runner, Bass Drop City) won on mood+energy but lost the genre point. The system could not satisfy both wishes simultaneously — a real-world sign that the user profile is internally contradictory.

### Experiment 3 — Feature Removal (mood check disabled)

Commenting out the mood scoring caused "Gym Hero" (pop, intense) to overtake "Sunrise City" (pop, happy) for the High-Energy Pop Fan because Gym Hero's energy (0.93) is marginally closer to the target (0.85) than Sunrise City's (0.82). Without mood as a tiebreaker, the system optimized purely for numeric proximity, losing the emotional context that makes the recommendation feel right.

---

## Limitations and Risks

- **Tiny catalog**: 20 songs means genre diversity is thin — many genres (R&B, blues, metal, reggae) are absent entirely.
- **Genre label rigidity**: A user who likes "indie pop" will never match songs labeled "pop" even when they are nearly identical in sound.
- **No history**: Every session starts cold — the system cannot learn from what the user actually played or skipped.
- **No language or lyric awareness**: Two songs with identical features but very different lyrical themes (e.g., a love ballad vs. a political anthem) are treated as equivalent.
- **Filter bubble risk**: High genre weight means users who list "pop" will almost always see pop songs ranked first, reinforcing existing preferences and hiding music they might love in other genres.

See `model_card.md` for a deeper analysis.

---

## Reflection

See [Model Card](model_card.md) for the full evaluation.

Building this system made it clear how much real platforms have to hide under the hood. Our simple weighted formula is transparent — you can read every point — but that transparency also reveals every flaw. Genre matching is blunt: "lofi" and "ambient" are treated as opposites even though they share the same sleepy, textural qualities. A real recommender would embed songs in a continuous vector space where those genres end up close together.

The most surprising finding was the adversarial profile. A user who says "I want ambient but intense" cannot be satisfied because the catalog has no songs that match both. A production system would surface this conflict with a message like "we couldn't find many tracks that match all your preferences." Our system silently returns the least-bad option with no warning — which is the kind of quiet failure that erodes trust in AI tools.
