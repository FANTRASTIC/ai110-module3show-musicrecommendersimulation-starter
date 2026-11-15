# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**Vibify**: a small, explainable, content-based music recommender.

---

## 2. Intended Use  

**Goal / task.** Given one listener's taste (favorite genre, favorite mood, target energy, and whether they like acoustic music), suggest the 5 songs from a small catalog that fit best. It also says *why* each song was picked.

**Intended use.**

- Classroom learning about how recommenders turn data into rankings.
- Showing a beginner how a score and a ranking work together.
- Trying out ideas, such as changing weights, in a safe small setting.

**Not intended for.**

- A real music app with real users. The catalog is only 19 songs.
- Judging or labeling people by their taste.
- Anything that needs fairness across many cultures, languages or genres.
- Replacing human curation or listening history.

**Assumptions about the user.** The user can describe their taste in one genre, one mood and one energy number, and their taste does not change between sessions.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

**In plain language:** the recommender acts like a judge giving every song in the catalog a score out of 6 for one listener, then handing back the highest-scoring songs.

- A song earns **2 points** if its genre is the listener's favorite genre, and **1 point** if its mood matches their favorite mood. These are all-or-nothing.
- For **energy** and **acousticness**, the song earns points for being *close* to what the listener wants, not for being high or low. A song exactly on target earns the full 2 points (energy) or 1 point (acousticness), and the points shrink the further away it is. A listener who wants calm music gets no credit for a loud, fast song, however "energetic" it is.
- Every song is scored independently. Then all songs are lined up from highest to lowest score and the top few are shown.
- Each recommendation comes with its **reasons** (for example "genre match (+2.0)"), so you can see exactly where each point came from.

Compared with the starter code, which only returned the first songs in the file, this version actually scores and ranks them. It runs entirely from the command line and uses no listening history or other users, only song attributes.

---

## 4. Data  

- **Size:** 19 songs. 10 came with the starter and I added 9.
- **Features per song:** genre, mood, energy, tempo (BPM), valence, danceability, acousticness, plus title and artist.
- **Used in scoring:** genre, mood, energy and acousticness. Tempo, valence and danceability are in the file but ignored.
- **Coverage:** 16 genres and 15 moods. Lofi has 3 songs and pop has 2. Every other genre has just 1.
- **Limits:** the numbers were made up for the project, not measured from real audio. There are no lyrics, no language info, no release dates and no listener history. The catalog leans toward Western genres.

---

## 5. Strengths  

- It works well when a user's tastes agree with each other, like Chill Lofi or Deep Intense Rock. The top results matched my intuition.
- Every pick comes with reasons, like "genre match (+2.0)", so nothing is a black box. I could trace every score by hand.
- Scoring by *closeness* instead of "higher is better" keeps calm listeners away from loud songs, and the other way around.
- It degrades gracefully. A k-pop fan with no genre match still got sensible happy, energetic songs.

---

## 6. Limitations and Bias 

**Weakness found: the catalog is lopsided, so some users get a far better list than others.** Lofi has 3 songs out of 19, while rock, blues, metal and most other genres have exactly one. A lofi fan gets three strong matches (scores 5.87, 5.84 and 4.98), but a rock fan gets one strong match (Storm Runner, 5.88) and then a cliff down to 3.83, after which the list is just "loud songs". A user whose genre is not in the catalog at all (my k-pop test) can never score above 4.0 out of 6, because the genre points are simply unreachable. On top of that, genre has to match exactly: "indie pop" earns nothing for a "pop" fan. Together this means the system quietly serves some tastes much better than others, and it can only ever recommend more of what the profile already says, which is a small filter bubble. I did not find a "pop takes over" problem (pop is only 2 of 19 songs), but one song, Gym Hero, shows up in the top 5 for 4 of my 6 profiles because it is a loud, intense pop song that partly matches several different tastes.

Other limitations:

- It ignores tempo, valence and danceability, even though they are in the data.
- Energy and acousticness use a straight-line "closeness" score, so a listener who says "0.9 energy" is treated as equally happy with a song 0.1 above or below, which is not how people hear it.
- A profile can hold only one genre and one mood, so "chill lofi or jazz" cannot be expressed.

---

## 7. Evaluation  

**Profiles tested.** Three normal profiles (High-Energy Pop, Chill Lofi, Deep Intense Rock) and three tricky ones I designed to try to break the scoring: *Conflicting* (blues + sad mood, but energy 0.9), *Unknown genre* (k-pop, which is not in the catalog) and *Mixed signals* (pop genre, chill mood, mid energy, likes acoustic). Full terminal output for each is in the README under "Sample Recommendation Output".

**Does it feel right?** Mostly yes. Chill Lofi gives Midnight Coding, Library Rain and Focus Flow, which is exactly what I would put on a study playlist. Deep Intense Rock puts Storm Runner far ahead of everything else. The first pick for High-Energy Pop (Sunrise City) also feels right. What feels slightly off is the second pick, Gym Hero, which is a workout track rather than a "happy" song.

