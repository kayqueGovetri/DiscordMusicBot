import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import os
import youtube_dl
from discord.utils import get

intents = discord.Intents.default()
intents.members = True


TOKEN = os.getenv('DISCORD_TOKEN')
print(f"O TOKEN É {TOKEN}")
queues = {}

client = commands.Bot(command_prefix="!", intents=intents)

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


def check_queues(ctx, id, options):
    voice = ctx.guild.voice_client
    if queues[id]:
        source = queues[id].pop(0)
        voice.play(source=source)
    else:
        voice.play(options)


@client.command(pass_context=True)
async def list(ctx):
    await ctx.send(queues)

@client.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        await channel.connect()


@client.command(pass_context = True)
async def play(ctx, url: str):
    if ctx.author.voice:
        voice = get(client.voice_clients, guild=ctx.guild)

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        url_youtube = info['url']

        options = FFmpegPCMAudio(url_youtube, **FFMPEG_OPTIONS)
        voice.play(options, after=lambda x=None: check_queues(ctx,
                                                              ctx.message.guild.id,
                                                              options))
        voice.is_playing()
        await ctx.send('Bot está tocando!')


@client.command(pass_context = True)
async def queue(ctx, url):
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
    url_youtube = info['url']

    source = FFmpegPCMAudio(url_youtube, **FFMPEG_OPTIONS)

    guild_id = ctx.message.guild.id

    if guild_id in queues:
        queues[guild_id].append(source)
    else:
        queues[guild_id] = [source]

    await ctx.send("Sua música foi adicionado a fila")


@client.command()
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        voice.resume()
        await ctx.send('Bot volta a tocar.')


@client.command()
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause()
        await ctx.send('Bot está sendo pausado.')


@client.command()
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.stop()
        await ctx.send('Parando o bot.')


@client.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)
    await ctx.send("Mensagens estão sendo apagadas deste canal.")


client.run(TOKEN)