# 🎵 Music Recommender Simulation (Vibify)

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

**Vibify 1.0** is a small, command-line, content-based music recommender. It reads a 19-song catalog (`data/songs.csv`), compares every song to a listener's taste profile (favorite genre, favorite mood, target energy, and whether they like acoustic music), and prints the top 5 matches. Each song gets a score out of 6 built from simple, visible rules: genre match, mood match, and how *close* the song's energy and acousticness are to what the listener wants. Every recommendation comes with reasons such as "genre match: pop (+2.0)", so you can see exactly why it ranked where it did. I tested it on six profiles, including tricky ones with conflicting tastes, and ran a weight experiment to see how sensitive the rankings are.

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
   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main               # baseline weights, all six profiles
python -m src.main --experiment  # energy x2, genre x0.5
```

### Running Tests

Run the tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` with the baseline weights (genre 2.0, mood 1.0, energy 2.0, acousticness 1.0) on the 19-song catalog. It covers three normal profiles (High-Energy Pop, Chill Lofi, Deep Intense Rock) and three adversarial ones: conflicting preferences (blues + sad but energy 0.9), a genre that is not in the catalog (k-pop), and mixed signals (pop genre but chill mood and mid energy).

```
Loaded songs: 19
Weights: {'genre': 2.0, 'mood': 1.0, 'energy': 2.0, 'acoustic': 1.0} (max score 6.00)

================================================================
PROFILE: High-Energy Pop
  genre=pop, mood=happy, energy=0.9, likes_acoustic=False
================================================================
1. Sunrise City by Neon Echo [pop/happy]
   Score: 5.82 / 6.00
     - genre match: pop (+2.0)
     - mood match: happy (+1.0)
     - energy 0.82 vs target 0.90 (+1.84)
     - acousticness 0.18 vs target 0.20 (+0.98)
2. Gym Hero by Max Pulse [pop/intense]
   Score: 4.79 / 6.00
     - genre match: pop (+2.0)
     - energy 0.93 vs target 0.90 (+1.94)
     - acousticness 0.05 vs target 0.20 (+0.85)
3. Rooftop Lights by Indigo Parade [indie pop/happy]
   Score: 3.57 / 6.00
     - mood match: happy (+1.0)
     - energy 0.76 vs target 0.90 (+1.72)
     - acousticness 0.35 vs target 0.20 (+0.85)
4. Storm Runner by Voltline [rock/intense]
   Score: 2.88 / 6.00
     - energy 0.91 vs target 0.90 (+1.98)
     - acousticness 0.10 vs target 0.20 (+0.90)
5. Pulse Cathedral by Helix Drop [edm/euphoric]
   Score: 2.73 / 6.00
     - energy 0.95 vs target 0.90 (+1.90)
     - acousticness 0.03 vs target 0.20 (+0.83)

================================================================
PROFILE: Chill Lofi
  genre=lofi, mood=chill, energy=0.4, likes_acoustic=True
================================================================
1. Midnight Coding by LoRoom [lofi/chill]
   Score: 5.87 / 6.00
     - genre match: lofi (+2.0)
     - mood match: chill (+1.0)
     - energy 0.42 vs target 0.40 (+1.96)
     - acousticness 0.71 vs target 0.80 (+0.91)
2. Library Rain by Paper Lanterns [lofi/chill]
   Score: 5.84 / 6.00
     - genre match: lofi (+2.0)
     - mood match: chill (+1.0)
     - energy 0.35 vs target 0.40 (+1.90)
     - acousticness 0.86 vs target 0.80 (+0.94)
3. Focus Flow by LoRoom [lofi/focused]
   Score: 4.98 / 6.00
     - genre match: lofi (+2.0)
     - energy 0.40 vs target 0.40 (+2.00)
     - acousticness 0.78 vs target 0.80 (+0.98)
4. Spacewalk Thoughts by Orbit Bloom [ambient/chill]
   Score: 3.64 / 6.00
     - mood match: chill (+1.0)
     - energy 0.28 vs target 0.40 (+1.76)
     - acousticness 0.92 vs target 0.80 (+0.88)
5. Last Train Blues by Delta Marlowe [blues/sad]
   Score: 2.96 / 6.00
     - energy 0.40 vs target 0.40 (+2.00)
     - acousticness 0.76 vs target 0.80 (+0.96)

================================================================
PROFILE: Deep Intense Rock
  genre=rock, mood=intense, energy=0.92, likes_acoustic=False
================================================================
1. Storm Runner by Voltline [rock/intense]
   Score: 5.88 / 6.00
     - genre match: rock (+2.0)
     - mood match: intense (+1.0)
     - energy 0.91 vs target 0.92 (+1.98)
     - acousticness 0.10 vs target 0.20 (+0.90)
2. Gym Hero by Max Pulse [pop/intense]
   Score: 3.83 / 6.00
     - mood match: intense (+1.0)
     - energy 0.93 vs target 0.92 (+1.98)
     - acousticness 0.05 vs target 0.20 (+0.85)
3. Sunrise City by Neon Echo [pop/happy]
   Score: 2.78 / 6.00
     - energy 0.82 vs target 0.92 (+1.80)
     - acousticness 0.18 vs target 0.20 (+0.98)
4. Pulse Cathedral by Helix Drop [edm/euphoric]
   Score: 2.77 / 6.00
     - energy 0.95 vs target 0.92 (+1.94)
     - acousticness 0.03 vs target 0.20 (+0.83)
5. Iron Verdict by Black Cairn [metal/angry]
   Score: 2.74 / 6.00
     - energy 0.97 vs target 0.92 (+1.90)
     - acousticness 0.04 vs target 0.20 (+0.84)

================================================================
PROFILE: Conflicting (sad but high energy)
  genre=blues, mood=sad, energy=0.9, likes_acoustic=False
================================================================
1. Last Train Blues by Delta Marlowe [blues/sad]
   Score: 4.44 / 6.00
     - genre match: blues (+2.0)
     - mood match: sad (+1.0)
     - energy 0.40 vs target 0.90 (+1.00)
     - acousticness 0.76 vs target 0.20 (+0.44)
2. Storm Runner by Voltline [rock/intense]
   Score: 2.88 / 6.00
     - energy 0.91 vs target 0.90 (+1.98)
     - acousticness 0.10 vs target 0.20 (+0.90)
3. Sunrise City by Neon Echo [pop/happy]
   Score: 2.82 / 6.00
     - energy 0.82 vs target 0.90 (+1.84)
     - acousticness 0.18 vs target 0.20 (+0.98)
4. Gym Hero by Max Pulse [pop/intense]
   Score: 2.79 / 6.00
     - energy 0.93 vs target 0.90 (+1.94)
     - acousticness 0.05 vs target 0.20 (+0.85)
5. Pulse Cathedral by Helix Drop [edm/euphoric]
   Score: 2.73 / 6.00
     - energy 0.95 vs target 0.90 (+1.90)
     - acousticness 0.03 vs target 0.20 (+0.83)

================================================================
PROFILE: Unknown genre (k-pop)
  genre=k-pop, mood=happy, energy=0.8, likes_acoustic=False
================================================================
1. Sunrise City by Neon Echo [pop/happy]
   Score: 3.94 / 6.00
     - mood match: happy (+1.0)
     - energy 0.82 vs target 0.80 (+1.96)
     - acousticness 0.18 vs target 0.20 (+0.98)
2. Rooftop Lights by Indigo Parade [indie pop/happy]
   Score: 3.77 / 6.00
     - mood match: happy (+1.0)
     - energy 0.76 vs target 0.80 (+1.92)
     - acousticness 0.35 vs target 0.20 (+0.85)
3. Night Drive Loop by Neon Echo [synthwave/moody]
   Score: 2.88 / 6.00
     - energy 0.75 vs target 0.80 (+1.90)
     - acousticness 0.22 vs target 0.20 (+0.98)
4. Concrete Crown by Verse Mason [hip hop/confident]
   Score: 2.88 / 6.00
     - energy 0.78 vs target 0.80 (+1.96)
     - acousticness 0.12 vs target 0.20 (+0.92)
5. Storm Runner by Voltline [rock/intense]
   Score: 2.68 / 6.00
     - energy 0.91 vs target 0.80 (+1.78)
     - acousticness 0.10 vs target 0.20 (+0.90)

================================================================
PROFILE: Mixed signals (pop + chill, mid energy)
  genre=pop, mood=chill, energy=0.5, likes_acoustic=True
================================================================
1. Midnight Coding by LoRoom [lofi/chill]
   Score: 3.75 / 6.00
     - mood match: chill (+1.0)
     - energy 0.42 vs target 0.50 (+1.84)
     - acousticness 0.71 vs target 0.80 (+0.91)
2. Sunrise City by Neon Echo [pop/happy]
   Score: 3.74 / 6.00
     - genre match: pop (+2.0)
     - energy 0.82 vs target 0.50 (+1.36)
     - acousticness 0.18 vs target 0.80 (+0.38)
3. Library Rain by Paper Lanterns [lofi/chill]
   Score: 3.64 / 6.00
     - mood match: chill (+1.0)
     - energy 0.35 vs target 0.50 (+1.70)
     - acousticness 0.86 vs target 0.80 (+0.94)
4. Spacewalk Thoughts by Orbit Bloom [ambient/chill]
   Score: 3.44 / 6.00
     - mood match: chill (+1.0)
     - energy 0.28 vs target 0.50 (+1.56)
     - acousticness 0.92 vs target 0.80 (+0.88)
5. Gym Hero by Max Pulse [pop/intense]
   Score: 3.39 / 6.00
     - genre match: pop (+2.0)
     - energy 0.93 vs target 0.50 (+1.14)
     - acousticness 0.05 vs target 0.80 (+0.25)
```


