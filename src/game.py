try:

    import traceback
    import pyglet
    import gamewindow
    import libres

except Exception as e:
    print('Error 20004')
    # traceback.print_exc()
    raise SystemExit


def play():
    try:

        song_num = ''
        banner = ''

        song_files, btms = libres.scan()
        print('OK')
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
            gamewindow.GameWindow(offset=libres.offset, speed=libres.speed, song=song, notes=notes,
                                  is_auto=is_auto, caption=song_files[song_num].split('.')[0],
                                  hit_banners_sounds=libres.hit_banners_sounds)

            pyglet.app.run()

    except Exception as e:
        print('Error 20002')
        traceback.print_exc()
        raise SystemExit


if __name__ == '__main__':
    play()
