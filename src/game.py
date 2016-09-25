try:

    # import traceback
    import cmd
    import pyglet
    import gamewindow
    import libres
    import llpractice
    import sys
    import os

except Exception as e:
    print('Error 20004')
    # traceback.print_exc()
    raise SystemExit


def play():
    try:

        song_num = ''
        banner = ''

        song_files, btms = libres.scan()
        # print('OK')
        for i in range(0, len(song_files)):
            banner += '[' + str(i + 1) + '] ' + song_files[i][:-4] + '\n'
        banner += 'Select Song No.: '

        #while True:
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

        print('-----Selected [%s]-----' % (song_files[song_num][:-4]))
        while True:
            is_auto = str(input('Auto?(Y/N): '))
            if is_auto == 'Y' or is_auto == 'y' or is_auto == '':
                is_auto = True
                break
            elif is_auto == 'N' or is_auto == 'n':
                is_auto = False
                break
        gamewindow.GameWindow(offset=libres.offset, speed=libres.speed, song=song, notes=notes,
                              is_auto=is_auto, caption=song_files[song_num].split('.')[0],
                              hit_banners_sounds=libres.hit_banners_sounds)

        pyglet.app.run()

    except:
        print('Error 20002')
        return
        # traceback.print_exc()
        #raise SystemExit


class GameConsole(cmd.Cmd):
    intro = None
    prompt = 'SIFemu>> '

    def cmdloop_keyboardinterrupt(self):
        print('\rType quit to exit.')
        try:
            cmd.Cmd.cmdloop(self)
        except KeyboardInterrupt:
            self.cmdloop_keyboardinterrupt()

    def cmdloop(self):
        # print(self.banner)
        try:
            cmd.Cmd.cmdloop(self)
        except KeyboardInterrupt:
            self.cmdloop_keyboardinterrupt()

    def do_play(self, args):
        """Play available songs."""
        play()

    def do_updatesonglist(self, args):
        """Update available songs from LLPractice. Please refer to the song_list.txt file in the game folder for available songs."""
        sys.stdout.write('Updating song list...')
        llpractice.update_song_list()
        print('OK')

    def do_downloadsong(self, args):
        """Download song with Live_ID.
        Usage:
        download_song Live_ID Live_ID...
        """
        if len(args) == 0:
            return
        for live in args.split(' '):
            llpractice.download_song(live)

    def do_quit(self, args):
        """quit"""
        print('Bye')
        raise SystemExit


def init():
    if not os.path.exists('./resources/song'):
        os.makedirs('./resources/song')
    if not os.path.exists('./resources/beatmap'):
        os.makedirs('./resources/beatmap')
    hint = """Available commands:
        [play]: Play available songs
        [updatesonglist]: Get available songs from LLPractice
        [downloadsong]: Download song from LLPractice with Live_ID
        [quit]: Quit the system
        Use help <command> to see detailed explanation."""
    print(hint)
    GameConsole().cmdloop()


if __name__ == '__main__':
    play()
