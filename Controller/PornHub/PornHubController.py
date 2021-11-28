import random
from pornhub_api import PornhubApi
from Controller.AbstractController import AbstractController


class PornHubController(AbstractController):

    def __init__(self):
        super().__init__()
        self.api = PornhubApi()
        self.command_handlers = {
            "random": self._process_random_command,
            "search": self._process_keyword_command,
            "clean": self._process_clean
        }

    async def _process_random_command(self, message):
        await self._search_for_video(message, random.choice("runescape factorio csgo".split(" ")))

    async def _process_keyword_command(self, message):
        await self._search_for_video(message, message.content)

    async def _search_for_video(self, message, keywords):
        result = self.api.search.search(ordering="mostrelevant", q=keywords)
        if len(result.videos) > 0:
            video = random.choice(result.videos)
            title = video.title
            response = f"Found this: ```{title}```"
        else:
            response = "Wow, I found nothing on that."

        async with message.channel.typing():
            await message.channel.send(response)

    async def _process_clean(self, message):
        messages = await message.channel.history(limit=200).flatten()
        for m in messages:
            await m.delete()

'''
    @staticmethod
    async def handle_surprise(channel, author, keywords):
        try:
            api = PornhubApi()
            result = api.search.search(ordering="mostrelevant", q=keywords)
        except:
            # does nothing
            return
        else:
            video = random.choice(result.videos)
            title = video.title
            title = "__" + title + "__"

            surprise_intros = [
                f"YES! That's exactly what I thought when I saw this {title}.",
                f"I don't know about that, but... I can assure that this {title} isn't.",
                f"I agree with that. Also, I would add that {title} is related to this.",
            ]

            await PornHubController._send_message(channel, author, random.choice(surprise_intros))
'''