---

## Experiments You Tried

**Experiment: weight shift.** I doubled the weight on energy (2.0 to 4.0) and halved the weight on genre (2.0 to 1.0). The maximum possible score goes from 6.0 to 7.0 (1.0 + 1.0 + 4.0 + 1.0), and `main.py` now reads that maximum from the weights instead of hard-coding it, so the "score / max" display stays correct. Run it with `python -m src.main --experiment`.

What changed:

- **High-Energy Pop:** same top 3 and same order, but the gap between Gym Hero (an intense pop song) and Rooftop Lights (indie pop) shrank from 1.2 points to 0.4.
- **Chill Lofi:** identical top 5. Lofi songs win on every dimension, so nothing was in tension.
- **Deep Intense Rock:** Storm Runner is still first, but Gym Hero is now only 1.05 behind instead of 2.05.
- **Conflicting (blues, sad, 0.9 energy):** the biggest change. Last Train Blues, the only song matching both the genre and mood the user asked for, fell out of the top 5 entirely, replaced by loud songs that matched only the energy.
- **Mixed signals (pop + chill):** the pop songs vanished from the top 5. The list became chill, calm songs, plus a country song.

Verdict: the change made the results **different, not clearly more accurate**. It helps users whose main concern is energy, but it punishes users whose stated genre and mood disagree with their energy, because the one song that matched what they *said* they wanted lost to songs that only matched a number.

