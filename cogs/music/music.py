import re
import typing as t
import discord
import wavelink

from discord.ext import commands
from constants import URL_REGEX
from . import player
from errors.exceptions import AlredyConnectedToChannel, NoVoiceChannel, \
    QueueIsEmpty
from embeds.embeds_queue_command import EmbedQueueCommand


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
                "host": "127.0.0.1",
                "port": 2333,
                "rest_uri": "http://127.0.0.1:2333",
                "password": "youshallnotpass",
                "identifier": "MAIN",
                "region": "europe",
                "secure": False
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
        player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx)

        if query is None:
            pass

        else:
            query = query.strip("<>")
            if not re.match(URL_REGEX, query):
                query = f"ytsearch:{query}"

            await player.add_tracks(ctx, await self.wavelink.get_tracks(query))

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

    async def on_error(self, err, *args, **kwargs):
        raise

    async def on_commanderror(self, ctx, exc):
        raise setattr(exc, "original", exc)


def setup(bot):
    bot.add_cog(Music(bot))
