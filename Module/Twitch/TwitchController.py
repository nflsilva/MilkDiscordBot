from twitch import TwitchHelix
import os
from dotenv import load_dotenv

load_dotenv()
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_OAUTH_TOKEN = os.getenv('TWITCH_OAUTH_TOKEN')


class TwitchController:

    @staticmethod
    async def get_legacy_shack_activity():
        try:
            tc = TwitchHelix(client_id=TWITCH_CLIENT_ID, oauth_token=TWITCH_OAUTH_TOKEN)
            tls_info = tc.get_streams(user_logins="thelegacyshack")[0]
            game_name = tls_info.game_name
            stream_url = "https://www.twitch.tv/thelegacyshack"
        except:
            game_name = "Postal 2"
            stream_url = "https://www.youtube.com/watch?v=Vefp3ITBu1I"

        return game_name, stream_url
