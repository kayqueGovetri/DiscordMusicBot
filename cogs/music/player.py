import wavelink

from embeds.embed_choose_track import EmbedChooseTrack
from .queue import Queue
from errors.exceptions import AlredyConnectedToChannel, NoVoiceChannel, \
    QueueIsEmpty, NotTracksFound
from emojis.emojis_choose_track import EmojisChooseTrack


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()

    async def connect(self, ctx, channel=None):
        if self.is_connected:
            raise AlredyConnectedToChannel

        if (channel := getattr(ctx.author.voice, "channel", channel)) is None:
            raise NoVoiceChannel

        await super().connect(channel.id)
        return channel

    async def teardown(self):
        try:
            await self.destroy()
        except KeyError:
            pass

    async def add_tracks(self, ctx, tracks):
        print(tracks)
        if not tracks:
            raise NotTracksFound
        if isinstance(tracks, wavelink.TrackPlaylist):
            self.queue.add(*tracks.tracks)
        elif len(tracks) == 1:
            self.queue.add(tracks[0])
            await ctx.send(f"Adicionado {tracks[0].title} a fila.")
        else:
            track = tracks[0]
            if (track != await self.choose_track(ctx, tracks)) is not None:
                self.queue.add(track)
                await ctx.send(f"Adicionado {track.title} na fila.")

        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()

    async def choose_track(self, ctx, tracks):
        embed_choose_track = EmbedChooseTrack(ctx=ctx, tracks=tracks)
        msg = await embed_choose_track.send_embed()
        emojis_choose_track = EmojisChooseTrack(msg=msg, ctx=ctx, bot=self.bot)
        await emojis_choose_track.set_emojis(tracks=tracks)

    async def start_playback(self):
        await self.play(self.queue.first_track)

    async def advance(self):
        try:
            if (track := self.queue.get_next_track()) is not None:
                await self.play(track)
        except QueueIsEmpty:
            pass
