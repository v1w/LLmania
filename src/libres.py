try:

    import sys
    import os
    import json
    import pyglet

except Exception as e:
    print('Error 20003')
    raise SystemExit


def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2


def parse_btm(btm):
    notes = []
    with open('./resources/beatmap/' + btm) as f:
        raw = json.loads(f.read())['lane']
        for lane in raw:
            tmp = []
            for note in lane:
                tmp.append([note['starttime'], note['endtime'] - note['starttime']])
            notes.append(tmp)
    return notes


def load_song(songfile):
    song = pyglet.resource.media("song/" + songfile, streaming=True)
    return song


def scan():
    """Use parameter song_file to check song and beat map existence"""
    song_files = []
    btms = []
    btms_ = []
    song_files_ = []
    invalid_songs = []
    scan_ = [i for i in os.walk('./resources/')]
    for parent, dir_names, file_names in scan_:
        if parent == './resources/beatmap':
            btms_ = file_names
        if parent == './resources/song':
            song_files_ = file_names

    for btm in btms_:
        if btm[-4:] == '.btm':
            btms.append(btm)
    for song_file in song_files_:
        if song_file[-4:] in ['.mp3', '.ogg', '.wav']:
            song_files.append(song_file)

    for song_file in song_files:
        if (song_file.split('.')[0] + '.btm') not in btms:
            invalid_songs.append(song_file)
    for invalid_song in invalid_songs:
        song_files.remove(invalid_song)
    return song_files, btms


try:

    speed = 0
    offset = 0
    print('======LLSIF emulator======\nAuthor: v1w\nWebsite: github.com/v1w/SIFemu')
    print('==========================')
    sys.stdout.write('Loading resources..')
    os.chdir(os.path.dirname(sys.argv[0]))
    pyglet.resource.path = ['./resources']
    pyglet.resource.reindex()
    pyglet.font.add_file('./resources/asset/Acens.ttf')
    font = pyglet.font.load('Acens')
    try:

        # Load config
        with open('./config') as f:
            conf = json.loads(f.read())
        speed = conf['speed']
        offset = conf['offset']

    except FileNotFoundError:
        speed = 0.4
        offset = -250
        # speed = 0.85
        # offset = -110
        conf = {'speed': speed, 'offset': offset}
        json.dump(conf, open('./config', 'w'))

    p_sound = pyglet.resource.media("asset/perfect.mp3", streaming=False)
    gr_sound = pyglet.resource.media("asset/great.mp3", streaming=False)
    g_sound = pyglet.resource.media("asset/good.mp3", streaming=False)
    # b_sound = pyglet.resource.media("asset/bad.mp3", streaming=False)

    background = pyglet.resource.image("asset/background.jpg")
    center_image(background)

    p_label = pyglet.resource.image("asset/perfect.png")
    center_image(p_label)
    gr_label = pyglet.resource.image("asset/great.png")
    center_image(gr_label)
    g_label = pyglet.resource.image("asset/good.png")
    center_image(g_label)
    b_label = pyglet.resource.image("asset/bad.png")
    center_image(b_label)
    m_label = pyglet.resource.image("asset/miss.png")
    center_image(m_label)
    print('OK')

except Exception as e:
    print('Error 20001')
    # print(e)
    raise SystemExit

if __name__ == '__main__':
    pass
