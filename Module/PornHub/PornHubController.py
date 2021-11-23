import random
from discord import AllowedMentions
from pornhub_api import PornhubApi


class PornHubController:

    @staticmethod
    async def _send_message(channel, author, text):
        mention = author.mention
        allowed_mentions = AllowedMentions(users=True)
        await channel.send(f"{mention} {text}", allowed_mentions=allowed_mentions)

    @staticmethod
    async def _handle_keyword_title(channel, author, keywords):
        try:
            api = PornhubApi()
            result = api.search.search(ordering="mostrelevant", q=keywords)
        except:
            await PornHubController._send_message(channel, author, f", wtf. No videos found.")

        else:
            video = random.choice(result.videos)
            title = video.title
            #thumb = video.thumb
            await PornHubController._send_message(channel, author, f", there you go:\n"
                                                              f"> {title}\n")

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

    @staticmethod
    async def handle_command(command, channel, author):
        command_parts = command.split(" ")[1:]
        if len(command_parts) == 1:
            command_handlers = {
                "random": PornHubController._handle_random_title,
            }
            try:
                handler = command_handlers[command_parts[0]]
            except:
                return
            await handler(channel, author, random.choice(["shemale", "wife", "man", "bbc"]))

        if len(command_parts) > 1:
            command_handlers = {
                "search": PornHubController._handle_keyword_title,
            }
            try:
                handler = command_handlers[command_parts[0]]
                arguments = command_parts[1:]
            except:
                return
            await handler(channel, author, arguments)
