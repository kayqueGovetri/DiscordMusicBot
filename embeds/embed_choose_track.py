from discord import Embed
from datetime import datetime


class EmbedChooseTrack:
    def __init__(self, ctx, tracks):
        self.ctx = ctx
        self.tracks = tracks

    async def send_embed(self):
        embed = Embed(
            title="Escolha a música",
            description="\n".join(
                f"**{i + 1}.** {t.title} "
                f"({t.length // 60000}:{str(t.length % 60).zfill(2)})"
                for i, t in enumerate(self.tracks[:5])
            ),
            colour=self.ctx.author.colour,
            timestamp=datetime.utcnow(),
        )

        embed.set_author(name="Resultados da pesquisa")
        embed.set_footer(
            text=f"Invocado pelo {self.ctx.author.display_name}",
            icon_url=self.ctx.author.avatar_url,
        )
        msg = await self.ctx.send(embed=embed)

        return msg
