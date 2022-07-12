import discord
import os
from dotenv import load_dotenv

import asyncio
from Common.MilkBackgroundJob import MilkBackgroundJob
from Controller.Twitch.TwitchController import TwitchController
from Controller.PornHub.PornHubController import PornHubController
from Controller.MusicPlayer.MusicPlayerController import MusicPlayerController
from Controller.GuildActivity.GuildActivityController import GuildActivityController


class MilkDiscordBot(discord.Client):

    def load_environment_variables(self):
        load_dotenv()
        self.token = os.getenv('DISCORD_TOKEN')
        self.server = os.getenv('DISCORD_SERVER')
        self.channel = os.getenv('DISCORD_CHANNEL')
        self.message_trigger = "!"

    def load_controllers(self):
        self.controllers = []
        self.controllers.append(TwitchController())
        self.controllers.append(PornHubController())
        self.controllers.append(MusicPlayerController())
        self.controllers.append(GuildActivityController())

    def create_background_job(self):
        self.background_job = MilkBackgroundJob(self.background_method)

    def start_activity(self):
        self.create_background_job()
        self.load_environment_variables()
        self.load_controllers()
        self.run(self.token)

    def end_activity(self):
        print("Stopping background job...")
        self.background_job.stop()

    def background_method(self):
        asyncio.run(self.update_presence())
        asyncio.run(self.update_voice_clients())

    async def update_presence(self):
        twitch_controller = None
        for controller in self.controllers:
            if isinstance(controller, TwitchController):
                twitch_controller = controller
                break

        if twitch_controller is None:
            return

        game, url = twitch_controller.get_legacy_shack_activity()
        activity = discord.Streaming(name=game, url=url)

        try:
            await bot.change_presence(activity=activity)
        except:
            pass

    async def update_voice_clients(self):
        music_controller = None
        for controller in self.controllers:
            if isinstance(controller, MusicPlayerController):
                music_controller = controller
                break

        if music_controller is None:
            return

        try:
            await music_controller.update_guild_contexts()
        except:
            pass

    async def on_ready(self):
        print("Ready!")
        self.background_job.start()

    async def on_message(self, message):
        # for debug
        if message.author == bot.user: #or message.channel.guild.name != "bottest":
            return

        is_not_trigger = message.content[:len(self.message_trigger)] != self.message_trigger
        if is_not_trigger:
            return

        message.content = message.content[len(self.message_trigger):]
        for controller in self.controllers:
            await controller.process_message(message)

        #else:
            #await PornHubController.handle_surprise(channel, author, message_text.split(" "))

    async def on_reaction_add(self, reaction, user):
        if user == bot.user:
            return

        for controller in self.controllers:
            await controller.process_reaction(reaction, user)


bot = MilkDiscordBot()
bot.start_activity()
bot.end_activity()
print("Done!")