**Why does Gym Hero keep showing up for people who just want happy pop?** Think of the system as giving points on a checklist. Gym Hero is a pop song, so it gets the full genre points. It is also very high energy (0.93), which is close to what a high-energy fan asks for, so it gets almost all the energy points. It misses only the "happy" mood check. That one missed check costs just 1 point, while the 2 genre points and the energy points it did earn put it well ahead of happy songs from other genres. The system never asks "is this song actually a *vibe* match?", it only adds up the checklist. The same reasoning explains why Gym Hero also appears for rock fans: its mood is "intense", which matches their mood check, and its energy is high. Concretely, for High-Energy Pop: Sunrise City scored 5.82 (genre 2.0 + mood 1.0 + energy 1.84 + acousticness 0.98) and Gym Hero scored 4.79 (genre 2.0 + mood 0.0 + energy 1.94 + acousticness 0.85).

**What surprised me.**

- The *Conflicting* profile put Last Train Blues first. That is the only song that matches both the genre and mood the user asked for, even though its energy (0.40) is nowhere near the 0.9 they want. After that single song, the list turned into ordinary loud songs.
- In the *Mixed signals* profile, the top five songs were separated by only about 0.3 points, so tiny changes would reshuffle the list. Contradictory tastes give the system nothing to grip.
- The *Unknown genre* profile still got sensible songs (happy, energetic pop) because mood and energy carried it, but its best score was only 3.94 out of 6, which looks like a "poor match" even though the songs are good.

**Comparing pairs of profiles.**

- *High-Energy Pop vs Chill Lofi:* no song appears in both lists. Pop gets loud, danceable songs (Sunrise City, Gym Hero, Rooftop Lights); Lofi gets quiet, acoustic ones (Midnight Coding, Library Rain, Focus Flow). That is the right result, since the two profiles differ on every setting: genre, mood, energy (0.9 vs 0.4) and acoustic taste.
- *High-Energy Pop vs Deep Intense Rock:* both want very loud music, so the lists overlap heavily (Gym Hero, Sunrise City, Storm Runner and Pulse Cathedral appear in both). What differs is the order at the top: genre breaks the tie, so pop fans get Sunrise City first and rock fans get Storm Runner first. This tells me energy decides *which pool* of songs you see and genre decides *who is first*.
- *Chill Lofi vs Deep Intense Rock:* opposite ends of the scale and no overlap at all, as expected.
- *Deep Intense Rock vs Conflicting:* both want energy around 0.9, and the lists share the same loud songs (Storm Runner, Sunrise City, Gym Hero, Pulse Cathedral) after that. The only difference is Last Train Blues at number one for the conflicting user, because they asked for blues and sad. This makes sense for the scoring rules, but a real listener who wants 0.9 energy would probably not be happy with a slow sad song first.
- *High-Energy Pop vs Unknown genre (k-pop):* the lists are very similar (Sunrise City first, Rooftop Lights near the top), because k-pop has no matches and the system falls back on mood and energy. The scores are lower across the board (3.94 vs 5.82), because no song can earn genre points.
- *Chill Lofi vs Mixed signals:* the mixed profile still gets Midnight Coding and Library Rain at the top, because its mood (chill) and energy (0.5) are close to lofi's, but Sunrise City sneaks into second place purely on the pop genre match, in a near tie with the lofi songs. This shows how one strong genre match can pull a song into a list it otherwise does not fit.

**Experiment: doubling energy and halving genre.** Pop and Lofi lists barely changed, but the Conflicting list lost Last Train Blues entirely and the Mixed signals list lost its pop songs. The new lists are different, not clearly better: they are more consistent on loudness but less faithful to the genre and mood the user actually named. Details are in the README under "Experiments You Tried".

---

## 8. Future Work  

1. **Use more features and fuzzier matching.** Add tempo, valence and danceability, and give partial genre credit ("indie pop" is close to "pop").
2. **Allow richer profiles.** Let a user list several genres and moods, so "chill lofi or jazz" is possible.
3. **Add diversity to the ranking.** Avoid showing several songs from the same artist or genre in one list, and mix in one surprise pick to reduce the filter bubble.
4. **Grow the catalog** so that every genre has several songs.

---

## 9. Personal Reflection  

**Biggest learning moment.** I had assumed the weights were a small detail. Then I doubled the weight on energy and watched the one song that matched both the genre and mood a user asked for drop out of their list. A single number choice decides who the system treats well. That is where "bias" lives in a simple system.

**How AI tools helped, and when I double-checked them.** The AI wrote the loading, scoring and ranking code quickly, and it helped me think up tricky test profiles. But I still checked its work. I ran the tests and looked at the real terminal output instead of trusting a description of it. I checked that the starter `main.py` imported the wrong way for `python -m src.main` (it failed until the import was fixed). I also checked claims against the data. The assignment hint suggested pop might dominate the catalog, but pop is only 2 of 19 songs, so the real problem was uneven genre counts.

**What surprised me.** A few lines of adding-up felt like a real recommender. When Chill Lofi returned Midnight Coding, Library Rain and Focus Flow, it felt like it "got" me. The "reasons" lines add to the illusion. But Gym Hero showing up for people who only wanted happy pop showed me the system doesn't understand vibe. It only counts matches.

**What I would try next.** I would add tempo and valence, give partial credit for related genres, and add a diversity rule to the ranking. I would also test with a much bigger catalog to see if the same problems show up.

