import requests
import json
from mutagen.mp3 import MP3
import os
import sys
#import traceback


def update_song_list():
    def sort_list(arg):
        return {'name': arg['live_name'], 'level': arg['level'], 'id': arg['live_id'], 'clicks': arg['click_count']}
    try:
        resp = requests.get('https://m.tianyi9.com/API/getlivelist?type=public&offset=0&limit=9999')
        text = json.loads(resp.text)['content']['items']
        json.dump(list(map(sort_list, text)), open('./resources/asset/songlist', 'w'))
        with open('./resources/asset/songlist') as f:
            songlist = json.loads(f.read())
        songlist.sort(key=lambda song: song['level'])
        try:
            os.remove('./song_list.txt')
        except FileNotFoundError:
            pass
        with open('./song_list.txt', 'a') as f:
            f.write("No.\tLevel\tLive_ID\t\t\tClicks\tName\r\n")
            for i in range(0, len(songlist)):
                f.write("%04d\t%d\t%s\t%d\t%s\r\n" %
                        (i + 1, songlist[i]['level'], songlist[i]['id'], songlist[i]['clicks'], songlist[i]['name']))
    except Exception:
        print('Update error, check internet conection.')


def download_song(*live_id):
    for live in live_id:
        try:
            live_data = json.loads(requests.get('https://m.tianyi9.com/API/getlive?live_id=' + live).text)['content']
            artist = live_data.get('artist', None)
            level = str(live_data.get('level', None))
            name = 'LEVEL' + level + '  ' + artist + '  ' + live_data.get('live_name', None)
            sys.stdout.write('Downloading %s...' % name)
            song = requests.get('https://m.tianyi9.com/upload/' + live_data['bgm_path'])
            btm = json.loads(requests.get('https://m.tianyi9.com/upload/' + live_data['map_path']).text)

            with open("./resources/song/" + name + '.mp3', "wb") as f:
                f.write(song.content)
            MP3("./resources/song/" + name + '.mp3').delete()
            # remove ID3
            json.dump(btm, open('./resources/beatmap/' + name + '.btm', 'w'))
            print('OK')
        except:
            print('Download Error for live ID %s, may need login.' % live)
            #traceback.print_exc()
