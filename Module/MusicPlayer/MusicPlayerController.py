import pafy
from discord import FFmpegPCMAudio
import asyncio

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}


class MusicPlayerController:

    voice_clients = {}

    @staticmethod
    async def _send_message(channel, text):
        await channel.send(f"{text}")

    @staticmethod
    async def handle_command(command, channel, author, voice_client):
        command_parts = command.split(" ")[1:]
        if len(command_parts) == 1:
            command_handlers = {
                "leave": MusicPlayerController._handle_leave,
                "stop": MusicPlayerController._handle_stop,
                "pause": MusicPlayerController._handle_pause,
                "resume": MusicPlayerController._handle_resume,
            }
            try:
                handler = command_handlers[command_parts[0]]
            except:
                return
            await handler(channel, author, voice_client)
        if len(command_parts) == 2:
            command_handlers = {
                "play": MusicPlayerController._handle_play,
            }
            try:
                handler = command_handlers[command_parts[0]]
                arguments = command_parts[1:]
            except:
                return
            await handler(channel, author, arguments, voice_client)

    @staticmethod
    async def _join_author_channel(channel, author):
        if not author.voice:
            await MusicPlayerController._send_message(channel, f"{author.name} is not connected to a voice channel")
            return False
        else:
            voice_channel = author.voice.channel
            await voice_channel.connect()
        return True

    @staticmethod
    async def _handle_leave(channel, author, voice_client):
        if not author.voice:
            await MusicPlayerController._send_message(channel, f"{author.name} is not connected to a voice channel")
            return False
        else:
            if voice_client.is_connected():
                await voice_client.disconnect()
            else:
                await MusicPlayerController._send_message(channel, "The bot is not connected to a voice channel.")

    @staticmethod
    async def _handle_play(channel, author, arguments, voice_client):
        if voice_client is None or not voice_client.is_playing():

            if voice_client is None:
                did_join_voice = await MusicPlayerController._join_author_channel(channel, author)

                if not did_join_voice:
                    return

            server = author.guild
            voice_client = server.voice_client
            MusicPlayerController.voice_clients[server.id] = 0
            async with channel.typing():
                #filename = "/mnt/storage/Archive/Music/RED/RED - Already Over.mp3"
                #voice_channel.play(discord.FFmpegPCMAudio(source=filename))
                video_url = arguments[0]
                song = pafy.new(video_url)
                audio = song.getbestaudio()
                source = FFmpegPCMAudio(audio.url)
                voice_client.play(source)
            await MusicPlayerController._send_message(channel, f'Now playing: {song.title}')

    @staticmethod
    async def _handle_stop(channel, author, voice_client):
        if voice_client.is_playing():
            voice_client.stop()

    @staticmethod
    async def _handle_pause(channel, author, voice_client):
        if voice_client.is_playing():
            voice_client.pause()

    @staticmethod
    async def _handle_resume(channel, author, voice_client):
        if not voice_client.is_playing():
            voice_client.resume()