<details>
<summary>Full terminal output with experiment weights</summary>

```
Loaded songs: 19
Weights: {'genre': 1.0, 'mood': 1.0, 'energy': 4.0, 'acoustic': 1.0} (max score 7.00)

================================================================
PROFILE: High-Energy Pop
  genre=pop, mood=happy, energy=0.9, likes_acoustic=False
================================================================
1. Sunrise City by Neon Echo [pop/happy]
   Score: 6.66 / 7.00
     - genre match: pop (+1.0)
     - mood match: happy (+1.0)
     - energy 0.82 vs target 0.90 (+3.68)
     - acousticness 0.18 vs target 0.20 (+0.98)
2. Gym Hero by Max Pulse [pop/intense]
   Score: 5.73 / 7.00
     - genre match: pop (+1.0)
     - energy 0.93 vs target 0.90 (+3.88)
     - acousticness 0.05 vs target 0.20 (+0.85)
3. Rooftop Lights by Indigo Parade [indie pop/happy]
   Score: 5.29 / 7.00
     - mood match: happy (+1.0)
     - energy 0.76 vs target 0.90 (+3.44)
     - acousticness 0.35 vs target 0.20 (+0.85)
4. Storm Runner by Voltline [rock/intense]
   Score: 4.86 / 7.00
     - energy 0.91 vs target 0.90 (+3.96)
     - acousticness 0.10 vs target 0.20 (+0.90)
5. Pulse Cathedral by Helix Drop [edm/euphoric]
   Score: 4.63 / 7.00
     - energy 0.95 vs target 0.90 (+3.80)
     - acousticness 0.03 vs target 0.20 (+0.83)

================================================================
PROFILE: Chill Lofi
  genre=lofi, mood=chill, energy=0.4, likes_acoustic=True
================================================================
1. Midnight Coding by LoRoom [lofi/chill]
   Score: 6.83 / 7.00
     - genre match: lofi (+1.0)
     - mood match: chill (+1.0)
     - energy 0.42 vs target 0.40 (+3.92)
     - acousticness 0.71 vs target 0.80 (+0.91)
2. Library Rain by Paper Lanterns [lofi/chill]
   Score: 6.74 / 7.00
     - genre match: lofi (+1.0)
     - mood match: chill (+1.0)
     - energy 0.35 vs target 0.40 (+3.80)
     - acousticness 0.86 vs target 0.80 (+0.94)
3. Focus Flow by LoRoom [lofi/focused]
   Score: 5.98 / 7.00
     - genre match: lofi (+1.0)
     - energy 0.40 vs target 0.40 (+4.00)
     - acousticness 0.78 vs target 0.80 (+0.98)
4. Spacewalk Thoughts by Orbit Bloom [ambient/chill]
   Score: 5.40 / 7.00
     - mood match: chill (+1.0)
     - energy 0.28 vs target 0.40 (+3.52)
     - acousticness 0.92 vs target 0.80 (+0.88)
5. Last Train Blues by Delta Marlowe [blues/sad]
   Score: 4.96 / 7.00
     - energy 0.40 vs target 0.40 (+4.00)
     - acousticness 0.76 vs target 0.80 (+0.96)

================================================================
PROFILE: Deep Intense Rock
  genre=rock, mood=intense, energy=0.92, likes_acoustic=False
================================================================
1. Storm Runner by Voltline [rock/intense]
   Score: 6.86 / 7.00
     - genre match: rock (+1.0)
     - mood match: intense (+1.0)
     - energy 0.91 vs target 0.92 (+3.96)
     - acousticness 0.10 vs target 0.20 (+0.90)
2. Gym Hero by Max Pulse [pop/intense]
   Score: 5.81 / 7.00
     - mood match: intense (+1.0)
     - energy 0.93 vs target 0.92 (+3.96)
     - acousticness 0.05 vs target 0.20 (+0.85)
3. Pulse Cathedral by Helix Drop [edm/euphoric]
   Score: 4.71 / 7.00
     - energy 0.95 vs target 0.92 (+3.88)
     - acousticness 0.03 vs target 0.20 (+0.83)
4. Iron Verdict by Black Cairn [metal/angry]
   Score: 4.64 / 7.00
     - energy 0.97 vs target 0.92 (+3.80)
     - acousticness 0.04 vs target 0.20 (+0.84)
5. Sunrise City by Neon Echo [pop/happy]
   Score: 4.58 / 7.00
     - energy 0.82 vs target 0.92 (+3.60)
     - acousticness 0.18 vs target 0.20 (+0.98)

================================================================
PROFILE: Conflicting (sad but high energy)
  genre=blues, mood=sad, energy=0.9, likes_acoustic=False
================================================================
1. Storm Runner by Voltline [rock/intense]
   Score: 4.86 / 7.00
     - energy 0.91 vs target 0.90 (+3.96)
     - acousticness 0.10 vs target 0.20 (+0.90)
2. Gym Hero by Max Pulse [pop/intense]
   Score: 4.73 / 7.00
     - energy 0.93 vs target 0.90 (+3.88)
     - acousticness 0.05 vs target 0.20 (+0.85)
3. Sunrise City by Neon Echo [pop/happy]
   Score: 4.66 / 7.00
     - energy 0.82 vs target 0.90 (+3.68)
     - acousticness 0.18 vs target 0.20 (+0.98)
4. Pulse Cathedral by Helix Drop [edm/euphoric]
   Score: 4.63 / 7.00
     - energy 0.95 vs target 0.90 (+3.80)
     - acousticness 0.03 vs target 0.20 (+0.83)
5. Iron Verdict by Black Cairn [metal/angry]
   Score: 4.56 / 7.00
     - energy 0.97 vs target 0.90 (+3.72)
     - acousticness 0.04 vs target 0.20 (+0.84)

================================================================
PROFILE: Unknown genre (k-pop)
  genre=k-pop, mood=happy, energy=0.8, likes_acoustic=False
================================================================
1. Sunrise City by Neon Echo [pop/happy]
   Score: 5.90 / 7.00
     - mood match: happy (+1.0)
     - energy 0.82 vs target 0.80 (+3.92)
     - acousticness 0.18 vs target 0.20 (+0.98)
2. Rooftop Lights by Indigo Parade [indie pop/happy]
   Score: 5.69 / 7.00
     - mood match: happy (+1.0)
     - energy 0.76 vs target 0.80 (+3.84)
     - acousticness 0.35 vs target 0.20 (+0.85)
3. Concrete Crown by Verse Mason [hip hop/confident]
   Score: 4.84 / 7.00
     - energy 0.78 vs target 0.80 (+3.92)
     - acousticness 0.12 vs target 0.20 (+0.92)
4. Night Drive Loop by Neon Echo [synthwave/moody]
   Score: 4.78 / 7.00
     - energy 0.75 vs target 0.80 (+3.80)
     - acousticness 0.22 vs target 0.20 (+0.98)
5. Storm Runner by Voltline [rock/intense]
   Score: 4.46 / 7.00
     - energy 0.91 vs target 0.80 (+3.56)
     - acousticness 0.10 vs target 0.20 (+0.90)

================================================================
PROFILE: Mixed signals (pop + chill, mid energy)
  genre=pop, mood=chill, energy=0.5, likes_acoustic=True
================================================================
1. Midnight Coding by LoRoom [lofi/chill]
   Score: 5.59 / 7.00
     - mood match: chill (+1.0)
     - energy 0.42 vs target 0.50 (+3.68)
     - acousticness 0.71 vs target 0.80 (+0.91)
2. Library Rain by Paper Lanterns [lofi/chill]
   Score: 5.34 / 7.00
     - mood match: chill (+1.0)
     - energy 0.35 vs target 0.50 (+3.40)
     - acousticness 0.86 vs target 0.80 (+0.94)
3. Spacewalk Thoughts by Orbit Bloom [ambient/chill]
   Score: 5.00 / 7.00
     - mood match: chill (+1.0)
     - energy 0.28 vs target 0.50 (+3.12)
     - acousticness 0.92 vs target 0.80 (+0.88)
4. Dusty Porch Light by Hollis Creek [country/nostalgic]
   Score: 4.91 / 7.00
     - energy 0.48 vs target 0.50 (+3.92)
     - acousticness 0.81 vs target 0.80 (+0.99)
5. Focus Flow by LoRoom [lofi/focused]
   Score: 4.58 / 7.00
     - energy 0.40 vs target 0.50 (+3.60)
     - acousticness 0.78 vs target 0.80 (+0.98)
```

