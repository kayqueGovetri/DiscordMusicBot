import asyncio

from constants import OPTIONS


class EmojisChooseTrack:
    def __init__(self, msg, ctx, bot):
        self.msg = msg
        self.bot = bot
        self.ctx = ctx

    def _check(self, r, u):
        return (
            r.emoji in OPTIONS.keys()
            and u == self.ctx.author
            and r.message.id == self.msg.id
        )

    async def set_emojis(self, tracks: list):
        for emoji in list(OPTIONS.keys())[: min(len(tracks), len(OPTIONS))]:
            await self.msg.add_reaction(emoji)
        try:
            reaction, _ = await self.bot.wait_for(
                "reaction_add", timeout=60.0, check=self._check
            )
        except asyncio.TimeoutError:
            await self.ctx.message.delete()
        else:
            return tracks[OPTIONS[reaction.emoji]]
        finally:
            await self.msg.delete()
