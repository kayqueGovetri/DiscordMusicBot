import youtube_dl
from discord import FFmpegPCMAudio
from discord.ext import commands
from discord.utils import get

from api_youtube.youtube import Youtube
from utils.utils import is_valid_url

YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.youtube = Youtube()
        self.players = {}
        self.position = {}

    def check_queues(self, ctx, id):
        if self.queues[id]:
            source = self.queues[id].pop(0)
            if type(source) == "tuple":
                source = source[0]
            self.players[id].play(
                source,
                after=lambda x=None: self.check_queues(ctx, ctx.message.guild.id),
            )

    @commands.command(pass_context=True)
    async def list(self, ctx):
        await ctx.send(self, self.queues)

    @commands.command()
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            await channel.connect()

    @commands.command(pass_context=True)
    async def play(self, ctx, *, url: str):

        if ctx.author.voice:
            player = get(self.bot.voice_clients, guild=ctx.guild)
            self.players[ctx.message.guild.id] = player

            if not is_valid_url(url=url):
                url = self.youtube.get_link_by_name(url)

            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
            url_youtube = info["url"]

            options = FFmpegPCMAudio(url_youtube, **FFMPEG_OPTIONS)

            self.players[ctx.message.guild.id].play(
                options,
                after=lambda x=None: self.check_queues(ctx, ctx.message.guild.id),
            )
            await ctx.send(f'Bot está tocando a música: {info["title"]}')

    @commands.command(pass_context=True)
    async def queue(self, ctx, *, url):
        if not is_valid_url(url=url):
            url = self.youtube.get_link_by_name(url)

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        url_youtube = info["url"]
        title = info["title"]

        source = FFmpegPCMAudio(url_youtube, **FFMPEG_OPTIONS)

        guild_id = ctx.message.guild.id

        if guild_id in self.queues:
            self.queues[guild_id].append((source, title))
        else:
            self.queues[guild_id] = [(source, title)]

        await ctx.send(f"A música {info['title']} foi adicionado na fila.")

    @commands.command(pass_context=True)
    async def next(self, ctx):
        guild_id = ctx.message.guild.id

        if guild_id in self.queues:
            if guild_id not in self.position:
                self.position[guild_id] = 0

            if self.position[guild_id] < len(self.queues[guild_id]):
                source = self.queues[guild_id][self.position[guild_id]][0]
                self.players[guild_id].stop()
                self.players[guild_id].play(
                    source,
                    after=lambda x=None: self.check_queues(ctx, ctx.message.guild.id),
                )
            else:
                await ctx.send("A fila acabou!")

    @commands.command()
    async def resume(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if not voice.is_playing():
            voice.resume()
            await ctx.send("Bot volta a tocar.")

    @commands.command()
    async def pause(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice.is_playing():
            voice.pause()
            await ctx.send("Bot está sendo pausado.")

    @commands.command()
    async def stop(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice.is_playing():
            voice.stop()
            await ctx.send("Parando o bot.")

    @commands.command()
    async def clear(self, ctx):
        guild_id = ctx.message.guild.id
        if guild_id in self.queues:
            self.queues[guild_id] = []
            await ctx.send("A fila foi limpa.")

    @commands.command()
    async def show(self, ctx):
        guild_id = ctx.message.guild.id
        if guild_id in self.queues:
            print(self.queues[guild_id])
            send = ""
            for (index, music) in enumerate(self.queues[guild_id]):
                send += f"{index+1}º {music[1]}\n"
                print(send)
            await ctx.send(send)
