try:

    import pyglet
    pyglet.lib.load_library('avbin') #for pyinstaller to recognize avbin
    pyglet.have_avbin=True
    from pyglet.gl import *
    import libres
    import time

except Exception as e:
        print('Error 20002')
        #traceback.print_exc()
        raise SystemExit

#import traceback
def draw_rect(centerx, bottomy, width, height, r, g, b):
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glColor3f(r, g, b)
    glRectf(centerx - width / 2.0, bottomy, centerx - width / 2.0 + width, bottomy + height)
    glFlush()


class Game_Window(pyglet.window.Window):
    def __init__(self, offset, speed, notes, music_start, auto_flag, caption):
        super(Game_Window, self).__init__(vsync=True, width=800, height=600, caption=caption)
        # pyglet.clock.set_fps_limit(60)
        self.notes = notes
        self.curnote = [0 for i in range(0, 9)]
        self.hitnote = [[0,0] for i in range(0, 9)]
        self.judge_pos = 100
        self.score = 0
        self.fps_display = pyglet.clock.ClockDisplay()
        self.dt = 0  # note 距离perfect点的距离 in ms
        self.music_start = music_start
        self.offset = offset
        self.speed = speed
        self.judge = self.judge_pos / self.speed  # 底部蓝线的timing
        self.lanes = [i for i in range(0, 9, 1)]
        self.lanepos = [i for i in range(100, 750, 65)]
        self.background = pyglet.sprite.Sprite(img=libres.background, x=400, y=300)
        self.p_score = 573
        self.gr_score = 333
        self.g_score = 150
        self.p_label = pyglet.sprite.Sprite(img=libres.p_label, x=400, y=400)
        self.gr_label = pyglet.sprite.Sprite(img=libres.gr_label, x=400, y=400)
        self.g_label = pyglet.sprite.Sprite(img=libres.g_label, x=400, y=400)
        self.combo = 0
        self.lanepressed = [[False, 0] for i in range(0, 9)]
        self.lanepressed_long = [[False, 0] for i in range(0, 9)]
        self.lastlane_long = 0
        self.score_label = pyglet.text.Label(text="Score: 0", x=400, y=575, anchor_x='center')
        self.combo_label = pyglet.text.Label(text="0 combo", x=400, y=350, anchor_x='center')
        self.count = 0
        self.lane = 0
        self.long_drawed = [False for i in range(0,9)]
        self.auto = auto_flag

    def on_draw(self):
        self.clear()
        self.background.draw()
        self.score_label.text = "Score: %d" % (self.score)
        self.combo_label.text = "%d combo" % (self.combo)
        self.score_label.draw()
        self.combo_label.draw()
        self.fps_display.draw()
        draw_rect(400, self.judge_pos, 800.0, 2.0, 0, 0, 1)

        for lane in self.lanes:
            for note in self.notes[lane]:
                if (note[0] - self.dt + note[1]) * self.speed - self.offset >= -100:
                    # note未出下边界
                    if (note[0] - self.dt - self.offset) * self.speed <= 600:
                        # note 进入上边界
                        pos_y = (note[0] - self.dt - self.offset) * self.speed
                        self.curnote[lane] = note[0] - self.dt - self.offset
                        self.hitnote[lane] = note[:]
                        if self.auto: self.autoplay(lane)
                        self.lane = lane
                        if note[1] == 0:
                            # 是单键
                            draw_rect(self.lanepos[lane], pos_y, 40.0, 10.0, 1, 1, 1)
                            self.hit_single()
                        else:
                            # 是长条
                            # print('%dlong:%d%s%s' % (self.count,lane, self.lanepressed_long[lane][0], self.lanepressed[lane][0]))
                            if self.lanepressed_long[lane][0] or self.lanepressed[lane][0]:
                                #  print('%dinside_if:%d%s%s' % (
                                # self.count, lane, self.lanepressed_long[lane][0], self.lanepressed[lane][0]))
                                if not self.lanepressed_long[lane][0]:
                                    self.lanepressed_long[lane] = self.lanepressed[lane][:]
                                self.lanepressed[lane][0] = False
                                # self.count += 1
                                if pos_y - self.judge_pos <= 20 and note[0] + note[1] - self.dt > 0: #到达judje且不反向
                                    draw_rect(self.lanepos[lane], self.judge_pos, 40.0,
                                              (note[0] + note[1] - self.dt - 25) * self.speed, 1, 1, 0)
                                    draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
                                    if not self.long_drawed[lane]:
                                        self.p_label.draw()
                                        libres.p_sound.play()
                                        self.long_drawed[lane] = True
                                    if note[0] + note[1] - self.dt <= 20:
                                        self.notes[lane].remove(note)
                                        self.combo += 1
                                        libres.p_sound.play()
                                        draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 0, 1, 0)
                                        self.p_label.draw()
                                        self.long_drawed[lane] = False
                                else:
                                    self.lanepressed_long[lane][0] = False
                                    #   print('%dsetFalse'%self.count)
                                    # pass
                            else:
                                # miss
                                draw_rect(self.lanepos[lane], pos_y, 40.0, note[1] * self.speed, 1, 1, 1)
                    else:
                        break
                else:
                    continue

    def on_key_press(self, key, modifiers):
        """Action upon key press, raise interrupt, modify self.lanepressed"""
        p_timing = 50
        gr_timing = 80
        g_timing = 100

        def key_action(lane):
            try:
                if abs(self.curnote[lane] - self.judge) <= p_timing:
                    if self.hitnote[lane][1] == 0:
                        self.notes[lane].remove(self.hitnote[lane])
                        self.curnote[lane] = 0
                    self.lanepressed[lane] = [True, 0]
                elif abs(self.curnote[lane] - self.judge) <= gr_timing:
                    if self.hitnote[lane][1] == 0:
                        self.notes[lane].remove(self.hitnote[lane])
                        self.curnote[lane] = 0
                    self.lanepressed[lane] = [True, 1]
                elif abs(self.curnote[lane] - self.judge) <= g_timing:
                    if self.hitnote[lane][1] == 0:
                        self.notes[lane].remove(self.hitnote[lane])
                        self.curnote[lane] = 0
                    self.lanepressed[lane] = [True, 2]
            except ValueError:
                #print("%s,%s,%s"%(self.lane,lane,self.hitnote[lane]))
                pass

        if key == pyglet.window.key.A: key_action(0)
        if key == pyglet.window.key.S: key_action(1)
        if key == pyglet.window.key.D: key_action(2)
        if key == pyglet.window.key.F: key_action(3)
        if key == pyglet.window.key.G: key_action(4)
        if key == pyglet.window.key.H: key_action(5)
        if key == pyglet.window.key.J: key_action(6)
        if key == pyglet.window.key.K: key_action(7)
        if key == pyglet.window.key.L: key_action(8)

    def hit_single(self):
        """Action upon hit"""
        for lane in range(0, 9):
            if self.lanepressed[lane][0]:
                draw_rect(self.lanepos[lane], 75, 70.0, 50.0, 1, 0, 0)
                self.lanepressed[lane][0] = False
                if self.lanepressed[lane][1] == 0:
                    self.p_label.draw()
                    self.score += self.p_score
                    self.combo += 1
                    libres.p_sound.play()
                elif self.lanepressed[lane][1] == 1:
                    self.gr_label.draw()
                    self.score += self.gr_score
                    self.combo += 1
                    libres.gr_sound.play()
                elif self.lanepressed[lane][1] == 2:
                    self.g_label.draw()
                    self.score += self.g_score
                    self.combo = 0
                    libres.g_sound.play()

    def autoplay(self, lane):
        if abs(self.curnote[lane] - self.judge) <= 15:
            self.lanepressed[lane] = [True, 0]
            if self.hitnote[lane][1] == 0:
                # 是单键
                self.notes[lane].remove(self.hitnote[lane])

    def update(self, dt):
        self.dt = int(time.time() * 1000) - self.music_start
        if self.dt > 180000:
            self.on_close()
            # print(self.dt)



def play():
    try:
        banner = ''
        songfiles,btms = libres.scan()
        for i in range(0,len(songfiles)):
            banner += '['+ str(i + 1) + '] ' + songfiles[i].split('.')[0] +'\n'
        banner += 'Select Song No.: '

        while True: 
            songnum = str(input(banner))
            if songnum.isdigit():
                songnum = int(songnum)
                songnum += -1
                if songnum in range(0,len(songfiles)): 
                    break
                else:
                    print('-----Song does not exist.-----\n\n')
        song = libres.load_song(songfiles[songnum])
        player = pyglet.media.Player()
        player.queue(song)
        notes = libres.parse_btm(btms[songnum])

        print('-----Selected [%s]-----'%(songfiles[songnum].split('.')[0]))
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
        window = Game_Window(offset=libres.offset, speed=libres.speed, notes=notes, music_start=music_start, auto_flag=auto_flag,caption=songfiles[songnum].split('.')[0])
        pyglet.clock.schedule_interval(window.update, 1 / 200)
        pyglet.app.run()
    except Exception as e:
        print('Error 20002')
        #traceback.print_exc()
        raise SystemExit

if __name__ == '__main__':
    play()
