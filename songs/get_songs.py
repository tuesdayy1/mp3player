import os


def get_song(name):
    len_song = len([i for i in name])
    len_s = len([i for i in os.path.join(os.getcwd(), name)])
    song = os.path.join(os.getcwd(), name)[:len_s - len_song]
    return song + rf'songs\{name}'


print(get_song('Nov.mp3'))

