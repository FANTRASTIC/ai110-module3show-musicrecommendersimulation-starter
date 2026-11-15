"""
Command line runner for the Music Recommender Simulation.

Loads the song catalog, scores every song against a taste profile,
and prints the top recommendations with the reasons behind each score.
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    """Run the recommender for the default profile and print a readable report."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Default starter profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"\nProfile: genre={user_prefs['genre']}, mood={user_prefs['mood']}, "
          f"energy={user_prefs['energy']}, likes_acoustic={user_prefs['likes_acoustic']}")
    print("\nTop recommendations:")
    print("=" * 60)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f} / 6.00")
        print("   Reasons:")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
        print("-" * 60)


if __name__ == "__main__":
    main()
