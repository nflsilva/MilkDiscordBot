from twitch import TwitchHelix
import os
from dotenv import load_dotenv
from Controller.AbstractController import AbstractController


class TwitchController(AbstractController):

    def __init__(self):
        super().__init__()
        load_dotenv()
        client_id = os.getenv("TWITCH_CLIENT_ID")
        oath_token = os.getenv("TWITCH_OAUTH_TOKEN")
        self.client = TwitchHelix(client_id=client_id, oauth_token=oath_token)

    def get_legacy_shack_activity(self):
        try:
            tls_info = self.client.get_streams(user_logins="thelegacyshack")[0]
            game_name = tls_info.game_name
            stream_url = "https://www.twitch.tv/thelegacyshack"
        except:
            game_name = "Postal 2"
            stream_url = "https://www.youtube.com/watch?v=Vefp3ITBu1I"
        return game_name, stream_url