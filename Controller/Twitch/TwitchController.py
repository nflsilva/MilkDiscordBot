from twitchAPI.twitch import Twitch

import os
from dotenv import load_dotenv
from Controller.AbstractController import AbstractController


class TwitchController(AbstractController):

    def __init__(self):
        super().__init__()
        load_dotenv()
        client_id = os.getenv("TWITCH_CLIENT_ID")
        client_secret = os.getenv("TWITCH_CLIENT_SECRET")
        self.stream_name = os.getenv("TWITCH_STREAM_NAME")
        self.stream_url = os.getenv("TWITCH_STREAM_URL")

        self.client = Twitch(client_id, client_secret)

    def get_legacy_shack_activity(self):
        try:
            tls_info = self.client.get_streams(user_login=self.stream_name)
            game_name = tls_info["data"][0]["game_name"]
            stream_url = self.stream_url
        except:
            game_name = "Postal 2"
            stream_url = "https://www.youtube.com/watch?v=Vefp3ITBu1I"
        return game_name, stream_url