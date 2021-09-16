from discord.ext.commands import CommandError


class QueueIsEmpty(CommandError):
    pass


class AlredyConnectedToChannel(CommandError):
    pass


class NoVoiceChannel(CommandError):
    pass


class NotTracksFound(CommandError):
    pass
