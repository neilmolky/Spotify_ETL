from spotify_recently_played.get_recent_songs import RecentlyPlayed

DATABASE_LOCATION = "sqlite:///recently_played_tracks.sqlite"

if __name__ == "__main__":
    data = RecentlyPlayed()
    data.get_recent_songs()
    if data.run_validation():
        data.export_to_sql(DATABASE_LOCATION)










