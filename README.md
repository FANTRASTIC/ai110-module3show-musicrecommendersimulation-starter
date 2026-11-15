# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders (Spotify, YouTube, TikTok) work by turning every item and every user into numbers, then predicting how much a given user will like a given item. They blend two signals: *collaborative filtering* ("people whose behavior looks like yours liked this") and *content-based filtering* ("this song's attributes resemble ones you liked"). The big platforms lean heavily on behavior data such as skips, replays, playlist adds and what millions of other listeners did.

My version is purely **content-based**. It has no listening history and no other users, only a small catalog of songs with measurable attributes and a one-person "taste profile". It prioritizes **closeness to the user's target vibe** over "bigger is better": a song scores high when its energy and acousticness are near what the user wants and when its genre and mood match. A calm user should not be handed a 0.93-energy workout track just because its energy number is large.

### Features used

**`Song`** (from `data/songs.csv`):

| Feature | Type | Used in scoring? |
|---|---|---|
| `genre` | categorical | Yes, exact match |
| `mood` | categorical | Yes, exact match |
| `energy` | 0-1 float | Yes, proximity to target |
| `acousticness` | 0-1 float | Yes, proximity to target |
| `tempo_bpm`, `valence`, `danceability` | numeric | Not in v1 (candidates for experiments) |
| `id`, `title`, `artist` | identifiers | No, display only |

**`UserProfile`:**

- `favorite_genre` (str)
- `favorite_mood` (str)
- `target_energy` (float, 0-1)
- `likes_acoustic` (bool). It maps to a target acousticness of about 0.8 if `True` and about 0.2 if `False`.

### Algorithm Recipe

**Scoring Rule** (one song vs. one user) - add up weighted points:

| Component | Formula | Max points |
|---|---|---|
| Genre | `+2.0` if `song.genre == favorite_genre`, else 0 | 2.0 |
| Mood | `+1.0` if `song.mood == favorite_mood`, else 0 | 1.0 |
| Energy | `2.0 * (1 - abs(song.energy - target_energy))` | 2.0 |
| Acousticness | `1.0 * (1 - abs(song.acousticness - target_acousticness))` | 1.0 |

The numeric terms reward **closeness**, not magnitude. A song exactly at the target gets full points, and points fall off linearly with distance in either direction. Genre is weighted above mood because genre is a stricter boundary (a metal fan rarely wants jazz at any mood), while mood is more situational. Both weights are starting guesses to be tested in the experiments section.

**Ranking Rule** (whole catalog) - score every song with the Scoring Rule, sort descending, and return the top `k`.

**Why both are needed:** the Scoring Rule only answers "how good is *this* song for *this* user?" and produces a number in isolation. That number means nothing until it is compared against the other songs. The Ranking Rule turns a pile of independent scores into an ordered, finite list, deciding what to show first and what to cut. Keeping them separate also means I can change one without touching the other (for example, swap in a new scoring weight, or add a diversity rule to ranking so the top 5 are not all by the same artist).

### Catalog

`data/songs.csv` now holds 19 songs: the 10 starter tracks plus 9 new ones covering hip hop, classical, metal, country, R&B, EDM, reggae, folk and blues, with new moods such as confident, peaceful, angry, nostalgic, romantic, euphoric, laid-back, melancholic and sad. The columns are unchanged, so every song still has `valence`, `danceability` and `acousticness` for later experiments. Candidate extra features to add later are `loudness`, `instrumentalness` and `speechiness`.

### Example taste profile

```python
user_prefs = {
    "genre": "lofi",
    "mood": "chill",
    "energy": 0.40,
    "likes_acoustic": True,   # target acousticness ~0.8
}
```

**Critique of this profile:**
- **Can it tell "intense rock" from "chill lofi"?** Yes. Genre, mood and energy all point the same way, so Storm Runner (rock, intense, 0.91) and Iron Verdict (metal, 0.97) score near the bottom, and Library Rain and Midnight Coding score near the top.
- **Where it is narrow:** it has a single genre and a single mood, so it can't express "chill lofi *or* jazz". Ambient and jazz tracks like Spacewalk Thoughts and Coffee Shop Stories match on energy and acousticness but get 0 for genre and mood, so they rank below weaker lofi tracks.
- **Test profiles:** I'll also run a high-energy profile (rock, intense, 0.9, not acoustic) and a conflicting one (e.g. genre=classical, energy=0.9), which shows how the weights handle contradictory tastes.

### Data flow

```
INPUT                  PROCESS (loop over every row)              OUTPUT
user_prefs  ─┐
             ├─►  for song in songs.csv:                      sort by score, descending
songs.csv   ─┘        score = genre pts + mood pts                      │
 (load_songs)               + energy closeness                          ▼
                            + acousticness closeness            top K songs, each with
                        keep (song, score, reasons)             its score and "because..." reasons
```

### Expected biases

- **Genre over-prioritization:** at 2.0 of 6.0 points, a genre match outweighs mood, so a great mood-and-energy match in a neighboring genre (e.g. ambient for a lofi fan) can lose to a mediocre same-genre song.
- **Exact string matching:** `indie pop` and `pop` count as completely different, even though they are close.
- **Catalog skew:** with 19 songs, many genres have only one track, so genre-match users get one obvious pick and then a drop-off.
- **Middle-heavy energy scoring:** because closeness is linear, users with a mid-range target (about 0.5) get partial energy credit from many songs, so energy separates their results less than it does for extreme users.
- **No novelty or diversity:** the system only reinforces what the profile already says and will never introduce the user to something new.
---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` for the default profile (pop / happy / energy 0.8 / not acoustic), run on the 19-song catalog:

```
Loaded songs: 19

Profile: genre=pop, mood=happy, energy=0.8, likes_acoustic=False

Top recommendations:
============================================================
1. Sunrise City by Neon Echo
   Score: 5.94 / 6.00
   Reasons:
     - genre match: pop (+2.0)
     - mood match: happy (+1.0)
     - energy 0.82 vs target 0.80 (+1.96)
     - acousticness 0.18 vs target 0.20 (+0.98)
------------------------------------------------------------
2. Gym Hero by Max Pulse
   Score: 4.59 / 6.00
   Reasons:
     - genre match: pop (+2.0)
     - energy 0.93 vs target 0.80 (+1.74)
     - acousticness 0.05 vs target 0.20 (+0.85)
------------------------------------------------------------
3. Rooftop Lights by Indigo Parade
   Score: 3.77 / 6.00
   Reasons:
     - mood match: happy (+1.0)
     - energy 0.76 vs target 0.80 (+1.92)
     - acousticness 0.35 vs target 0.20 (+0.85)
------------------------------------------------------------
4. Night Drive Loop by Neon Echo
   Score: 2.88 / 6.00
   Reasons:
     - energy 0.75 vs target 0.80 (+1.90)
     - acousticness 0.22 vs target 0.20 (+0.98)
------------------------------------------------------------
5. Concrete Crown by Verse Mason
   Score: 2.88 / 6.00
   Reasons:
     - energy 0.78 vs target 0.80 (+1.96)
     - acousticness 0.12 vs target 0.20 (+0.92)
------------------------------------------------------------
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



