try:

    import time
    import types
    import pyglet
    from pyglet.gl import *
    import matplotlib.pyplot as plt

except Exception as e:
    print('Error 20004')
    # traceback.print_exc()
    raise SystemExit


class GameWindow(pyglet.window.Window):

    JUDGE_COLOR = (1, 0, 0)
    NOTE_COLOR = (1, 1, 1)
    LONG_COLOR = (1, 1, 1)
    HIT_COLOR = (1, 0, 0)
    KEY_HIT_COLOR = (255, 0, 0, 255)
    LONG_PRESSING_COLOR = (1, 1, 0)
    HIT_EFFECT_FRAMES = 3

    @staticmethod
    def gl_draw_rect(centerx, bottomy, width, height, color):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glColor3f(color[0], color[1], color[2])
        glRectf(centerx - width / 2.0, bottomy, centerx - width / 2.0 + width, bottomy + height)
        glFlush()

    def __init__(self, offset, speed, song, notes, is_auto, caption, hit_banners_sounds):
        super(GameWindow, self).__init__(vsync=True, width=540, height=700, caption=caption)
        # pyglet.clock.set_fps_limit(60)
        self.center = [self.width/2, self.height/2]
        self.song = song
        self.notes = notes
        self.note_width = 40
        self.note_height = 10
        self.hit_effect_width = 60
        self.offset = offset
        self.speed = speed
        self.is_auto = is_auto
        self.judge_pos = 100
        self.judge_time = self.judge_pos / self.speed
        # timing of the judge line
        self.lanes = [lane for lane in range(0, 9)]
        self.lane_pos = [lane for lane in range(30, 900, 60)]
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
        # self.background = pyglet.sprite.Sprite(img=libres.background, x=self.width/2, y=self.height/2)
        self.p_timing = 40
        self.gr_timing = 80
        self.g_timing = 150
        self.b_timing = 200
        self.p_score = 573
        self.gr_score = 333
        self.g_score = 150
        self.b_score = 70
        self.score_label = pyglet.text.Label(text="Score: 0", x=20, y=self.height-30, anchor_x='left', font_name='Acens')
        self.combo_label = pyglet.text.Label(text="0 combo", x=self.width/2, y=250, anchor_x='center', font_name='Acens')
        self.p_banner = pyglet.sprite.Sprite(img=hit_banners_sounds[0], x=self.width/2, y=300)
        self.gr_banner = pyglet.sprite.Sprite(img=hit_banners_sounds[1], x=self.width/2, y=300)
        self.g_banner = pyglet.sprite.Sprite(img=hit_banners_sounds[2], x=self.width/2, y=300)
        self.b_banner = pyglet.sprite.Sprite(img=hit_banners_sounds[3], x=self.width/2, y=300)
        self.m_banner = pyglet.sprite.Sprite(img=hit_banners_sounds[4], x=self.width/2, y=300)
        self.p_sound = hit_banners_sounds[5]
        self.gr_sound = hit_banners_sounds[6]
        self.g_sound = hit_banners_sounds[7]
        self.score_banners = [self.p_banner, self.gr_banner, self.g_banner, self.b_banner, self.m_banner]
        for banner in self.score_banners:
            banner.opacity = 255

        keys = ['Q', 'W', 'E', 'R', 'B', 'U', 'I', 'O', 'P']
        self.key_hint = [pyglet.text.Label(text=keys[i], x=self.lane_pos[i], y=50, anchor_x='center',
                                           font_name='Arial', font_size=20) for i in range(0, 9)]

        self.key_hint_hit = [pyglet.text.Label(
            text=keys[i], x=self.lane_pos[i], y=50, anchor_x='center',
            font_name='Arial', font_size=20, color=self.KEY_HIT_COLOR) for i in range(0, 9)]

        if not self.is_auto:
            def auto_play(*args):
                pass

            self.auto_play = types.MethodType(auto_play, self)

        self.player = pyglet.media.Player()
        self.player.queue(self.song)
        self.music_duration = int(self.song.duration * 1000)
        self.player.play()
        self.music_start = int(time.time() * 1000)
        # music start time in ms

        pyglet.clock.schedule_interval(self.update, 1 / 200)
        # self.score = 0

    def on_draw(self):
        self.clear()
        self.score_label.text = "Score: %d" % self.score
        self.combo_label.text = "%d combo" % self.combo
        self.set_combo_color()
        # self.background.draw()
        self.gl_draw_rect(self.center[0], 95, self.width, self.note_height, self.JUDGE_COLOR)
        for i in self.lanes:
            # self.draw_rect(self.lanepos[i], self.judge_pos - 10, 50, 20.0, self.JUDGE_COLOR)
            self.key_hint[i].draw()
        # self.score_banners_draw()
        for lane in self.lanes:
            for note in self.notes[lane]:
                if note[0] + note[1] - self.dt - self.offset >= 0:
                    # note is not below window bottom
                    if (note[0] - self.dt - self.offset) * self.speed <= self.height:
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
                            self.gl_draw_rect(self.lane_pos[lane], self.pos_y, self.note_width, self.note_height, self.NOTE_COLOR)
                            if self.is_lane_pressed[lane]:
                                self.judge_score_single(time_diff, lane)
                            elif time_diff <= - self.b_timing and note not in self.missed_single_notes:
                                # miss
                                self.combo = 0
                                self.m_banner.draw()
                                self.hit_effect_cached_frames[lane][4] += self.HIT_EFFECT_FRAMES
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
                                self.gl_draw_rect(self.lane_pos[lane], self.pos_y, self.note_width, note[1] * self.speed, self.LONG_COLOR)

                                if time_diff <= - self.b_timing and note not in self.missed_single_notes:
                                    # press miss
                                    self.combo = 0
                                    self.m_banner.draw()
                                    self.hit_effect_cached_frames[lane][4] += self.HIT_EFFECT_FRAMES
                                    self.missed_single_notes.append(note)
                                    self.note_accuracy.append(-1000)

                            elif self.is_lane_pressed[lane] and self.is_lane_pressed_long[lane] \
                                    and note == self.pressing_note_long[lane]:
                                # pressing, pressed, the note being checked is the note checked on last frame
                                if self.time_remain_long >= - self.b_timing:
                                    # long note will not go upside down
                                    self.gl_draw_rect(self.lane_pos[lane], self.judge_pos,
                                                      self.note_width, self.time_remain_long * self.speed, self.LONG_PRESSING_COLOR)
                                    self.gl_draw_rect(self.lane_pos[lane], 75, self.hit_effect_width, 50, self.HIT_COLOR)

                                    self.key_hint_hit[lane].draw()
                                else:
                                    # missed release (no release all the time)
                                    self.is_lane_pressed_long[lane] = False
                                    self.combo = 0
                                    self.m_banner.draw()
                                    self.hit_effect_cached_frames[lane][4] += self.HIT_EFFECT_FRAMES

                            elif (not self.is_lane_pressed[lane]) and self.is_lane_pressed_long[lane] \
                                    and note == self.pressing_note_long[lane]:
                                # caught release
                                self.judge_score_release(self.time_remain_long, lane)

                            else:
                                self.gl_draw_rect(self.lane_pos[lane], self.pos_y, self.note_width, note[1] * self.speed, self.LONG_COLOR)

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
            self.p_banner.draw()
            self.hit_effect_cached_frames[lane][0] += self.HIT_EFFECT_FRAMES
            self.gl_draw_rect(self.lane_pos[lane], 75, self.hit_effect_width, 50, self.HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.p_score
            self.combo += 1
            self.p_sound.play()
            self.notes[lane].remove(self.cur_note)
            self.note_accuracy.append(_time_diff)
        elif time_diff <= self.gr_timing:
            self.gr_banner.draw()
            self.hit_effect_cached_frames[lane][1] += self.HIT_EFFECT_FRAMES
            self.gl_draw_rect(self.lane_pos[lane], 75, self.hit_effect_width, 50, self.HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.gr_score
            self.combo += 1
            self.gr_sound.play()
            self.notes[lane].remove(self.cur_note)
            self.note_accuracy.append(_time_diff)
        elif time_diff <= self.g_timing:
            self.g_banner.draw()
            self.hit_effect_cached_frames[lane][2] += self.HIT_EFFECT_FRAMES
            self.gl_draw_rect(self.lane_pos[lane], 75, self.hit_effect_width, 50, self.HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.g_score
            self.combo = 0
            self.g_sound.play()
            self.notes[lane].remove(self.cur_note)
            self.note_accuracy.append(_time_diff)
        elif time_diff <= self.b_timing:
            self.b_banner.draw()
            self.hit_effect_cached_frames[lane][3] += self.HIT_EFFECT_FRAMES
            self.gl_draw_rect(self.lane_pos[lane], 75, self.hit_effect_width, 50, self.HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.b_score
            self.combo = 0
            self.notes[lane].remove(self.cur_note)
            self.note_accuracy.append(_time_diff)
            # self.b_sound.play()
        else:
            pass

    def judge_score_press(self, time_diff, lane):
        _time_diff = time_diff
        time_diff = abs(_time_diff)
        if time_diff <= self.p_timing:
            self.p_banner.draw()
            self.hit_effect_cached_frames[lane][0] += self.HIT_EFFECT_FRAMES
            self.gl_draw_rect(self.lane_pos[lane], 75, self.hit_effect_width, 50, self.HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.gl_draw_rect(self.lane_pos[lane], self.judge_pos, self.note_width, self.time_remain_long * self.speed, self.LONG_PRESSING_COLOR)
            self.score += self.p_score
            self.p_sound.play()
            self.is_lane_pressed_long[lane] = True
            self.pressing_note_long[lane] = self.cur_note[:]
            self.note_accuracy.append(_time_diff)
        elif time_diff <= self.gr_timing:
            self.gr_banner.draw()
            self.hit_effect_cached_frames[lane][1] += self.HIT_EFFECT_FRAMES
            self.gl_draw_rect(self.lane_pos[lane], 75, self.hit_effect_width, 50, self.HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.gl_draw_rect(self.lane_pos[lane], self.judge_pos, self.note_width, self.time_remain_long * self.speed, self.LONG_PRESSING_COLOR)
            self.score += self.gr_score
            self.gr_sound.play()
            self.is_lane_pressed_long[lane] = True
            self.pressing_note_long[lane] = self.cur_note[:]
            self.note_accuracy.append(_time_diff)
        elif time_diff <= self.g_timing:
            self.g_banner.draw()
            self.hit_effect_cached_frames[lane][2] += self.HIT_EFFECT_FRAMES
            self.gl_draw_rect(self.lane_pos[lane], 75, self.hit_effect_width, 50, self.HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.gl_draw_rect(self.lane_pos[lane], self.judge_pos, self.note_width, self.time_remain_long * self.speed, self.LONG_PRESSING_COLOR)
            self.score += self.g_score
            self.combo = 0
            self.g_sound.play()
            self.is_lane_pressed_long[lane] = True
            self.pressing_note_long[lane] = self.cur_note[:]
            self.note_accuracy.append(_time_diff)
        elif time_diff <= self.b_timing:
            self.b_banner.draw()
            self.hit_effect_cached_frames[lane][3] += self.HIT_EFFECT_FRAMES
            self.gl_draw_rect(self.lane_pos[lane], 75, self.hit_effect_width, 50, self.HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.gl_draw_rect(self.lane_pos[lane], self.judge_pos, self.note_width, self.time_remain_long * self.speed, self.LONG_PRESSING_COLOR)
            self.score += self.b_score
            self.combo = 0
            self.is_lane_pressed_long[lane] = True
            self.pressing_note_long[lane] = self.cur_note[:]
            self.note_accuracy.append(_time_diff)
            # self.b_sound.play()
        else:
            self.gl_draw_rect(self.lane_pos[lane], self.pos_y, self.note_width, self.cur_note[1] * self.speed, self.LONG_COLOR)
            self.is_lane_pressed_long[lane] = False

    def judge_score_release(self, time_diff, lane):
        _time_diff = time_diff
        time_diff = abs(_time_diff)
        if time_diff <= self.p_timing:
            self.p_banner.draw()
            self.hit_effect_cached_frames[lane][0] += self.HIT_EFFECT_FRAMES
            self.gl_draw_rect(self.lane_pos[lane], 75, self.hit_effect_width, 50, self.HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.p_score
            self.combo += 1
            self.p_sound.play()
            self.note_accuracy.append(_time_diff)
            self.notes[lane].remove(self.cur_note)
            self.is_lane_pressed_long[lane] = False
        elif time_diff <= self.gr_timing:
            self.gr_banner.draw()
            self.hit_effect_cached_frames[lane][1] += self.HIT_EFFECT_FRAMES
            self.gl_draw_rect(self.lane_pos[lane], 75, self.hit_effect_width, 50, self.HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.gr_score
            self.combo += 1
            self.gr_sound.play()
            self.note_accuracy.append(_time_diff)
            self.notes[lane].remove(self.cur_note)
            self.is_lane_pressed_long[lane] = False
        elif time_diff <= self.g_timing:
            self.g_banner.draw()
            self.hit_effect_cached_frames[lane][2] += self.HIT_EFFECT_FRAMES
            self.gl_draw_rect(self.lane_pos[lane], 75, self.hit_effect_width, 50, self.HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.g_score
            self.combo = 0
            self.g_sound.play()
            self.note_accuracy.append(_time_diff)
            self.notes[lane].remove(self.cur_note)
            self.is_lane_pressed_long[lane] = False
        else:
            # release bad or miss
            self.b_banner.draw()
            self.hit_effect_cached_frames[lane][3] += self.HIT_EFFECT_FRAMES
            self.gl_draw_rect(self.lane_pos[lane], 75, self.hit_effect_width, 50, self.HIT_COLOR)
            self.key_hint_hit[lane].draw()
            self.score += self.b_score
            self.combo = 0
            self.note_accuracy.append(_time_diff)
            self.notes[lane].remove(self.cur_note)
            self.is_lane_pressed_long[lane] = False
        '''
        else:
            # miss (release too early)
            self.draw_rect(self.lane_pos[lane], 75, 70.0, self.hit_effect_width, self.HIT_COLOR)
            self.hit_effect_cached_frames[lane][0] += self.HIT_EFFECT_FRAMES
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
        plt.yticks(range(-int(self.b_timing), int(self.b_timing)+int(self.b_timing/5), int(self.b_timing/5)), **font)
        plt.savefig("Song Summary.png")
        _pic = pyglet.image.load("./Song Summary.png")
        self.song_summary = pyglet.sprite.Sprite(img=_pic, x=0, y=self.height/2-3 * self.width/8)
        self.song_summary.scale = self.width/800

        def _on_finish_draw(self):
            self.clear()
            self.song_summary.draw()

        self.on_draw = types.MethodType(_on_finish_draw, self)

    def hit_score_label_draw(self, hit_type, opacity):
        if hit_type == 0:
            self.p_banner.opacity = opacity
            self.p_banner.draw()
            self.p_banner.opacity = 255
        elif hit_type == 1:
            self.gr_banner.opacity = opacity
            self.gr_banner.draw()
            self.gr_banner.opacity = 255
        elif hit_type == 2:
            self.g_banner.opacity = opacity
            self.g_banner.draw()
            self.g_banner.opacity = 255
        elif hit_type == 3:
            self.b_banner.opacity = opacity
            self.b_banner.draw()
            self.b_banner.opacity = 255
        else:
            self.m_banner.opacity = opacity
            self.m_banner.draw()
            self.m_banner.opacity = 255

    def hit_effect_draw(self):
        for lane in self.lanes:
            for hit_type in range(0, 4):
                if self.hit_effect_cached_frames[lane][hit_type] != 0:
                    self.gl_draw_rect(self.lane_pos[lane], 75, self.hit_effect_width, 50, self.HIT_COLOR)
                    self.key_hint_hit[lane].draw()
                    opacity = 200 * (self.hit_effect_cached_frames[lane][hit_type]) / self.HIT_EFFECT_FRAMES
                    self.hit_score_label_draw(hit_type, 255)
                    self.hit_effect_cached_frames[lane][hit_type] -= 1
            if self.hit_effect_cached_frames[lane][4] != 0:
                opacity = 200 * (self.hit_effect_cached_frames[lane][4]) / self.HIT_EFFECT_FRAMES
                self.hit_score_label_draw(4, opacity)
                self.hit_effect_cached_frames[lane][4] -= 1

    def update(self, dt):
        self.dt = int(time.time() * 1000) - self.music_start
        if self.dt > self.music_duration and not self.is_finished:
            self.on_song_finish()
        elif self.is_finished:
            pass

    def on_close(self):
        self.player.delete()
        super(GameWindow, self).on_close()
        # del self
    '''
    def score_banners_draw(self):
        for banner in self.score_banners:
            banner.draw()
            if banner.opacity > 10:
                banner.opacity -= banner.opacity/1.5
            else:
                banner.opacity = 0
    '''