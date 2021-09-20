from discord.ext.commands import CommandError


class QueueIsEmpty(CommandError):
    pass


class AlredyConnectedToChannel(CommandError):
    pass


class NoVoiceChannel(CommandError):
    pass


class NotTracksFound(CommandError):
    pass


class PlayerIsAlreadyPaused(CommandError):
    pass


class PlayerIsAlreadyPlaying(CommandError):
    pass


class NoMoreTracks(CommandError):
    pass


class NoPreviousTracks(CommandError):
    pass
