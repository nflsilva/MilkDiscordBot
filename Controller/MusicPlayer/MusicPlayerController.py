import pafy
from pytube import Playlist
from youtubesearchpython import VideosSearch
from discord import FFmpegPCMAudio
import random
from Controller.AbstractController import AbstractController
import asyncio
from Emoji import *
from discord import Embed


class MusicPlayerController(AbstractController):

    class GuildMusicPlayer:
        def __init__(self, guild, channel):
            self.guild = guild
            self.channel = channel
            self.current_music_index = 0
            self.music_queue = []
            self.idle_cycles = 0
            self.message = None
            self.in_loop = False
            self.was_shuffled = False

        def is_idle_overtime(self):
            return self.idle_cycles > 2

        def refresh_idle_time(self):
            self.idle_cycles = 0

        def get_next_music(self):
            music = self.music_queue[self.current_music_index]
            if not self.in_loop:
                self.current_music_index += 1
            return music

        def add_music(self, music):
            self.music_queue.append(music)

        def clear_playlist(self):
            self.message = None
            self.current_music_index = 0
            self.music_queue.clear()

        def shuffle_playlist(self):
            random.shuffle(self.music_queue)
            self.was_shuffled = True

        def toggle_loop(self):
            self.in_loop = not self.in_loop

        def is_on_last_music(self):
            return self.current_music_index >= len(self.music_queue) and not self.in_loop

        def get_playlist_ui(self):
            title = "Now playing \n"
            if self.in_loop or self.was_shuffled:
                title += "Modes: [ "
                if self.in_loop:
                    title += Emoji.LOOP_SINGLE + " "
                if self.was_shuffled:
                    title += Emoji.SHUFFLE + " "
                title += "]\n"
            content = title
            content += f"```\n"
            for i in range(
                    max(0, self.current_music_index - 5),
                    min(len(self.music_queue), self.current_music_index + 20)):

                song = self.music_queue[i]
                if i == self.current_music_index - 1:
                    content += Emoji.PLAY
                    embed = Embed(title=song.title, url=song.watchv_url, description="")
                    embed.set_thumbnail(url=song.bigthumbhd)
                    embed.add_field(name="Author", value=song.author, inline=False)
                content += f"[{song.duration}] {song.title}\n"
            content += f"```\n"
            return content, embed

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
        self.reaction_handlers = {
            Emoji.FAST_FORWARD: self._handle_skip_reaction,
            Emoji.FAST_REVERSE: self._handle_back_reaction,
            Emoji.STOP: self._handle_stop_reaction,
            Emoji.SHUFFLE: self._handle_shuffle_reaction,
            Emoji.LOOP_SINGLE: self._handle_loop_reaction
        }

    async def update_guild_contexts(self):
        for guild_context in self.guild_contexts.values():
            voice_client = guild_context.guild.voice_client

            if guild_context.guild.voice_client is None and guild_context.current_music_index == 0:
                continue

            if voice_client.is_playing():
                guild_context.refresh_idle_time()
            else:
                if guild_context.is_on_last_music():
                    guild_context.idle_cycles += 1
                else:
                    asyncio.run_coroutine_threadsafe(self._play_next_song(guild_context), voice_client.loop)

                if guild_context.is_idle_overtime():
                    await self._handle_stop(guild_context.message)
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

        if guild_context.is_on_last_music():
            await self._handle_stop(guild_context.message)

        song = guild_context.get_next_music()
        guild_context.refresh_idle_time()

        n_tries = 3
        while n_tries > 0:
            try:
                audio = song.getbestaudio()
                source = FFmpegPCMAudio(audio.url)
                guild_context.guild.voice_client.play(source)
                break
            except:
                n_tries -= 1

        content, embed = guild_context.get_playlist_ui()
        if guild_context.message is None:
            message = await guild_context.channel.send(content=content, embed=embed)
            guild_context.message = message
            await asyncio.gather(message.add_reaction(Emoji.FAST_REVERSE),
                                 message.add_reaction(Emoji.STOP),
                                 message.add_reaction(Emoji.FAST_FORWARD),
                                 message.add_reaction(Emoji.LOOP_SINGLE),
                                 message.add_reaction(Emoji.SHUFFLE))
        else:
            await guild_context.message.edit(content=content, embed=embed)

    async def _handle_play(self, message):

        if message.guild.voice_client is None or not message.guild.voice_client.is_connected():
            did_join_voice = await self._join_voice_channel(message)
            if not did_join_voice:
                return

        if message.guild.id not in self.guild_contexts.keys():
            self.guild_contexts[message.guild.id] = \
                MusicPlayerController.GuildMusicPlayer(message.guild, message.channel)

        guild_context = self.guild_contexts[message.guild.id]
        is_playlist = "list=" in message.content and "v=" not in message.content
        is_search = "www.youtube.com" not in message.content

        if is_search:
            search_terms = message.content
            search_results = VideosSearch(search_terms, limit=10).result()["result"]
            if len(search_results) > 0:
                video = random.choice(search_results)["id"]
                song = pafy.new(video)
                guild_context.add_music(song)
        elif is_playlist:
            playlist = Playlist(message.content)
            await message.add_reaction(Emoji.THUMBS_UP)
            loading_message = await message.channel.send(content=f"I'm loading your playlist. Just give me a minute...")
            for video in playlist:
                song = pafy.new(video)
                guild_context.add_music(song)
            await loading_message.delete()
        else:
            video = message.content
            song = pafy.new(video)
            guild_context.add_music(song)

        await message.delete()
        if not message.guild.voice_client.is_playing():
            await self._play_next_song(guild_context)
        else:
            content, embed = guild_context.get_playlist_ui()
            await asyncio.gather(guild_context.message.edit(content=content, embed=embed),
                                 message.channel.send(content=f"{Emoji.THUMBS_UP} Your request was added to the playlist.",
                                                      delete_after=5.0))

    async def _handle_skip(self, message):
        guild_context = self.guild_contexts[message.guild.id]
        if guild_context.is_on_last_music():
            await self._handle_stop(message)
        else:
            try:
                to_skip = min(max(int(message.content), 1), len(guild_context.music_queue))
            except:
                to_skip = 1
            guild_context.current_music_index += (to_skip - 1)

            if message.guild.voice_client.is_playing():
                message.guild.voice_client.stop()
            await self._play_next_song(guild_context)

    async def _handle_back(self, message):
        guild_context = self.guild_contexts[message.guild.id]
        try:
            to_back = max(int(message.content), 0)
        except:
            to_back = 1
        guild_context.current_music_index -= (to_back + 1)
        guild_context.current_music_index = max(guild_context.current_music_index, 0)

        if message.guild.voice_client.is_playing():
            message.guild.voice_client.stop()
        await self._play_next_song(guild_context)

    async def _handle_stop(self, message):
        if message is None:
            return
        await asyncio.gather(message.clear_reactions(), message.edit(embed=None))
        message.guild.voice_client.stop()
        self.guild_contexts[message.guild.id].clear_playlist()

    async def _handle_pause(self, message):
        if message.guild.voice_client.is_playing():
            message.guild.voice_client.pause()

    async def _handle_resume(self, message):
        if not message.guild.voice_client.is_playing():
            message.guild.voice_client.resume()

    def _handle_shuffle(self, message):
        guild_context = self.guild_contexts[message.guild.id]
        guild_context.shuffle_playlist()

    def _handle_loop_single(self, message):
        guild_context = self.guild_contexts[message.guild.id]
        guild_context.toggle_loop()

    # Reactions #
    async def _handle_skip_reaction(self, reaction, user):
        guild_context = self.guild_contexts[reaction.message.guild.id]
        if guild_context.message.id == reaction.message.id:
            await asyncio.gather(self._handle_skip(reaction.message),
                                 reaction.message.remove_reaction(reaction.emoji, user))

    async def _handle_back_reaction(self, reaction, user):
        guild_context = self.guild_contexts[reaction.message.guild.id]
        if guild_context.message.id == reaction.message.id:
            await asyncio.gather(self._handle_back(reaction.message),
                                 reaction.message.remove_reaction(reaction.emoji, user))

    async def _handle_stop_reaction(self, reaction, user):
        guild_context = self.guild_contexts[reaction.message.guild.id]
        if guild_context.message.id == reaction.message.id:
            await self._handle_stop(reaction.message)

    async def _handle_shuffle_reaction(self, reaction, user):
        guild_context = self.guild_contexts[reaction.message.guild.id]
        if guild_context.message.id == reaction.message.id:
            self._handle_shuffle(reaction.message)
            content, embed = guild_context.get_playlist_ui()
            await asyncio.gather(reaction.message.remove_reaction(reaction.emoji, user),
                                 reaction.message.edit(content=content, embed=embed))

    async def _handle_loop_reaction(self, reaction, user):
        guild_context = self.guild_contexts[reaction.message.guild.id]
        if guild_context.message.id == reaction.message.id:
            self._handle_loop_single(reaction.message)
            content, embed = guild_context.get_playlist_ui()
            await asyncio.gather(reaction.message.remove_reaction(reaction.emoji, user),
                                 reaction.message.edit(content=content, embed=embed))
