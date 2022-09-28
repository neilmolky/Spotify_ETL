import sqlite3
from spotify_recently_played.get_refresh_token import RecentSongsToken, TrackFeaturesToken
import requests
from datetime import datetime, timedelta, timezone
import pandas as pd
import sqlalchemy


class RecentlyPlayed:
    def __init__(self):
        self.today = datetime.now(timezone.utc)
        self.yesterday = self.today - timedelta(days=1)
        self.unix_timestamp = int(self.yesterday.timestamp()) * 1000  # transforms yesterday to ms
        self.data = None
        self.RecentSongs = RecentSongsToken()
        self.TrackFeatures = TrackFeaturesToken()

    @property
    def recent_songs_token(self):
        return self.RecentSongs.get_token()

    @property
    def track_features_token(self):
        return self.TrackFeatures.get_token()

    def access_spotify(self):
        print("contacting spotify user API")
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.recent_songs_token}'
        }
        url = f"https://api.spotify.com/v1/me/player/recently-played?after={self.unix_timestamp}"

        r = requests.get(url, headers=headers)

        if not r:
            raise Exception("Unable to connect to Spotify. Program terminated")

        return r.json()


    def get_recent_songs(self):
        spotify_id = []
        song_name = []
        artist_name = []
        album_name = []
        played_at = []
        album_release_date = []
        song_duration_ms = []
        song_popularity = []
        danceability = []
        energy = []
        key = []
        loudness = []
        mode = []
        speechiness = []
        acousticness = []
        instrumentalness = []
        liveness = []
        valence = []
        tempo = []
        time_signature = []

        data = self.access_spotify()

        for song in data["items"]:
            track_id = song["track"]["id"]
            spotify_id.append(track_id)
            song_name.append(song["track"]["name"])
            artist_list = []
            for artist in song["track"]["artists"]:
                artist_list.append(artist["name"])
            artist_name.append(", ".join(artist_list))
            album_name.append(song["track"]["album"]["name"])
            played_at.append(song["played_at"])
            album_release_date.append(song["track"]["album"]["release_date"])
            song_duration_ms.append(song["track"]["duration_ms"])
            song_popularity.append(song["track"]["popularity"])
            features = self.get_track_features(track_id)
            danceability.append(features["danceability"])
            energy.append(features["energy"])
            key.append(features["key"])
            loudness.append(features["loudness"])
            mode.append(features["mode"])
            speechiness.append(features["speechiness"])
            acousticness.append(features["acousticness"])
            instrumentalness.append(features["instrumentalness"])
            liveness.append(features["liveness"])
            valence.append(features["valence"])
            tempo.append(features["tempo"])
            time_signature.append(features["time_signature"])

        song_dict = {
            "spotify_id": spotify_id,
            "song_name": song_name,
            "artist_name": artist_name,
            "album_name": album_name,
            "played_at": played_at,
            "album_release_date": album_release_date,
            "song_duration_ms": song_duration_ms,
            "song_popularity": song_popularity,
            "danceability": danceability,
            "energy": energy,
            "key": key,
            "loudness": loudness,
            "mode": mode,
            "speechiness": speechiness,
            "acousticness": acousticness,
            "instrumentalness": instrumentalness,
            "liveness": liveness,
            "valence": valence,
            "tempo": tempo,
            "time_signature": time_signature,
        }

        df_cols = [key for key in song_dict]

        self.data = pd.DataFrame(song_dict, columns=df_cols)

        self.data["played_at"] = pd.to_datetime(self.data["played_at"], utc=True)


    def get_track_features(self, track_id):
        headers = {
            'Authorization': f'Bearer {self.track_features_token}',
            'Content-Type': 'application/json',
        }
        url = f"https://api.spotify.com/v1/audio-features/{track_id}"

        r = requests.get(url, headers=headers)

        if not r:
            raise Exception("Unable to connect to Spotify. Program terminated")

        return r.json()

    def run_validation(self):
        """
        returns True if data is present, False if no data is present.
        If any validation steps fail an exception will be raised terminating the program
        :return: bool
        """

        print(f"executing spotify ETL @ {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}")

        # check that a dataframe has been created
        # if no dataframe has been created our program has failed
        if self.data is None:
            raise Exception("Attempted Validation before data has been created. Program Terminated")

        # check if dataframe is empty
        # if we haven't listened to any songs data
        if self.data.empty:
            print("No songs downloaded. Execution completed.")
            return False

        # check if timestamps contain duplicated data
        # timestamps are our primary key constraint as only 1 song can be listened to at a time
        if not pd.Series(self.data["played_at"]).is_unique:
            raise Exception("Primary key violation. Program terminated.")

        # check if timestamps are in the corrct date range
        timestamps = self.data["played_at"].tolist()
        for t in timestamps:
            if not self.yesterday <= t <= self.today:
                raise Exception("Entry outside of specified date range found. Program terminated")

        # check for null values
        # we don't want nulls at all!
        if self.data.isnull().values.any():
            raise Exception("Data contains nulls. Program terminated.")

        print("Validation successful")

        return True

    def export_to_sql(self, file_path):
        """
        :param file_path: location you want to save to
        :return:
        """

        engine = sqlalchemy.create_engine(file_path)
        connection = sqlite3.connect("recently_played_tracks.sqlite")
        cursor = connection.cursor()

        sql_query = """
            CREATE TABLE IF NOT EXISTS recently_played_tracks(
                spotify_id VARCHAR(200),
                song_name VARCHAR(200),
                artist_name VARCHAR(200),
                album_name VARCHAR(200),
                played_at DATETIME,
                album_release_date DATE,
                song_duration_ms MEDIUMINT,
                song_popularity TINYINT,
                danceability FLOAT(10, 9),
                energy FLOAT(10, 9),
                key TINYINT,
                loudness FLOAT(11, 9),
                mode TINYINT,
                speechiness FLOAT(10, 9),
                acousticness FLOAT(10, 9),
                instrumentalness FLOAT(10, 9),
                liveness FLOAT(10, 9),
                valence FLOAT(10, 9),
                tempo FLOAT(15, 9),
                time_signature TINYINT,
                CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
            )
            """

        cursor.execute(sql_query)
        print("Opened database successfully")


        self.data.to_sql("recently_played_tracks.sqlite", engine, index=False, if_exists='append')

        connection.close()
        print("Database closed")


