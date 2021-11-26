import pafy
from pytube import Playlist
from youtubesearchpython import VideosSearch
from discord import FFmpegPCMAudio
import random
from Controller.AbstractController import AbstractController
import asyncio


class MusicPlayerController(AbstractController):

    class MusicPlayerGuildContext:
        def __init__(self, guild, channel):
            self.guild = guild
            self.channel = channel
            self.music_queue = []
            self.idle_cycles = 0

        def is_idle_overtime(self):
            return self.idle_cycles > 10

        def refresh_idle_time(self):
            self.idle_cycles = 0

        def get_next_music(self):
            return self.music_queue.pop(0)

        def add_music(self, music):
            self.music_queue.append(music)

        def has_playlist(self):
            return len(self.music_queue) > 0

        def is_playlist_empty(self):
            return len(self.music_queue) == 0

        def clear_playlist(self):
            self.music_queue.clear()

        def shuffle_playlist(self):
            random.shuffle(self.music_queue)

    def __init__(self):
        super().__init__()
        self.ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.guild_contexts = {}
        self.command_handlers = {
            "leave": self._leave_voice_channel,
            "stop": self._handle_stop,
            "pause": self._handle_pause,
            "resume": self._handle_resume,
            "skip": self._handle_skip,
            "play": self._handle_play,
            "shuffle": self._handle_shuffle
        }

    async def update_guild_contexts(self):

        for guild_context in self.guild_contexts.values():
            voice_client = guild_context.guild.voice_client

            if guild_context.guild.voice_client is None:
                continue

            if voice_client.is_playing():
                guild_context.refresh_idle_time()
            else:
                if guild_context.has_playlist():
                    asyncio.run_coroutine_threadsafe(self._play_next_song(guild_context), voice_client.loop)
                else:
                    guild_context.idle_cycles += 1

            if guild_context.is_idle_overtime():
                if voice_client.is_connected():
                    asyncio.run_coroutine_threadsafe(voice_client.disconnect(), voice_client.loop)

    async def _join_voice_channel(self, message):
        if not message.author.voice:
            await message.channel.send(f"{message.author.name} is not connected to a voice channel")
            return False
        else:
            await message.author.voice.channel.connect()
        return True

    async def _leave_voice_channel(self, message):
        if not message.author.voice:
            await message.send(f"{message.author.name} is not connected to a voice channel")
            return False
        else:
            voice_client = message.guild.voice_client
            if voice_client.is_connected():
                await voice_client.disconnect()
            else:
                await message.channel.send("The bot is not connected to a voice channel.")

    async def _play_next_song(self, guild_context):

        if guild_context.is_playlist_empty():
            return

        content_url = guild_context.get_next_music()
        guild_context.refresh_idle_time()

        try_again = True
        while try_again:
            try_again = False
            try:
                song = pafy.new(content_url)
                audio = song.getbestaudio()
                source = FFmpegPCMAudio(audio.url)
                guild_context.guild.voice_client.play(source)
            except:
                try_again = True

        await guild_context.channel.send(f"Playing ```{song.title}```")

    async def _handle_play(self, message):

        if message.guild.voice_client is None or not message.guild.voice_client.is_connected():
            did_join_voice = await self._join_voice_channel(message)
            if not did_join_voice:
                return

        if message.guild.id not in self.guild_contexts.keys():
            self.guild_contexts[message.guild.id] = \
                MusicPlayerController.MusicPlayerGuildContext(message.guild, message.channel)

        guild_context = self.guild_contexts[message.guild.id]
        is_playlist = "list=" in message.content and "v=" not in message.content
        is_search = "www.youtube.com" not in message.content

        if is_search:
            search_terms = message.content
            search_results = VideosSearch(search_terms, limit=10).result()["result"]
            if len(search_results) > 0:
                video = random.choice(search_results)["id"]
                guild_context.add_music(video)
        elif is_playlist:
            playlist = Playlist(message.content)
            for video in playlist:
                guild_context.add_music(video)
        else:
            video = message.content
            guild_context.add_music(video)

        if not message.guild.voice_client.is_playing():
            await self._play_next_song(guild_context)

    async def _handle_skip(self, message):
        guild_context = self.guild_contexts[message.guild.id]
        if guild_context.has_playlist():
            try:
                to_skip = min(max(int(message.content), 1), len(guild_context.music_queue))
            except:
                to_skip = 1
            guild_context.music_queue = guild_context.music_queue[to_skip-1:]

            if message.guild.voice_client.is_playing():
                message.guild.voice_client.stop()

            await self._play_next_song(guild_context)

    async def _handle_stop(self, message):
        self.guild_contexts[message.guild.id].clear_playlist()
        if message.guild.voice_client.is_playing():
            message.guild.voice_client.stop()

    async def _handle_pause(self, message):
        if message.guild.voice_client.is_playing():
            message.guild.voice_client.pause()

    async def _handle_resume(self, message):
        if not message.guild.voice_client.is_playing():
            message.guild.voice_client.resume()

    async def _handle_shuffle(self, message):
        guild_context = self.guild_contexts[message.guild.id]
        guild_context.shuffle_playlist()
