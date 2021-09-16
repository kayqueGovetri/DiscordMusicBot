from discord.ext import commands
from cogs.music.music import Music


class Bot(commands.Bot):
    def __init__(self):
        super(Bot, self).__init__(command_prefix=['!'])
        self.add_cog(Music(self))
        self.client_id = None

    async def on_ready(self):
        self.client_id = (await self.application_info()).id
        print("O bot está pronto!")
        print(f'Logado como username: {self.user.name} | id: {self.user.id}')

    async def close(self):
        print("Fechando na interrupção do teclado...")
        await self.shutdown()

    async def on_connect(self):
        print(f"Conectado ao Discord (latência: {self.latency*1000:,.0f} ms).")
        print(self.get_all_channels())

    async def on_resumed(self):
        print("O bot foi retomado.")

    async def prefix(self, bot, msg):
        return commands.when_mentioned_or("+")(bot, msg)

    async def on_error(self, err, *args, **kwargs):
        raise

    async def on_command_error(self, context, exception):
        raise getattr(exception, "original", exception)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=commands.Context)

        if ctx.command is not None:
            await self.invoke(ctx)

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)