</details>

---

## Limitations and Risks

- **Tiny, uneven catalog.** With 19 songs, lofi has 3 and most genres have just 1. A lofi fan gets three strong matches, while a rock fan gets one and then a sharp drop in quality.
- **Exact matching only.** "indie pop" earns nothing for a "pop" fan, and a genre that is not in the catalog (like k-pop) can never earn genre points, so those users cannot score above 4.0 out of 6.
- **Only one genre and one mood per profile.** It cannot express "chill lofi or jazz", and it cannot handle tastes that change with the situation.
- **Ignores most of the data.** Tempo, valence and danceability are in the CSV but not scored. It also has no lyrics, language, or listening history.
- **Checklist, not understanding.** It adds up matches, so a loud intense pop song (Gym Hero) shows up for happy-pop fans and rock fans alike. It does not know what a song actually *feels* like.
- **Filter bubble.** It only returns more of what the profile already says, with no novelty or diversity.
- **Sensitive to weights.** Doubling energy and halving genre dropped the one song that matched a user's stated genre and mood out of their list. The weights are my choices, and they decide who the system serves well.
- **Fairness.** The made-up catalog leans toward Western genres. A real system built this way could consistently serve some listeners worse than others.

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Building this showed me that a recommender is mostly a series of small choices that look neutral but are not. A recommender turns data into predictions by giving each item a score and sorting by it. Everything interesting happens in the scoring rule. The idea of rewarding *closeness* instead of "bigger is better" kept calm listeners away from loud songs. The reasons list made the results trustworthy, because I could check any ranking by hand. It also made it easy to see when the system was wrong, like when Gym Hero kept appearing for people who only wanted happy pop. It matched a checklist, not a vibe.

Bias shows up in the places that feel like details: the weights, the catalog, and the exact-match rules. Doubling the weight on energy pushed out the one song that matched a user's stated genre and mood, so the system served that user worse. Uneven genre counts mean some tastes get a full list of good options while others get one. In a real product these quiet choices would decide whose music gets heard. Using AI tools sped up the coding and brainstorming, but I still had to run the code, read the real output and check its claims against the data. For example, the starter code's import failed under `python -m src.main`, and the hint that pop might dominate did not match this catalog. Next I would add more features, partial genre credit and a diversity rule, and test on a much larger catalog.
