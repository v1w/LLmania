try:

    import pyglet
    import os
    import sys
    import json

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
    # 用songfile来判断有没有歌，以及是否有相应的btm
    songfiles = []
    btms = []
    invalid_songs = []
    scan = [i for i in os.walk('./resources/')]
    for parent, dirnames, filenames in scan:
        if parent == './resources/beatmap':
            btms_ = filenames
        if parent == './resources/song':
            songfiles_ = filenames

    for btm in btms_:
        if btm[-4:] == '.btm':
            btms.append(btm)
    for songfile in songfiles_:
        if songfile[-4:] in ['.mp3', '.ogg', '.wav']:
            songfiles.append(songfile)

    for songfile in songfiles:
        if (songfile.split('.')[0] + '.btm') not in btms:
            invalid_songs.append(songfile)
    for invalid_song in invalid_songs:
        songfiles.remove(invalid_song)
    return songfiles, btms


try:

    speed = 0
    offset = 0
    print('======LLSIF emulator======\nVersion: Alpha 1\nAuthor: vincent.w\nCompiled: 2016.9.13')
    print('==========================')
    sys.stdout.write('Loading resources..')
    os.chdir(os.path.dirname(sys.argv[0]))
    pyglet.resource.path = ['./resources']
    pyglet.resource.reindex()

    try:

        # 加载config文件，如果不存在就创建
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
