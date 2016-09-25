try:

    import sys
    import os
    import json
    import time
    import pyglet
    import gamewindow
    # import traceback

except Exception as e:
    print('Error 20003')
    # print(e)
    raise SystemExit


def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2


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
        if (song_file[:-4] + '.btm') not in btms:
            invalid_songs.append(song_file)
    for invalid_song in invalid_songs:
        song_files.remove(invalid_song)
    return song_files, btms


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


class RhythmAdjust(gamewindow.GameWindow):
    def __init__(self):
        super(RhythmAdjust, self).__init__(offset=-250, speed=0.4, song=setup_s, notes=setup_n,
                                          is_auto=False, caption='Rhythm Adjust', hit_banners_sounds=hit_banners_sounds)
        self.player.eos_action = pyglet.media.Player.EOS_LOOP
        self.speed_up = False
        self.speed_down = False
        self.offset_up = False
        self.offset_down = False
        self.speed_label = pyglet.text.Label(text="Speed: 0", x=20, y=self.height-30, anchor_x='left',
                                             font_name='Acens')
        self.offset_label = pyglet.text.Label(text="Offset: 0", x=20, y=self.height - 60, anchor_x='left',
                                             font_name='Acens')
        self.hint = ["Speed: Arrow key UP/DOWN", "Offset: Arrow key LEFT/RIGHT", "Reset: R", "Confirm: ENTER"]
        self.hint_labels = []
        for i in range(0, 4):
            self.hint_labels.append(pyglet.text.Label(text=self.hint[i], x=20, y=self.height - 90 - i*30, anchor_x='left'))
        self.lastnote = []
        self.confirm_label = pyglet.text.Label(text="Config CONFIRMED. Please close this window.",
                                               x=self.width/2, y=self.height/2, anchor_x='center', color=(255,0,0,255))
        self.is_confirmed = False

    def on_draw(self):
        self.clear()
        if self.is_confirmed:
            self.confirm_label.draw()
        self.speed_label.text = "Speed: %.2f" % self.speed
        self.offset_label.text = "Offset: %s" % self.offset
        self.speed_label.draw()
        self.offset_label.draw()
        for label in self.hint_labels:
            label.draw()
        self.gl_draw_rect(self.center[0], 95, self.width, self.note_height, self.JUDGE_COLOR)
        for note in self.notes:
            if note[0] - self.dt - self.offset >= 0:
                if (note[0] - self.dt - self.offset) * self.speed <= self.height:
                    self.cur_note_time = note[0] - self.dt - self.offset
                    self.pos_y = self.cur_note_time * self.speed
                    self.gl_draw_rect(self.lane_pos[4], self.pos_y, self.note_width, self.note_height,
                                      self.NOTE_COLOR)
                    if self.cur_note_time - self.judge_time < 10 and note != self.lastnote:
                        hit_banners_sounds['sound'][0].play()
                        self.lastnote = note[:]
            else:
                self.notes.pop(0)
                # print(len(self.notes))

    def on_key_press(self, key, modifiers):
        if key == pyglet.window.key.UP:
            self.speed_up = True
        if key == pyglet.window.key.DOWN:
            self.speed_down = True
        if key == pyglet.window.key.LEFT:
            self.offset_up = True
        if key == pyglet.window.key.RIGHT:
            self.offset_down = True
        if key == pyglet.window.key.R:
            self.offset = -250
            self.speed = 0.4
        if key == pyglet.window.key.ENTER:
            self.is_confirmed = True
            conf = {'speed': self.speed, 'offset': self.offset}
            json.dump(conf, open('./config', 'w'))

    def on_key_release(self, key, modifiers):
        if key == pyglet.window.key.UP:
            self.speed_up = False
        if key == pyglet.window.key.DOWN:
            self.speed_down = False
        if key == pyglet.window.key.LEFT:
            self.offset_up = False
        if key == pyglet.window.key.RIGHT:
            self.offset_down = False

    def update(self, dt):
        self.dt = int(time.time() * 1000) - self.music_start
        if self.speed_up:
            self.speed += 0.01
        elif self.speed_down and self.speed > 0.01:
            self.speed -= 0.01
        if self.offset_up:
            self.offset += 3
        elif self.offset_down:
            self.offset -= 3

try:

    speed = 0
    offset = 0
    print('======LLSIF emulator======\nAuthor: v1w\nWebsite: github.com/v1w/SIFemu')
    print('==========================')
    #sys.stdout.write('Loading asset..\n')
    os.chdir(os.path.dirname(sys.argv[0]))
    pyglet.resource.path = ['./resources']
    pyglet.resource.reindex()
    pyglet.font.add_file('./resources/asset/Acens.ttf')
    font = pyglet.font.load('Acens')

    p_sound = pyglet.resource.media("asset/perfect.mp3", streaming=False)
    gr_sound = pyglet.resource.media("asset/great.mp3", streaming=False)
    g_sound = pyglet.resource.media("asset/good.mp3", streaming=False)
    setup_s = pyglet.resource.media("asset/setup.wav", streaming=False)
    setup_n = [[i, i] for i in range(0, 353 * 1200, 353*3)]
    # notes and sound used in setup
    # b_sound = pyglet.resource.media("asset/bad.mp3", streaming=False)

    background = pyglet.resource.image("asset/background.jpg")
    center_image(background)

    p_img = pyglet.resource.image("asset/perfect.png")
    center_image(p_img)
    gr_img = pyglet.resource.image("asset/great.png")
    center_image(gr_img)
    g_img = pyglet.resource.image("asset/good.png")
    center_image(g_img)
    b_img = pyglet.resource.image("asset/bad.png")
    center_image(b_img)
    m_img = pyglet.resource.image("asset/miss.png")
    center_image(m_img)

    hit_banners_sounds = {'img': [p_img, gr_img, g_img, b_img, m_img], 'sound': [p_sound, gr_sound, g_sound]}

    try:

        # Load config
        with open('./config') as f:
            conf = json.loads(f.read())
        speed = conf['speed']
        offset = conf['offset']

    except Exception:
        # Initialize
        is_init = False
        while True:
            is_init = input('I found no valid config, start first time adjustment?(Y/N)')
            if is_init == 'Y' or is_init == 'y' or is_init == '':
                is_init = True
                break
            elif is_init == 'N' or is_init == 'n':
                is_init = False
                break
        if not is_init:
            print('Loaded default config:\nspeed: 0.4\noffset: -250')
            speed = 0.4
            offset = -250
            # speed = 0.85
            # offset = -110
            conf = {'speed': speed, 'offset': offset}
            json.dump(conf, open('./config', 'w'))
        else:
            RhythmAdjust()
            pyglet.app.run()
            try:
                with open('./config') as f:
                    conf = json.loads(f.read())
                speed = conf['speed']
                offset = conf['offset']
            except FileNotFoundError:
                print('Setup Failed.')
                raise SystemExit

except Exception as e:
    print('Error 20001')
    # print(e)
    # traceback.print_exc()
    raise SystemExit

if __name__ == '__main__':
    RhythmAdjust()
    pyglet.app.run()

