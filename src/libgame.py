try:

    import time
    import traceback
    import types
    import pyglet
    from pyglet.gl import *
    import matplotlib.pyplot as plt
    import libres

    pyglet.lib.load_library('avbin')
    pyglet.have_avbin = True
    # for pyinstaller to recognize avbin

except Exception as e:
    print('Error 20004')
    # traceback.print_exc()
    raise SystemExit

JUDGE_COLOR = (1, 0, 0)
NOTE_COLOR = (1, 1, 1)
LONG_COLOR = (1, 1, 1)
HIT_COLOR = (1, 0, 0)
KEY_HIT_COLOR = (255, 0, 0, 255)
LONG_PRESSING_COLOR = (1, 1, 0)
HIT_EFFECT_FRAMES = 3


def draw_rect(centerx, bottomy, width, height, color):
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glColor3f(color[0], color[1], color[2])
    glRectf(centerx - width / 2.0, bottomy, centerx - width / 2.0 + width, bottomy + height)
    glFlush()


class GameWindow(pyglet.window.Window):
    def __init__(self, offset, speed, song, notes, is_auto, caption):
        super(GameWindow, self).__init__(vsync=True, width=800, height=600, caption=caption)
        # pyglet.clock.set_fps_limit(60)
        self.song = song
        self.notes = notes
        self.offset = offset
        self.speed = speed
        self.is_auto = is_auto
        self.judge_pos = 100
        self.judge_time = self.judge_pos / self.speed
        # timing of the judge line
        self.lanes = [i for i in range(0, 9)]
        self.lane_pos = [i for i in range(100, 750, 75)]
        self.cur_note_time = 0
        self.cur_note = []
        self.pos_y = 0
        self.is_lane_pressed = [False for lane in self.lanes]
        # the lane is pressed or not
        self.time_remain_long = 0
        self.is_lane_pressed_long = [False for lane in self.lanes]
        # long note is hold pressed or not
        self.pressing_note_long = [[] for lane in self.lanes]
        # the long note being currently pressed
        self.missed_single_notes = []
        self.dt = 0
        # music played time
        self.score = 0
        self.combo = 0
        self.is_finished = False
        self.note_accuracy = []
        self.fps_display = pyglet.clock.ClockDisplay()
        self.hit_effect_cached_frames = [[0, 0, 0, 0, 0] for lane in self.lanes]

        self.song_summary = 0
        self.background = pyglet.sprite.Sprite(img=libres.background, x=400, y=300)
        self.p_timing = 40
        self.gr_timing = 80
        self.g_timing = 150
        self.b_timing = 200
        self.p_score = 573
        self.gr_score = 333
        self.g_score = 150
        self.b_score = 70
        self.p_label = pyglet.sprite.Sprite(img=libres.p_label, x=400, y=400)
        self.gr_label = pyglet.sprite.Sprite(img=libres.gr_label, x=400, y=400)
        self.g_label = pyglet.sprite.Sprite(img=libres.g_label, x=400, y=400)
        self.b_label = pyglet.sprite.Sprite(img=libres.b_label, x=400, y=400)
        self.m_label = pyglet.sprite.Sprite(img=libres.m_label, x=400, y=400)
        self.score_label = pyglet.text.Label(text="Score: 0", x=400, y=575, anchor_x='center', font_name='Acens')
        self.combo_label = pyglet.text.Label(text="0 combo", x=400, y=350, anchor_x='center', font_name='Acens')

        keys = ['Q', 'W', 'E', 'R', 'SPACE', 'U', 'I', 'O', 'P']
        self.key_hint = [pyglet.text.Label(text=keys[i], x=self.lane_pos[i], y=50, anchor_x='center',
                                           font_name='Arial', font_size=20) for i in range(0, 9)]

        self.key_hint_hit = [pyglet.text.Label(
            text=keys[i], x=self.lane_pos[i], y=50, anchor_x='center',
            font_name='Arial', font_size=20, color=KEY_HIT_COLOR) for i in range(0, 9)]

        if not self.is_auto:
            def auto_play(*args):
                pass

            self.auto_play = types.MethodType(auto_play, self)

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
        self.set_combo_color()
        # self.background.draw()
        draw_rect(400, self.judge_pos, 800.0, 2.0, JUDGE_COLOR)
        for i in self.lanes:
            # draw_rect(self.lanepos[i], self.judge_pos - 10, 50, 20.0, JUDGE_COLOR)
            self.key_hint[i].draw()

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
                            draw_rect(self.lane_pos[lane], self.pos_y, 40.0, 10.0, NOTE_COLOR)
                            if self.is_lane_pressed[lane]:
                                self.judge_score_single(time_diff, lane)
                            elif time_diff <= - self.b_timing and note not in self.missed_single_notes:
                                # miss
                                self.combo = 0
                                self.m_label.draw()
                                self.hit_effect_cached_frames[lane][4] += HIT_EFFECT_FRAMES
                                self.missed_single_notes.append(note)
                                self.note_accuracy.append(-1000)

                        else:

                            # long note
                            self.time_remain_long = note[0] + note[1] - self.dt - self.offset - self.judge_time
                            if self.is_lane_pressed[lane] and (not self.is_lane_pressed_long[lane]):
                                # first press, check score
                                self.judge_score_press(time_diff, lane)

                            elif (not self.is_lane_pressed[lane]) and (not self.is_lane_pressed_long[lane]):
                                # not pressed
                                draw_rect(self.lane_pos[lane], self.pos_y, 40.0, note[1] * self.speed, LONG_COLOR)

                                if time_diff <= - self.b_timing and note not in self.missed_single_notes:
                                    # press miss
                                    self.combo = 0
                                    self.m_label.draw()
                                    self.hit_effect_cached_frames[lane][4] += HIT_EFFECT_FRAMES
                                    self.missed_single_notes.append(note)
                                    self.note_accuracy.append(-1000)

                            elif self.is_lane_pressed[lane] and self.is_lane_pressed_long[lane] \
                                    and note == self.pressing_note_long[lane]:
                                # pressing, pressed, the note being checked is the note checked on last frame
                                if self.time_remain_long >= - self.b_timing:
                                    # long note will not go upside down
                                    draw_rect(self.lane_pos[lane], self.judge_pos,
                                              40.0, self.time_remain_long * self.speed, LONG_PRESSING_COLOR)
                                    draw_rect(self.lane_pos[lane], 75, 70.0, 50.0, HIT_COLOR)

                                    self.key_hint_hit[lane].draw()
                                else:
                                    # missed release (no release all the time)
                                    self.is_lane_pressed_long[lane] = False
                                    self.combo = 0
                                    self.m_label.draw()
                                    self.hit_effect_cached_frames[lane][4] += HIT_EFFECT_FRAMES

                            elif (not self.is_lane_pressed[lane]) and self.is_lane_pressed_long[lane] \
                                    and note == self.pressing_note_long[lane]:
                                # caught release
                                self.judge_score_release(self.time_remain_long, lane)

                            else:
                                draw_rect(self.lane_pos[lane], self.pos_y, 40.0, note[1] * self.speed, LONG_COLOR)

                    else:
                        break
                else:
                    continue
        self.score_label.draw()
        if self.combo != 0:
            self.combo_label.draw()
        self.hit_effect_draw()
        self.fps_display.draw()

    def set_combo_color(self):
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

    def on_key_press(self, key, modifiers):
        """set lanepressed to True on key press"""
        if key == pyglet.window.key.Q:
            self.is_lane_pressed[0] = True
        elif key == pyglet.window.key.W:
            self.is_lane_pressed[1] = True
        elif key == pyglet.window.key.E:
            self.is_lane_pressed[2] = True
        elif key == pyglet.window.key.R:
            self.is_lane_pressed[3] = True
        elif key == pyglet.window.key.SPACE:
            self.is_lane_pressed[4] = True
        elif key == pyglet.window.key.U:
            self.is_lane_pressed[5] = True
        elif key == pyglet.window.key.I:
            self.is_lane_pressed[6] = True
        elif key == pyglet.window.key.O:
            self.is_lane_pressed[7] = True
        elif key == pyglet.window.key.P:
            self.is_lane_pressed[8] = True

    def on_key_release(self, key, modifiers):
        """set lanepressed to False on key release"""
        if key == pyglet.window.key.Q:
            self.is_lane_pressed[0] = False
        elif key == pyglet.window.key.W:
            self.is_lane_pressed[1] = False
        elif key == pyglet.window.key.E:
            self.is_lane_pressed[2] = False
        elif key == pyglet.window.key.R:
            self.is_lane_pressed[3] = False
        elif key == pyglet.window.key.SPACE:
            self.is_lane_pressed[4] = False
        elif key == pyglet.window.key.U:
            self.is_lane_pressed[5] = False
        elif key == pyglet.window.key.I:
            self.is_lane_pressed[6] = False
        elif key == pyglet.window.key.O:
            self.is_lane_pressed[7] = False
        elif key == pyglet.window.key.P:
            self.is_lane_pressed[8] = False

    def judge_score_single(self, time_diff, lane):
        _time_diff = time_diff
        time_diff = abs(_time_diff)
        if time_diff <= self.p_timing:
            self.p_label.draw()
            self.hit_effect_cached_frames[lane][0] += HIT_EFFECT_FRAMES
            draw_rect(self.lane_pos[lane], 75, 70.0, 50.0, HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.p_score
            self.combo += 1
            libres.p_sound.play()
            self.notes[lane].remove(self.cur_note)
            self.note_accuracy.append(_time_diff)
        elif time_diff <= self.gr_timing:
            self.gr_label.draw()
            self.hit_effect_cached_frames[lane][1] += HIT_EFFECT_FRAMES
            draw_rect(self.lane_pos[lane], 75, 70.0, 50.0, HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.gr_score
            self.combo += 1
            libres.gr_sound.play()
            self.notes[lane].remove(self.cur_note)
            self.note_accuracy.append(_time_diff)
        elif time_diff <= self.g_timing:
            self.g_label.draw()
            self.hit_effect_cached_frames[lane][2] += HIT_EFFECT_FRAMES
            draw_rect(self.lane_pos[lane], 75, 70.0, 50.0, HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.g_score
            self.combo = 0
            libres.g_sound.play()
            self.notes[lane].remove(self.cur_note)
            self.note_accuracy.append(_time_diff)
        elif time_diff <= self.b_timing:
            self.b_label.draw()
            self.hit_effect_cached_frames[lane][3] += HIT_EFFECT_FRAMES
            draw_rect(self.lane_pos[lane], 75, 70.0, 50.0, HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.b_score
            self.combo = 0
            self.notes[lane].remove(self.cur_note)
            self.note_accuracy.append(_time_diff)
            # libres.b_sound.play()
        else:
            pass

    def judge_score_press(self, time_diff, lane):
        _time_diff = time_diff
        time_diff = abs(_time_diff)
        if time_diff <= self.p_timing:
            self.p_label.draw()
            self.hit_effect_cached_frames[lane][0] += HIT_EFFECT_FRAMES
            draw_rect(self.lane_pos[lane], 75, 70.0, 50.0, HIT_COLOR)
            self.key_hint_hit[lane].draw()
            draw_rect(self.lane_pos[lane], self.judge_pos, 40.0, self.time_remain_long * self.speed, LONG_PRESSING_COLOR)
            self.score += self.p_score
            libres.p_sound.play()
            self.is_lane_pressed_long[lane] = True
            self.pressing_note_long[lane] = self.cur_note[:]
            self.note_accuracy.append(_time_diff)
        elif time_diff <= self.gr_timing:
            self.gr_label.draw()
            self.hit_effect_cached_frames[lane][1] += HIT_EFFECT_FRAMES
            draw_rect(self.lane_pos[lane], 75, 70.0, 50.0, HIT_COLOR)
            self.key_hint_hit[lane].draw()
            draw_rect(self.lane_pos[lane], self.judge_pos, 40.0, self.time_remain_long * self.speed, LONG_PRESSING_COLOR)
            self.score += self.gr_score
            libres.gr_sound.play()
            self.is_lane_pressed_long[lane] = True
            self.pressing_note_long[lane] = self.cur_note[:]
            self.note_accuracy.append(_time_diff)
        elif time_diff <= self.g_timing:
            self.g_label.draw()
            self.hit_effect_cached_frames[lane][2] += HIT_EFFECT_FRAMES
            draw_rect(self.lane_pos[lane], 75, 70.0, 50.0, HIT_COLOR)
            self.key_hint_hit[lane].draw()
            draw_rect(self.lane_pos[lane], self.judge_pos, 40.0, self.time_remain_long * self.speed, LONG_PRESSING_COLOR)
            self.score += self.g_score
            self.combo = 0
            libres.g_sound.play()
            self.is_lane_pressed_long[lane] = True
            self.pressing_note_long[lane] = self.cur_note[:]
            self.note_accuracy.append(_time_diff)
        elif time_diff <= self.b_timing:
            self.b_label.draw()
            self.hit_effect_cached_frames[lane][3] += HIT_EFFECT_FRAMES
            draw_rect(self.lane_pos[lane], 75, 70.0, 50.0, HIT_COLOR)
            self.key_hint_hit[lane].draw()
            draw_rect(self.lane_pos[lane], self.judge_pos, 40.0, self.time_remain_long * self.speed, LONG_PRESSING_COLOR)
            self.score += self.b_score
            self.combo = 0
            self.is_lane_pressed_long[lane] = True
            self.pressing_note_long[lane] = self.cur_note[:]
            self.note_accuracy.append(_time_diff)
            # libres.b_sound.play()
        else:
            draw_rect(self.lane_pos[lane], self.pos_y, 40.0, self.cur_note[1] * self.speed, LONG_COLOR)
            self.is_lane_pressed_long[lane] = False

    def judge_score_release(self, time_diff, lane):
        _time_diff = time_diff
        time_diff = abs(_time_diff)
        if time_diff <= self.p_timing:
            self.p_label.draw()
            self.hit_effect_cached_frames[lane][0] += HIT_EFFECT_FRAMES
            draw_rect(self.lane_pos[lane], 75, 70.0, 50.0, HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.p_score
            self.combo += 1
            libres.p_sound.play()
            self.note_accuracy.append(_time_diff)
            self.notes[lane].remove(self.cur_note)
            self.is_lane_pressed_long[lane] = False
        elif time_diff <= self.gr_timing:
            self.gr_label.draw()
            self.hit_effect_cached_frames[lane][1] += HIT_EFFECT_FRAMES
            draw_rect(self.lane_pos[lane], 75, 70.0, 50.0, HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.gr_score
            self.combo += 1
            libres.gr_sound.play()
            self.note_accuracy.append(_time_diff)
            self.notes[lane].remove(self.cur_note)
            self.is_lane_pressed_long[lane] = False
        elif time_diff <= self.g_timing:
            self.g_label.draw()
            self.hit_effect_cached_frames[lane][2] += HIT_EFFECT_FRAMES
            draw_rect(self.lane_pos[lane], 75, 70.0, 50.0, HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.g_score
            self.combo = 0
            libres.g_sound.play()
            self.note_accuracy.append(_time_diff)
            self.notes[lane].remove(self.cur_note)
            self.is_lane_pressed_long[lane] = False
        else:
            # release bad or miss
            self.b_label.draw()
            self.hit_effect_cached_frames[lane][3] += HIT_EFFECT_FRAMES
            draw_rect(self.lane_pos[lane], 75, 70.0, 50.0, HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.b_score
            self.combo = 0
            self.note_accuracy.append(_time_diff)
            self.notes[lane].remove(self.cur_note)
            self.is_lane_pressed_long[lane] = False
        '''
        else:
            # miss (release too early)
            draw_rect(self.lane_pos[lane], 75, 70.0, 50.0, HIT_COLOR)
            self.hit_effect_cached_frames[lane][0] += HIT_EFFECT_FRAMES
            self.combo = 0
            self.notes[lane].remove(self.cur_note)
            self.is_lane_pressed_long[lane] = False
            self.note_accuracy.append(_time_diff)
        '''

    def auto_play(self, lane):
        self.is_lane_pressed = [False for i in range(0, 9)]
        if self.cur_note[1] == 0:
            if self.cur_note_time - self.judge_time <= 10:
                self.is_lane_pressed[lane] = True
        elif self.cur_note_time - self.judge_time <= 15 \
                and self.cur_note[1] + self.cur_note[0] - self.dt - self.offset - self.judge_time > 0:
            self.is_lane_pressed[lane] = True

    def on_song_finish(self):
        self.is_finished = True
        _sum_acc = 0
        _abs_acc = 0
        _not_missed_note_num = 0
        for i in self.note_accuracy:
            if i != -1000:
                _sum_acc += i
                _abs_acc += abs(i)
                _not_missed_note_num += 1
        if _not_missed_note_num != 0:
            print("\nAverage Absolute Error: %3f ms" % (_abs_acc / _not_missed_note_num))
        font = {'name': 'Arial'}
        font_title = {'name': 'Arial', 'color': 'darkred'}
        plt.scatter(range(1, len(self.note_accuracy) + 1), self.note_accuracy, s=5)
        plt.plot(range(0, len(self.note_accuracy) + 2), [self.p_timing] * (len(self.note_accuracy) + 2), 'r--')
        plt.plot(range(0, len(self.note_accuracy) + 2), [-self.p_timing] * (len(self.note_accuracy) + 2), 'r--')
        plt.plot(range(0, len(self.note_accuracy) + 2),
                 [(int((_sum_acc / len(self.note_accuracy)) * 10) / 10)] * (len(self.note_accuracy) + 2),
                 'g--', linewidth=2.5)
        plt.ylim(-100, 100)
        plt.xlim(0, len(self.note_accuracy) + 1)
        plt.title("Song Summary", **font_title)
        plt.ylabel("Error (ms)", **font)
        plt.xlabel("Note Number", **font)
        plt.yticks(range(-100, 120, 20), **font)
        plt.savefig("Song Summary.png")
        _pic = pyglet.image.load("./Song Summary.png")
        self.song_summary = pyglet.sprite.Sprite(img=_pic, x=0, y=0)

        def _on_finish_draw(self):
            self.clear()
            self.song_summary.draw()

        self.on_draw = types.MethodType(_on_finish_draw, self)

    def update(self, dt):
        self.dt = int(time.time() * 1000) - self.music_start
        if self.dt > self.music_duration and not self.is_finished:
            self.on_song_finish()
        elif self.is_finished:
            pass

        # self.on_close()

    def hit_score_label_draw(self, hit_type, opacity):
        if hit_type == 0:
            self.p_label.opacity = opacity
            self.p_label.draw()
            self.p_label.opacity = 255
        elif hit_type == 1:
            self.gr_label.opacity = opacity
            self.gr_label.draw()
            self.gr_label.opacity = 255
        elif hit_type == 2:
            self.g_label.opacity = opacity
            self.g_label.draw()
            self.g_label.opacity = 255
        elif hit_type == 3:
            self.b_label.opacity = opacity
            self.b_label.draw()
            self.b_label.opacity = 255
        else:
            self.m_label.opacity = opacity
            self.m_label.draw()
            self.m_label.opacity = 255

    def hit_effect_draw(self):
        for lane in self.lanes:
            for hit_type in range(0, 4):
                if self.hit_effect_cached_frames[lane][hit_type] != 0:
                    draw_rect(self.lane_pos[lane], 75, 70.0, 50.0, HIT_COLOR)
                    self.key_hint_hit[lane].draw()
                    opacity = 200 * (self.hit_effect_cached_frames[lane][hit_type]) / HIT_EFFECT_FRAMES
                    self.hit_score_label_draw(hit_type, opacity)
                    self.hit_effect_cached_frames[lane][hit_type] -= 1
            if self.hit_effect_cached_frames[lane][4] != 0:
                opacity = 200 * (self.hit_effect_cached_frames[lane][4]) / HIT_EFFECT_FRAMES
                self.hit_score_label_draw(4, opacity)
                self.hit_effect_cached_frames[lane][4] -= 1

    def on_draw_back(self):
        pass

    def auto_play_back(self):
        pass


def play():
    try:
        song_num = ''
        banner = ''
        song_files, btms = libres.scan()
        for i in range(0, len(song_files)):
            banner += '[' + str(i + 1) + '] ' + song_files[i].split('.')[0] + '\n'
        banner += 'Select Song No.: '
        while True:
            while True:
                song_num = str(input(banner))
                if song_num.isdigit():
                    song_num = int(song_num)
                    song_num += -1
                    if song_num in range(0, len(song_files)):
                        break
                    else:
                        print('-----Song does not exist-----\n\n')
            song = libres.load_song(song_files[song_num])
            notes = libres.parse_btm(btms[song_num])

            print('-----Selected [%s]-----' % (song_files[song_num].split('.')[0]))
            while True:
                is_auto = str(input('Auto?(Y/N): '))
                if is_auto == 'Y' or is_auto == 'y' or is_auto == '':
                    is_auto = True
                    break
                elif is_auto == 'N' or is_auto == 'n':
                    is_auto = False
                    break
            GameWindow(offset=libres.offset, speed=libres.speed, song=song, notes=notes,
                       is_auto=is_auto, caption=song_files[song_num].split('.')[0])

            pyglet.app.run()

    except Exception as e:
        print('Error 20002')
        traceback.print_exc()
        raise SystemExit


if __name__ == '__main__':
    play()
