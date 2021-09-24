import re
import typing as t
import discord
import wavelink
import os

from dotenv import load_dotenv
from discord.ext import commands
from constants import URL_REGEX
from . import player
from errors.exceptions import AlredyConnectedToChannel, NoVoiceChannel, \
    QueueIsEmpty, PlayerIsAlreadyPaused, PlayerIsAlreadyPlaying, \
    NoMoreTracks, NoPreviousTracks
from embeds.embeds_queue_command import EmbedQueueCommand

load_dotenv()
LAVALINK_HOST = os.getenv('LAVALINK_HOST')
LAVALINK_URL = os.getenv('LAVALINK_URL')
SECURE = os.getenv("SECURE")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD")
LAVALINK_PORT = int(os.getenv("LAVALINK_PORT"))
LAVALINK_IDENTIFIER = os.getenv("LAVALINK_IDENTIFIER")
LAVALINK_REGION = os.getenv("LAVALINK_REGION")

print(f"{LAVALINK_HOST}")
print(f"{LAVALINK_URL}")
print(f"{SECURE}")
print(f"{LAVALINK_PASSWORD}")
print(f"{LAVALINK_PORT}")
print(f"{LAVALINK_IDENTIFIER}")
print(f"{LAVALINK_REGION}")


class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot):
        self.bot = bot
        self.wavelink = wavelink.Client(bot=self.bot)
        self.bot.loop.create_task(self.start_nodes())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await self.get_player(member.guild).teardown()

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node):
        print(f"Wavelink node {node.identifier} ready.")

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node, payload):
        await payload.player.advance()

    @wavelink.WavelinkMixin.listener("on_websocket_closed")
    async def on_websocket_closed(self, node, payload):
        self.bot.loop.create_task(self.start_nodes())

    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Os comandos de música não estão disponíveis em "
                           "DMs.")
            return False
        return True

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        nodes = {
            "MAIN": {
                "host": LAVALINK_HOST,
                "port": int(LAVALINK_PORT),
                "rest_uri": LAVALINK_URL,
                "password": LAVALINK_PASSWORD,
                "identifier": LAVALINK_IDENTIFIER,
                "region": LAVALINK_REGION,
            }
        }

        for node in nodes.values():
            await self.wavelink.initiate_node(**node)

    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=player.Player,
                                            context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=player.Player)

    @commands.command(name="connect", aliases=["join"])
    async def connect_command(self, ctx, *,
                              channel: t.Optional[discord.VoiceChannel]):
        player = self.get_player(ctx)
        channel = await player.connect(ctx, channel)
        await ctx.send(f"Conectado a {channel.name}.")

    @connect_command.error
    async def connect_command_error(self, ctx, exc):
        if isinstance(exc, AlredyConnectedToChannel):
            await ctx.send("Já conectado a um canal de voz.")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("Nenhum canal de voz adequado foi fornecido.")

    @commands.command(name="disconnect", aliases=["leave"])
    async def disconnect_command(self, ctx):
        player = self.get_player(ctx)
        await player.teardown()
        await ctx.send("Desconectado")

    @commands.command(name="play")
    async def play_command(self, ctx, *, query: t.Optional[str]):
        try:
            player = self.get_player(ctx)
        except wavelink.errors.ZeroConnectedNodes:
            await self.bot.loop.create_task(self.start_nodes())
            player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx)

        if query is None:
            if player.queue.is_empty:
                raise QueueIsEmpty

            await player.set_pause(False)
            await ctx.send("O player está voltando a tocar.")

        else:
            query = query.strip("<>")
            if not re.match(URL_REGEX, query):
                query = f"ytsearch:{query}"
            teste = await self.wavelink.get_tracks(query)
            await player.add_tracks(ctx, teste)

    @play_command.error
    async def play_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPlaying):
            await ctx.send("Player já está tocando.")
        elif isinstance(exc, QueueIsEmpty):
            await ctx.send("Não há mais músicas para tocar")

    @commands.command(name="queue")
    async def queue_command(self, ctx, *, show: t.Optional[int] = 10):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        embed_queue_command = EmbedQueueCommand(
            ctx=ctx,
            player=player,
            show=show
        )
        msg = await embed_queue_command.send_embed()
        print(msg)

    @queue_command.error
    async def queue_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("A fila atualmente está vazia.")

    @commands.command(name="pause")
    async def pause_command(self, ctx):
        player = self.get_player(ctx)

        if player.is_paused:
            raise PlayerIsAlreadyPaused

        await player.set_pause(True)
        await ctx.send("O player foi pausado")

    @commands.command(name="stop")
    async def stop_command(self, ctx):
        player = self.get_player(ctx)

        player.queue.empty()
        await player.stop()

        await ctx.send("O player foi parou")

    @commands.command(name="next", aliases=["skip"])
    async def next_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.upcoming:
            player.queue.clean_queue()
            raise NoMoreTracks

        await player.stop()
        await ctx.send("Tocando a proxima música da fila")

    @commands.command(name="previous")
    async def previous_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.history:
            raise NoPreviousTracks

        player.queue.position -= 2
        await player.stop()
        await ctx.send("Tocando a música anterior da fila")

    @next_command.error
    async def next_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("A fila já está vazia, não há próxima música.")
        elif isinstance(exc, NoMoreTracks):
            await ctx.send("Não a nenhuma música após essa na fila.")

    @previous_command.error
    async def previous_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("A fila já está vazia, não há próxima música.")
        elif isinstance(exc, NoPreviousTracks):
            await ctx.send("Não a nenhuma música na fila.")

    @pause_command.error
    async def pause_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send("O player já está pausado")

    async def on_error(self, err, *args, **kwargs):
        raise

    async def on_commanderror(self, ctx, exc):
        raise setattr(exc, "original", exc)


def setup(bot):
    bot.add_cog(Music(bot))
