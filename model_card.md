# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0** — a content-based music recommender simulation

---

## 2. Intended Use

VibeFinder suggests up to five songs from a small catalog based on a user's stated preferences for genre, mood, energy, valence, and danceability. It is designed for **classroom exploration** of how content-based filtering works. It assumes the user can accurately describe their own taste in advance and does not learn from listening history or implicit feedback.

**Not intended for**:
- Making real product recommendations to real users
- Any context where fairness, diversity, or cultural representation is required
- Replacing a trained machine-learning model or any system that learns from actual listening behavior
- Making decisions that affect users' access to content at scale

---

## 3. How the Model Works

Think of VibeFinder as a judge at a talent show where every song auditions against the user's wish list.

Each song earns points in three categories:

1. **Genre match** — Does the song belong to the genre the user asked for? If yes, it earns the biggest reward (2.0 points), because genre is the broadest signal of musical identity.

2. **Mood match** — Does the song's emotional tone match what the user wants right now? A match earns 1.5 points. Happy songs for a happy mood, chill songs for a study session.

3. **Numeric proximity** — For features like energy, valence, and danceability, the system measures the gap between the song's value and the user's target. A song at the exact preferred energy earns a full point; a song at the opposite extreme earns zero. This rewards "closeness" rather than "highest."

After every song in the catalog has been scored, the list is sorted from highest to lowest, and the top five are returned along with a written explanation of why each song ranked where it did.

---

## 4. Data

The dataset (`data/songs.csv`) contains **20 songs** across a range of genres and moods.

**Genres represented**: pop, lofi, rock, ambient, jazz, synthwave, indie pop, country, EDM, folk, latin, classical, hip-hop, acoustic, indie rock, world music, ska

**Moods represented**: happy, chill, intense, moody, relaxed, focused

**What was added**: 10 songs were added to the original 10-song starter dataset. The additions brought in genres that were missing (country, EDM, latin, classical, hip-hop, folk, ska, world music, acoustic, indie rock) and provided better coverage of the mood spectrum.

**Whose taste does this reflect**: The catalog skews toward Western popular music and electronic genres. Traditional music from Latin America, Africa, South Asia, and East Asia is largely absent. The mood vocabulary also assumes Western emotional categories.

---

## 5. Strengths

- **Transparency**: Every point in the score is explained in plain language. Unlike a neural recommender, there are no hidden weights.
- **Predictable for clear profiles**: Users with a strong preference for one genre and mood (e.g., "lofi / chill") consistently receive relevant results because the top two scoring factors directly reward that match.
- **Handles numeric nuance**: The proximity formula for energy means the system rewards songs that are close to the user's preference, not just the highest- or lowest-energy tracks in the catalog.
- **Fast and interpretable**: No training required. Results are deterministic and explainable in a single function call.

---

## 6. Limitations and Bias

**Filter bubble effect**: Because genre match is the highest-weighted factor, users who list "pop" will almost always see pop songs in positions 1 and 2. Songs from other genres — even ones that closely match the mood and energy — are systematically deprioritized. Over time, this would narrow rather than expand a user's musical world.

**Genre label rigidity**: Genre categories are exact string matches. "Indie pop" and "pop" are treated as completely different genres even though they share many sonic qualities. A listener who loves indie pop will never get Sunrise City (labeled "pop") in their recommendations unless they type "pop" exactly.

**Cold start assumption**: The system requires the user to know and articulate their preferences before listening. In practice, many people discover what they like by browsing, not by describing it in advance.

**Dataset size**: Twenty songs is far too small for real diversity. The system can produce near-identical recommendation lists for users with different profiles if the catalog happens to lack songs in their preferred genre.

**No negative feedback**: There is no mechanism to say "I skipped this song" or "never recommend this again." The system will keep recommending the same top scorer regardless of whether the user liked it.

**Mood and genre mismatch**: Approximately 60% of the catalog is in mood categories like "happy" and "chill." Users who prefer "moody" or "focused" have fewer songs competing for the top spots, which can make their recommendations feel repetitive.

---

## 7. Evaluation

Four user profiles were tested:

| Profile | Top Result | Matched Intuition? |
|---|---|---|
| High-Energy Pop Fan (pop/happy/0.85) | Sunrise City | Yes — exact genre+mood match |
| Chill Lofi Studier (lofi/chill/0.38) | Library Rain | Yes — genre+mood+energy all close |
| Intense Rock Headbanger (rock/intense/0.92) | Storm Runner | Yes — only one rock/intense song |
| Adversarial (ambient/intense/0.90) | Storm Runner (not ambient!) | Partially — the system cannot resolve the contradiction |

**Surprises**:
- The adversarial profile placed Spacewalk Thoughts (ambient/chill) at #2 despite its low energy (0.28), purely because of the genre bonus. This shows that a +2.0 genre match can outweigh a large energy gap.
- "Gym Hero" (pop/intense) appeared in the top 5 for multiple profiles because its high energy (0.93) earns proximity points from almost every high-energy user, even when mood is wrong.
- The lofi studier profile had nearly identical scores for Library Rain and Midnight Coding (both lofi/chill), separated by less than 0.01 — the ranking is essentially a tie.

**Tests run**: Two unit tests in `tests/test_recommender.py` verify that (1) the OOP recommender sorts pop/happy songs above lofi/chill ones for a pop-loving user, and (2) explanation strings are non-empty. Both pass.

---

## 8. Future Work

- **Collaborative filtering layer**: Track which songs users skip or replay and blend that signal with content scores. This would reduce the cold-start problem.
- **Genre embedding**: Replace exact-match genre scoring with a similarity matrix so that "indie pop" and "pop" score closer than "pop" and "classical."
- **Diversity penalty**: Add a rule that prevents the same genre from occupying all top-5 slots — a "1/3 diversity budget" that forces at least two different genres into every recommendation list.
- **Larger catalog**: A dataset of 200+ songs would make the numeric proximity scores more meaningful and allow real experimentation with edge-case profiles.
- **Negative preference support**: Allow users to say "never recommend rock" and subtract points for unwanted attributes.
- **Tempo range matching**: Users who run or study often have a target BPM range. Adding tempo proximity would better serve activity-based listening.

---

## 9. Personal Reflection

**Biggest learning moment**: The adversarial profile test was the clearest aha. I designed a user who wanted an ambient genre but an intense, high-energy mood — two preferences that no song in the catalog can satisfy simultaneously. Rather than flagging the conflict, the system silently returned the "least bad" answer. This small experiment taught me something large: an algorithm can appear confident even when it is completely confused. That gap between apparent confidence and actual understanding is exactly where AI systems cause harm at scale.

**How AI tools helped — and where I had to verify**: AI tools were useful for generating the expanded song dataset and suggesting balanced weight values for the scoring formula. But I had to verify the math by hand because the first suggestion used a multiplicative formula (genre × mood × energy) instead of additive — which would have collapsed the score to zero whenever any single factor was zero. Additive scoring is more forgiving and more explainable, which is what this project needs.

**Why simple algorithms still "feel" like recommendations**: The key insight is that matching on genre and mood is a surprisingly strong signal. When a user says "pop / happy" and the system returns songs labeled "pop / happy," it feels correct — even though the system knows nothing about the actual sound of the music. The feeling of relevance comes from the label, not from acoustic understanding. Real recommendation systems work the same way at their core; they just have vastly more labels and learn them from behavior rather than CSV columns.

**What I would try next**: I would add a diversity rule — something like "no more than two songs from the same genre in the top 5." That single change would force the system to surface music the user hasn't heard of, which is how discovery actually works.
