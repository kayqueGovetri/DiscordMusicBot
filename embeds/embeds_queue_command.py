from discord import Embed
from datetime import datetime


class EmbedQueueCommand:
    def __init__(self, ctx, show, player):
        self.ctx = ctx
        self.show = show
        self.player = player

    async def send_embed(self):
        embed = Embed(
            title="Queue",
            description=f"Mostrando as proximas musicas. {self.show} ",
            colour=self.ctx.author.colour,
            timestamp=datetime.utcnow()
        )
        display_name = self.ctx.author.display_name
        avatar_url = self.ctx.author.avatar_url
        if self.player.queue.current_track:
            current_track_title = self.player.queue.current_track.title
        else:
            current_track_title = "Não está tocando nenhuma música."

        queue_upcoming = self.player.queue.upcoming

        embed.set_author(name="Resultado da pesquisa")
        embed.set_footer(
            text=f"Chamado por {display_name}",
            icon_url=avatar_url
        )
        embed.add_field(
            name="Tocando agora",
            value=current_track_title,
            inline=False
        )
        if upcoming := queue_upcoming:
            embed.add_field(
                name="Proximos",
                value="\n".join(t.title for t in upcoming[:self.show]),
                inline=False
            )
        msg = await self.ctx.send(embed=embed)
        return msg
