try:

    import pyglet

    # for pyinstaller to recognize avbin
    pyglet.lib.load_library('avbin')
    pyglet.have_avbin = True
    from pyglet.gl import *
    import libres
    import time
    import traceback

except Exception as e:
    print('Error 20004')
    # traceback.print_exc()
    raise SystemExit


def draw_rect(centerx, bottomy, width, height, r, g, b):
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glColor3f(r, g, b)
    glRectf(centerx - width / 2.0, bottomy, centerx - width / 2.0 + width, bottomy + height)
    glFlush()


class GameWindow(pyglet.window.Window):
    def __init__(self, offset, speed, notes, music_start, auto_flag, caption):
        super(GameWindow, self).__init__(vsync=True, width=800, height=600, caption=caption)
        # pyglet.clock.set_fps_limit(60)
        self.notes = notes
        self.offset = offset
        self.speed = speed
        self.music_start = music_start
        self.auto = auto_flag
        self.judge_pos = 100
        # 底部蓝线的timing
        self.judge_time = self.judge_pos / self.speed
        self.lanes = [i for i in range(0, 9)]
        self.lanepos = [i for i in range(100, 750, 75)]
        # 不能用[0]*9,否则九个元素指向同一片内存地址
        self.curnote_time = 0
        self.curnote = []
        self.lanepressed = [0 for i in range(0, 9)]
        # 0表示没有按下，1表示p, 2表示gr
        self.lanepressed_long = [False for i in range(0, 9)]
        # 长条是否按下(保持)
        self.pressing_note_long = [[] for i in range(0,9)]
        # 当前处于按下状态的note
        self.dt = 0
        # note 距离perfect点的距离 in ms
        self.score = 0
        self.combo = 0
        self.fps_display = pyglet.clock.ClockDisplay()

        self.background = pyglet.sprite.Sprite(img=libres.background, x=400, y=300)
        self.p_score = 573
        self.gr_score = 333
        self.g_score = 150
        self.p_label = pyglet.sprite.Sprite(img=libres.p_label, x=400, y=400)
        self.gr_label = pyglet.sprite.Sprite(img=libres.gr_label, x=400, y=400)
        self.g_label = pyglet.sprite.Sprite(img=libres.g_label, x=400, y=400)
        self.score_label = pyglet.text.Label(text="Score: 0", x=400, y=575, anchor_x='center')
        self.combo_label = pyglet.text.Label(text="0 combo", x=400, y=350, anchor_x='center')

    def on_draw(self):
        self.clear()
        self.score_label.text = "Score: %d" % self.score
        self.combo_label.text = "%d combo" % self.combo
        #self.background.draw()
        self.score_label.draw()
        self.combo_label.draw()
        self.fps_display.draw()
        draw_rect(400, self.judge_pos, 800.0, 2.0, 1, 0, 0)
        for i in self.lanes:
            draw_rect(self.lanepos[i], self.judge_pos-10, 40, 20.0, 1, 0, 0)

        for lane in self.lanes:
            for note in self.notes[lane]:
                if note[0] + note[1] - self.dt - self.offset >= 0:
                    # note未出下边界
                    if (note[0] - self.dt - self.offset) * self.speed <= 600:
                        # note 进入上边界

                        self.curnote_time = note[0] - self.dt - self.offset
                        pos_y = self.curnote_time * self.speed
                        # 当前note的剩余时间, 高度
                        self.curnote = note[:]
                        # 当前的note,浅复制
                        if self.auto:
                            self.autoplay(lane)
                        if note[1] == 0:
                            # 是单键,画出单键
                            draw_rect(self.lanepos[lane], pos_y, 40.0, 10.0, 1, 1, 1)
                            if self.lanepressed[lane]:
                                self.judge_score(self.lanepressed, lane)
                                self.notes[lane].remove(self.curnote)
                                self.lanepressed[lane] = 0

                        else:

                            # 是长条
                            if self.lanepressed[lane] and not self.lanepressed_long[lane]:

                                # 第一次按下，且未miss
                                draw_rect(self.lanepos[lane], pos_y, 40.0, note[1] * self.speed, 1, 1, 0)
                                self.judge_score(self.lanepressed, lane)
                                self.lanepressed_long[lane] = True
                                self.lanepressed[lane] = 0
                                self.pressing_note_long[lane] = note[:]
                            elif self.lanepressed_long[lane] and note == self.pressing_note_long[lane]:
                                # 已经按下过,且本循环的note是上个循环判断的note
                                self.lanepressed[lane] = 0
                                time_remain = note[0] + note[1] - self.dt - self.offset - self.judge_time
                                if time_remain > 0:
                                    # 保证不反向
                                    draw_rect(
                                        self.lanepos[lane], self.judge_pos, 40.0, time_remain * self.speed, 1, 1, 0)
                                    draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
                                else:
                                    # 长条结束，删除长条
                                    self.notes[lane].remove(note)
                                    self.combo += 1
                                    libres.p_sound.play()
                                    draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 0, 1, 0)
                                    self.p_label.draw()
                                    self.lanepressed_long[lane] = False
                            else:
                                # miss
                                draw_rect(self.lanepos[lane], pos_y, 40.0, note[1] * self.speed, 1, 1, 1)
                                self.lanepressed[lane] = 0

                    else:
                        break
                else:
                    continue
    '''
    def on_key_press(self, key, modifiers):
        """Action upon key press, raise interrupt, modify self.lanepressed"""
        p_timing = 30
        gr_timing = 50
        g_timing = 70

        def key_action(lane):
            if abs(self.curnote_time[lane] - self.judge_time) <= p_timing:
                if self.curnote[lane][1] == 0:
                    self.curnote_time[lane] = 0
                self.lanepressed[lane] = [True, 0]
            elif abs(self.curnote_time[lane] - self.judge_time) <= gr_timing:
                if self.curnote[lane][1] == 0:
                    self.curnote_time[lane] = 0
                self.lanepressed[lane] = [True, 1]
            elif abs(self.curnote_time[lane] - self.judge_time) <= g_timing:
                if self.curnote[lane][1] == 0:
                    self.curnote_time[lane] = 0
                self.lanepressed[lane] = [True, 2]

        if key == pyglet.window.key.A:
            key_action(0)
        if key == pyglet.window.key.S:
            key_action(1)
        if key == pyglet.window.key.D:
            key_action(2)
        if key == pyglet.window.key.F:
            key_action(3)
        if key == pyglet.window.key.G:
            key_action(4)
        if key == pyglet.window.key.H:
            key_action(5)
        if key == pyglet.window.key.J:
            key_action(6)
        if key == pyglet.window.key.K:
            key_action(7)
        if key == pyglet.window.key.L:
            key_action(8)
    '''
    def judge_score(self, lanepressed, lane):
        """none"""
        try:
            draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
            # 得分特效
            if lanepressed[lane] == 1:
                self.p_label.draw()
                self.score += self.p_score
                self.combo += 1
                libres.p_sound.play()
            elif lanepressed[lane] == 2:
                self.gr_label.draw()
                self.score += self.gr_score
                self.combo += 1
                libres.gr_sound.play()
            elif lanepressed[lane] == 3:
                self.g_label.draw()
                self.score += self.g_score
                self.combo = 0
                libres.g_sound.play()

        except ValueError:
            pass

    def autoplay(self, lane):
        if abs(self.curnote_time - self.judge_time) <= 15:
            self.lanepressed[lane] = 1

    def update(self, dt):
        self.dt = int(time.time() * 1000) - self.music_start
        if self.dt > 180000:
            self.on_close()


