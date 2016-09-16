try:

    import pyglet
    pyglet.lib.load_library('avbin')
    pyglet.have_avbin = True
    # for pyinstaller to recognize avbin
    from pyglet.gl import *
    import libres
    import time
    # import traceback

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

    def __init__(self, offset, speed, song, notes, auto_flag, caption):
        super(GameWindow, self).__init__(vsync=True, width=800, height=600, caption=caption)
        # pyglet.clock.set_fps_limit(60)
        self.song = song
        self.notes = notes
        self.offset = offset
        self.speed = speed
        self.auto_flag = auto_flag
        self.judge_pos = 100
        self.judge_time = self.judge_pos / self.speed
        # timing of the judge line
        self.lanes = [i for i in range(0, 9)]
        self.lanepos = [i for i in range(100, 750, 75)]
        self.cur_note_time = 0
        self.cur_note = []
        self.pos_y = 0
        self.lanepressed = [False for i in range(0, 9)]
        # the lane is pressed or not
        self.time_remain_long = 0
        self.lanepressed_long = [False for i in range(0, 9)]
        # long note is hold pressed or not
        self.pressing_note_long = [[] for i in range(0, 9)]
        # the long note being currently pressed
        self.missed_notes = []
        self.dt = 0
        # music played time
        self.score = 0
        self.combo = 0
        self.fps_display = pyglet.clock.ClockDisplay()

        self.background = pyglet.sprite.Sprite(img=libres.background, x=400, y=300)
        self.p_timing = 30
        self.gr_timing = 60
        self.g_timing = 80
        self.b_timing = 100
        self.timing_limit = 300
        self.p_score = 573
        self.gr_score = 333
        self.g_score = 150
        self.b_score = 70
        self.p_label = pyglet.sprite.Sprite(img=libres.p_label, x=400, y=400)
        self.gr_label = pyglet.sprite.Sprite(img=libres.gr_label, x=400, y=400)
        self.g_label = pyglet.sprite.Sprite(img=libres.g_label, x=400, y=400)
        self.b_label = pyglet.sprite.Sprite(img=libres.b_label, x=400, y=400)
        self.m_label = pyglet.sprite.Sprite(img=libres.m_label, x=400, y=400)
        self.score_label = pyglet.text.Label(text="Score: 0", x=400, y=575, anchor_x='center', font_name = 'Acens')
        self.combo_label = pyglet.text.Label(text="0 combo", x=400, y=350, anchor_x='center', font_name = 'Acens')

        if not self.auto_flag:
            def auto_play(*args):
                pass
            GameWindow.auto_play = auto_play

        player = pyglet.media.Player()
        player.queue(self.song)
        player.play()
        self.music_start = int(time.time() * 1000)
        # music start time in ms
        self.music_duration = int(self.song.duration * 1000)

        pyglet.clock.schedule_interval(self.update, 1 / 200)

    def on_draw(self):
        self.clear()
        self.score_label.text = "Score: %d" % self.score
        self.combo_label.text = "%d combo" % self.combo
        if self.combo >= 800:
            self.combo_label.color = (255, 0, 255, 250)
        elif self.combo >= 500:
            self.combo_label.color = (0, 255, 255, 250)
            self.combo_label.font_size = 14
        elif self.combo >= 300:
            self.combo_label.color = (255, 0, 0, 220)
            self.combo_label.font_size = 13
        elif self.combo >= 100:
            self.combo_label.color = (255, 255, 0, 200)
            self.combo_label.bold = True
        elif self.combo >= 50:
            self.combo_label.color = (0, 255, 0, 200)
        elif self.combo >= 10:
            self.combo_label.color = (0, 0, 255, 220)
        else:
            self.combo_label.color = (255, 255, 255, 180)
            self.combo_label.bold = False
            self.combo_label.font_size = 12
        # self.background.draw()
        draw_rect(400, self.judge_pos, 800.0, 2.0, 1, 0, 0)
        for i in self.lanes:
            draw_rect(self.lanepos[i], self.judge_pos - 10, 40, 20.0, 1, 0, 0)

        for lane in self.lanes:
            for note in self.notes[lane]:
                if note[0] + note[1] - self.dt - self.offset >= 0:
                    # note is not below window bottom
                    if (note[0] - self.dt - self.offset) * self.speed <= 600:
                        # note is not above window top
                        self.cur_note_time = note[0] - self.dt - self.offset
                        self.pos_y = self.cur_note_time * self.speed
                        # the y position and time to window bottom of the current note
                        self.cur_note = note[:]
                        # the note currently being checked
                        time_diff = self.cur_note_time - self.judge_time
                        # time remaining until judge line
                        self.auto_play(lane)
                        if note[1] == 0:
                            # single note, draw note
                            draw_rect(self.lanepos[lane], self.pos_y, 40.0, 10.0, 1, 1, 1)
                            if self.lanepressed[lane]:
                                self.judge_score_single(abs(time_diff), lane)
                            elif time_diff <= - self.b_timing and note not in self.missed_notes:
                                # miss
                                self.combo = 0
                                self.m_label.draw()
                                self.missed_notes.append(note)

                        else:

                            # long note
                            self.time_remain_long = note[0] + note[1] - self.dt - self.offset - self.judge_time
                            if self.lanepressed[lane] and (not self.lanepressed_long[lane]):
                                # first press, check score
                                self.judge_score_press(abs(time_diff), lane)

                            elif (not self.lanepressed[lane]) and (not self.lanepressed_long[lane]):
                                # not pressed
                                draw_rect(self.lanepos[lane], self.pos_y, 40.0, note[1] * self.speed, 1, 1, 1)

                                if time_diff <= - self.b_timing and note not in self.missed_notes:
                                    # press miss
                                    self.combo = 0
                                    self.m_label.draw()
                                    self.missed_notes.append(note)

                            elif self.lanepressed[lane] and self.lanepressed_long[lane] \
                                    and note == self.pressing_note_long[lane]:
                                # pressing, pressed, the note being checked is the note checked on last frame
                                if self.time_remain_long >= - self.b_timing:
                                    # long note will not go upside down
                                    draw_rect(self.lanepos[lane], self.judge_pos,
                                              40.0, self.time_remain_long * self.speed, 1, 1, 0)
                                    draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
                                else:
                                    # missed release
                                    self.lanepressed_long[lane] = False
                                    self.combo = 0
                                    self.m_label.draw()

                            elif (not self.lanepressed[lane]) and self.lanepressed_long[lane] \
                                    and note == self.pressing_note_long[lane]:
                                # release
                                self.judge_score_release(abs(self.time_remain_long), lane)
                                self.notes[lane].remove(self.cur_note)
                                self.lanepressed_long[lane] = False

                            else:
                                draw_rect(self.lanepos[lane], self.pos_y, 40.0, note[1] * self.speed, 1, 1, 1)

                    else:
                        break
                else:
                    continue
        self.score_label.draw()
        if self.combo != 0:
            self.combo_label.draw()
        self.fps_display.draw()

    def on_key_press(self, key, modifiers):
        """set lanepressed to True on key press"""
        if key == pyglet.window.key.A:
            self.lanepressed[0] = True
        elif key == pyglet.window.key.S:
            self.lanepressed[1] = True
        elif key == pyglet.window.key.D:
            self.lanepressed[2] = True
        elif key == pyglet.window.key.F:
            self.lanepressed[3] = True
        elif key == pyglet.window.key.G:
            self.lanepressed[4] = True
        elif key == pyglet.window.key.H:
            self.lanepressed[5] = True
        elif key == pyglet.window.key.J:
            self.lanepressed[6] = True
        elif key == pyglet.window.key.K:
            self.lanepressed[7] = True
        elif key == pyglet.window.key.L:
            self.lanepressed[8] = True

    def on_key_release(self, key, modifiers):
        """set lanepressed to False on key release"""
        if key == pyglet.window.key.A:
            self.lanepressed[0] = False
        elif key == pyglet.window.key.S:
            self.lanepressed[1] = False
        elif key == pyglet.window.key.D:
            self.lanepressed[2] = False
        elif key == pyglet.window.key.F:
            self.lanepressed[3] = False
        elif key == pyglet.window.key.G:
            self.lanepressed[4] = False
        elif key == pyglet.window.key.H:
            self.lanepressed[5] = False
        elif key == pyglet.window.key.J:
            self.lanepressed[6] = False
        elif key == pyglet.window.key.K:
            self.lanepressed[7] = False
        elif key == pyglet.window.key.L:
            self.lanepressed[8] = False

    def judge_score_single(self, timediff, lane):
        if timediff <= self.p_timing:
            self.p_label.draw()
            draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
            self.score += self.p_score
            self.combo += 1
            libres.p_sound.play()
            self.notes[lane].remove(self.cur_note)
        elif timediff <= self.gr_timing:
            self.gr_label.draw()
            draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
            self.score += self.gr_score
            self.combo += 1
            libres.gr_sound.play()
            self.notes[lane].remove(self.cur_note)
        elif timediff <= self.g_timing:
            self.g_label.draw()
            draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
            self.score += self.g_score
            self.combo = 0
            libres.g_sound.play()
            self.notes[lane].remove(self.cur_note)
        elif timediff <= self.b_timing:
            self.b_label.draw()
            draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
            self.score += self.b_score
            self.combo = 0
            self.notes[lane].remove(self.cur_note)
            # libres.b_sound.play()
        else:
            pass

    def judge_score_press(self, timediff, lane):
        if timediff <= self.p_timing:
            self.p_label.draw()
            draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
            draw_rect(self.lanepos[lane], self.judge_pos, 40.0, self.time_remain_long * self.speed, 1, 1, 0)
            self.score += self.p_score
            libres.p_sound.play()
            self.lanepressed_long[lane] = True
            self.pressing_note_long[lane] = self.cur_note[:]
        elif timediff <= self.gr_timing:
            self.gr_label.draw()
            draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
            draw_rect(self.lanepos[lane], self.judge_pos, 40.0, self.time_remain_long * self.speed, 1, 1, 0)
            self.score += self.gr_score
            libres.gr_sound.play()
            self.lanepressed_long[lane] = True
            self.pressing_note_long[lane] = self.cur_note[:]
        elif timediff <= self.g_timing:
            self.g_label.draw()
            draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
            draw_rect(self.lanepos[lane], self.judge_pos, 40.0, self.time_remain_long * self.speed, 1, 1, 0)
            self.score += self.g_score
            self.combo = 0
            libres.g_sound.play()
            self.lanepressed_long[lane] = True
            self.pressing_note_long[lane] = self.cur_note[:]
        elif timediff <= self.b_timing:
            self.b_label.draw()
            draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
            draw_rect(self.lanepos[lane], self.judge_pos, 40.0, self.time_remain_long * self.speed, 1, 1, 0)
            self.score += self.b_score
            self.combo = 0
            self.lanepressed_long[lane] = True
            self.pressing_note_long[lane] = self.cur_note[:]
            # libres.b_sound.play()
        else:
            draw_rect(self.lanepos[lane], self.pos_y, 40.0, self.cur_note[1] * self.speed, 1, 1, 1)
            self.lanepressed_long[lane] = False

    def judge_score_release(self, timediff, lane):
        if timediff <= self.p_timing:
            self.p_label.draw()
            draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
            self.score += self.p_score
            self.combo += 1
            libres.p_sound.play()
        elif timediff <= self.gr_timing:
            self.gr_label.draw()
            draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
            self.score += self.gr_score
            self.combo += 1
            libres.gr_sound.play()
        elif timediff <= self.g_timing:
            self.g_label.draw()
            draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
            self.score += self.g_score
            self.combo = 0
            libres.g_sound.play()

    def auto_play(self, lane):
        self.lanepressed = [False for i in range(0, 9)]
        if self.cur_note[1] == 0:
            if self.cur_note_time - self.judge_time <= 10:
                self.lanepressed[lane] = True
        elif self.cur_note_time - self.judge_time <= 15 \
                and self.cur_note[1] + self.cur_note[0] - self.dt - self.offset - self.judge_time > 0:
            self.lanepressed[lane] = True

    def update(self, dt):
        self.dt = int(time.time() * 1000) - self.music_start
        if self.dt > self.music_duration + 5000:
            self.on_close()


def play():
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
        notes = libres.parse_btm(btms[songnum])

        print('-----Selected [%s]-----' % (songfiles[songnum].split('.')[0]))
        while True:
            auto_flag = str(input('Auto?(Y/N): '))
            if auto_flag == 'Y' or auto_flag == 'y' or auto_flag == '':
                auto_flag = True
                break
            elif auto_flag == 'N' or auto_flag == 'n':
                auto_flag = False
                break

        GameWindow(offset=libres.offset, speed=libres.speed, song=song, notes=notes,
                   auto_flag=auto_flag, caption=songfiles[songnum].split('.')[0])
        pyglet.app.run()

    except Exception as e:
        print('Error 20002')
        # traceback.print_exc()
        raise SystemExit


if __name__ == '__main__':
    play()
