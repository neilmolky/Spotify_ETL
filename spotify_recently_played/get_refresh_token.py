from spotify_recently_played.spotify_secrets import recent_songs_token, recent_songs_id, recent_songs_secret, track_features_secret, track_features_id
import requests


class RecentSongsToken:

    def __init__(self):
        self.refresh_token = recent_songs_token
        self.client_id = recent_songs_id
        self.client_secret = recent_songs_secret

    def get_token(self):
        """
        using the recent_songs_token from our secrets file this function will create a new API token
        :return: API token
        """
        url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }

        r = requests.post(url, data=data, auth=(self.client_id, self.client_secret))

        if not r:
            raise Exception("Unable to get new API token. program Terminated.")

        response = r.json()

        return response["access_token"]


class TrackFeaturesToken:

    def __init__(self):
        self.client_id = track_features_id
        self.client_secret = track_features_secret
        self.grant_type = ""

    def get_token(self):
        """
        using the client ID and Secret alone we can generate an access token
        :return: API token
        """
        url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "client_credentials",
        }
        r = requests.post(url, data=data, auth=(self.client_id, self.client_secret))

        if not r:
            raise Exception("Unable to get new API token. program Terminated.")

        response = r.json()

        return response["access_token"]