def play():
    global auto_flag
    try:
        songnum = ''
        banner = ''
        songfiles, btms = libres.scan()
        for i in range(0, len(songfiles)):
            banner += '[' + str(i + 1) + '] ' + songfiles[i].split('.')[0] + '\n'
        banner += 'Select Song No.: '

        while True:
            songnum = str(input(banner))
            if songnum.isdigit():
                songnum = int(songnum)
                songnum += -1
                if songnum in range(0, len(songfiles)):
                    break
                else:
                    print('-----Song does not exist-----\n\n')
        song = libres.load_song(songfiles[songnum])
        player = pyglet.media.Player()
        player.queue(song)
        notes = libres.parse_btm(btms[songnum])

        print('-----Selected [%s]-----' % (songfiles[songnum].split('.')[0]))
        while True:
            auto_flag = str(input('Auto?(Y/N): '))
            if auto_flag == 'Y' or auto_flag == 'y' or auto_flag == '\n':
                auto_flag = True
                break
            elif auto_flag == 'N' or auto_flag == 'n':
                auto_flag = False
                break

        player.play()
        music_start = int(time.time() * 1000)  # 音乐开始时间in ms
        window = GameWindow(offset=libres.offset, speed=libres.speed, notes=notes, music_start=music_start,
                            auto_flag=auto_flag, caption=songfiles[songnum].split('.')[0])
        pyglet.clock.schedule_interval(window.update, 1 / 200)
        pyglet.app.run()

    except Exception as e:
        print('Error 20002')
        traceback.print_exc()
        raise SystemExit


if __name__ == '__main__':
    play()
