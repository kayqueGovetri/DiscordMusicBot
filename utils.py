from random import shuffle
from discord import FFmpegPCMAudio
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


def shuffle_names(list_names):
    list_shuffle = list_names.split(" ")
    shuffle(list_shuffle)
    return " ".join(list_shuffle)

