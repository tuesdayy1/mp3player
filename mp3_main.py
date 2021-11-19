# -*- coding: cp1251 -*-
from PyQt5.QtWidgets import QMainWindow, QApplication, \
    QStyle, QFileDialog, QWidget, QMessageBox
from PyQt5.QtCore import QTimer
from mutagen.mp3 import MP3
import sys
from pygame import mixer
from mp3player import Ui_MainWindow
from create_playlist import Ui_Form as Ui1
from open_pl import Ui_Form as Ui2
from songs_in_playlist import Ui_Form as Ui3
from songs.get_songs import get_song
import webbrowser
import sqlite3
from random import shuffle


class Mp3Player(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setGeometry(200, 300, 500, 560)
        self.setWindowTitle('Mp3Player')
        self.count = 0
        self.count_for_vol = 0
        self.is_stoped = True
        self.play1 = 0
        self.play = 0
        self.count_for_timer = 0
        self.count_for_style = 0
        self.songs = []
        self.songs_path = []

        self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.pushButton_2.clicked.connect(self.comp)

        self.pushButton_6.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.pushButton_6.clicked.connect(self.volume)

        self.horizontalSlider.setRange(0, 100)
        self.horizontalSlider.setPageStep(25)
        self.horizontalSlider.setSliderPosition(100)
        self.horizontalSlider.valueChanged[int].connect(self.change_value_volume)

        self.horizontalSlider_2.setPageStep(1)
        self.horizontalSlider_2.valueChanged[int].connect(self.change_value_song)

        self.pushButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.pushButton.clicked.connect(self.skipBack)

        self.pushButton_3.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.pushButton_3.clicked.connect(self.skipForw)

        self.pushButton_4.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.pushButton_4.clicked.connect(self.stop)

        self.pushButton_5.clicked.connect(self.download)
        self.pushButton_7.clicked.connect(self.create_playlist)
        self.pushButton_8.clicked.connect(self.download_youtube)
        self.pushButton_9.clicked.connect(self.open_playlist)
        self.pushButton_12.clicked.connect(self.random)

        self.pushButton_13.clicked.connect(self.style_)
        self.pushButton_13.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMenuButton))

        self.lcdNumber.display('00:00')

        self.init()

    def init(self):
        self.createplaylist = CreatePlaylist()
        self.openplaylist = OpenPlayList(self)

        for i in self.songs_path:
            self.songs.append(get_song(i))

        for i in self.songs_path:
            self.listWidget.addItem(i)
        self.listWidget.itemActivated.connect(self.other_song)

        mixer.init()
        self.msc = mixer.music
        self.currvol = 1
        self.currvol_slider_ = 100
        self.currsong = ''
        self.currsong_ind = 0
        self.currsong_list = ''
        self.play1, self.play = 0, 0
        self.horizontalSlider.setSliderPosition(self.currvol_slider_)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tim)

    def get(self, text):
        self.songs = []
        self.songs_path = []
        self.listWidget.clear()
        self.label_2.setText('')
        self.lcdNumber.display('00:00')
        self.count_for_timer = 0
        self.msc.stop()
        self.timer.stop()
        self.is_stoped = True
        self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.count = 0
        self.play1, self.play = 1, 1

        for i in text:
            self.songs_path.append(i[0])
        self.init()

    def end_event(self):
        if self.currsong_ind == len(self.songs) - 1:
            self.currsong_ind = 0
            self.currsong = self.songs[0]
            self.currsong_list = self.songs_path[0].split()[-1]
            self.msc.load(self.currsong)
            self.play = 0
        else:
            self.currsong_ind += 1
            self.currsong = self.songs[self.currsong_ind]
            self.currsong_list = self.songs_path[self.currsong_ind]
            self.msc.load(self.currsong)
            self.play = 0
        self.lcdNumber.display('00:00')
        self.msc.play()
        self.play_func()

    def tim(self):
        if self.count_for_timer > self.end or self.horizontalSlider_2.value() == self.end:
            self.count_for_timer = 0
            self.end_event()
        else:
            self.count_for_timer += 1
            self.timer.start(1000)
            self.lcd()
            self.horizontalSlider_2.setSliderPosition(self.count_for_timer)

    def play_func(self):
        if not self.is_stoped and self.songs:
            if self.play1 == 0:
                self.msc.load(self.songs[0])
                self.currsong = self.songs[self.currsong_ind]
                self.currsong_list = self.songs_path[self.currsong_ind]
                self.msc.play()
                self.play1 += 1
            if self.play == 0:
                self.play += 1
                self.horizontalSlider_2.setSliderPosition(0)
                self.end = int(str(MP3(self.currsong).info.length).split('.')[0])
                self.horizontalSlider_2.setRange(0, self.end)
                self.label_2.setText(self.currsong_list)
                self.timer.start(1000)

    def comp(self):
        if self.songs:
            if self.count == 0:
                self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
                self.count = 1
                self.is_stoped = False
                self.music()
                self.play_func()
            else:
                self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                self.count = 0
                self.is_stoped = True
                self.music()

    def music(self):
        if not self.is_stoped:
            self.msc.unpause()
            self.timer.start(1000)
        else:
            self.msc.pause()
            self.timer.stop()

    def volume(self):
        if self.count_for_vol == 0:
            self.pushButton_6.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
            self.msc.set_volume(0)
            self.count_for_vol = 1
        else:
            self.pushButton_6.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
            self.msc.set_volume(self.currvol)
            self.count_for_vol = 0

    def change_value_volume(self, value):
        self.msc.set_volume(value / 100)
        self.currvol = value / 100
        if self.currvol == 0:
            self.pushButton_6.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
            self.pushButton_6.setEnabled(False)
        else:
            self.pushButton_6.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
            self.pushButton_6.setEnabled(True)

    def change_value_song(self, value):
        if self.horizontalSlider_2.isSliderDown() and self.songs:
            self.msc.stop()
            self.count_for_timer = value
            self.msc.load(self.currsong)
            self.msc.play(start=value)

    def skipForw(self):
        if not self.is_stoped:
            self.msc.stop()
            self.timer.stop()
            if self.currsong == self.songs[-1]:
                self.currsong_ind = 0
                self.currsong = self.songs[self.currsong_ind]
                self.currsong_list = self.songs_path[self.currsong_ind]
                self.play1 = 0
            else:
                self.currsong_ind += 1
                self.currsong = self.songs[self.currsong_ind]
                self.currsong_list = self.songs_path[self.currsong_ind]
                self.msc.load(self.currsong)
                self.msc.play()
            self.play = 0
            self.count_for_timer = 0
            self.end = 0
            self.lcdNumber.display('00:00')
            self.play_func()

    def skipBack(self):
        if not self.is_stoped:
            self.msc.stop()
            self.timer.stop()
            if self.currsong == self.songs[0]:
                self.currsong_ind = len(self.songs) - 1
                self.currsong = self.songs[self.currsong_ind]
                self.currsong_list = self.songs_path[self.currsong_ind]
                self.play = 0

            else:
                self.currsong_ind -= 1
                self.currsong = self.songs[self.currsong_ind]
                self.currsong_list = self.songs_path[self.currsong_ind]
                self.play = 0
            self.msc.load(self.currsong)
            self.msc.play()
            self.count_for_timer = 0
            self.end = 0
            self.play_func()

    def stop(self):
        if self.songs:
            self.msc.stop()
            self.timer.stop()
            self.play = 0
            self.play1 = 0
            self.count = 0
            self.count_for_vol = 0
            self.count_for_timer = 0
            self.msc.set_volume(self.currvol)
            self.lcdNumber.display('00:00')
            self.currsong, self.currsong_ind, self.currsong_list = self.songs[0], 0, self.songs_path[0]
            self.label_2.setText('')
            self.is_stoped = True
            self.horizontalSlider_2.setSliderPosition(0)
            self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.pushButton_6.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
            self.msc.stop()

    def download(self):
        dl = QFileDialog.getOpenFileName(self, 'Загрузить песню', '', '*.mp3')[0].split('/')[-1]
        if dl != '':
            self.songs.append(get_song(dl))
            self.songs_path.append(dl)
            self.listWidget.addItem(dl)

    def other_song(self, item):
        if not self.is_stoped:
            it = item.text()

            self.msc.stop()
            self.count_for_timer = 0
            self.timer.stop()
            self.play = 0
            self.currsong_ind = self.songs.index(get_song(it))
            self.currsong = self.songs[self.currsong_ind]
            self.currsong_list = self.songs_path[self.currsong_ind]

            self.lcdNumber.display('00:00')
            self.msc.load(get_song(it))
            self.msc.play()
            self.play_func()

    def download_youtube(self):
        webbrowser.open('https://www.converto.io/ru21')

    def create_playlist(self):
        self.createplaylist.show()

    def open_playlist(self):
        self.openplaylist.show()
        self.openplaylist.get_pl_names()

    def lcd(self):
        self.lcdNumber.display(str(self.count_for_timer))
        leng = self.end
        minutes = leng // 60
        secs = leng % 60
        hours = 0
        if minutes >= 60:
            hours //= minutes
        minutes_now = self.count_for_timer // 60
        secs_now = self.count_for_timer % 60
        hours_now = 0
        if minutes_now >= 60:
            hours_now = minutes_now // 60
            minutes_now = minutes_now % 60
        secs_now = str(secs_now).rjust(2, '0')
        minutes_now = str(minutes_now).rjust(2, '0')
        hours_now = str(hours_now).rjust(2, '0')
        self.lcdNumber.display(f'{hours_now}:{minutes_now}:{secs_now}')

    def random(self):
        if self.songs:
            self.listWidget.clear()
            self.label_2.setText('')
            self.lcdNumber.display('00:00')
            self.msc.stop()
            self.timer.stop()
            self.count = 0
            self.is_stoped = True
            self.pushButton_2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            shuffle(self.songs)
            list_ = []
            len_ = len([i for i in get_song('')])
            for i in self.songs:
                i = i[len_:]
                for j in self.songs_path:
                    if i == j:
                        list_.append(j)
            self.songs_path = list_[:]
            list_ = []
            print(self.songs_path)
            for i in self.songs_path:
                self.listWidget.addItem(i)
            self.currsong_ind = 0
            self.currsong = self.songs[self.currsong_ind]
            self.currsong_list = self.songs_path[self.currsong_ind]
            self.play = 0
            self.play1 = 0
            self.play_func()

    def style_(self):
        if self.count_for_style == 0:
            self.setStyleSheet('background-color: black')
            self.pushButton_2.setStyleSheet('background-color: white')
            self.pushButton_6.setStyleSheet('background-color: white')
            self.horizontalSlider.setStyleSheet('background-color: white')
            self.horizontalSlider_2.setStyleSheet('background-color: white')
            self.pushButton.setStyleSheet('background-color: white')
            self.pushButton_3.setStyleSheet('background-color: white')
            self.pushButton_4.setStyleSheet('background-color: white')
            self.pushButton_12.setStyleSheet('background-color: white')
            self.pushButton_5.setStyleSheet('background-color: white')
            self.pushButton_7.setStyleSheet('background-color: white')
            self.pushButton_8.setStyleSheet('background-color: white')
            self.pushButton_9.setStyleSheet('background-color: white')
            self.lcdNumber.setStyleSheet('background-color: white')
            self.listWidget.setStyleSheet('background-color: white')
            self.label_2.setStyleSheet('background-color: white')
            self.pushButton_13.setStyleSheet('background-color: white')

            self.count_for_style += 1
        else:
            self.setStyleSheet('background-color: white')
            self.pushButton_2.setStyleSheet('background-color: white')
            self.pushButton_6.setStyleSheet('background-color: white')
            self.horizontalSlider.setStyleSheet('background-color: white')
            self.horizontalSlider_2.setStyleSheet('background-color: white')
            self.pushButton.setStyleSheet('background-color: white')
            self.pushButton_3.setStyleSheet('background-color: white')
            self.pushButton_4.setStyleSheet('background-color: white')
            self.pushButton_12.setStyleSheet('background-color: white')
            self.pushButton_5.setStyleSheet('background-color: white')
            self.pushButton_7.setStyleSheet('background-color: white')
            self.pushButton_8.setStyleSheet('background-color: white')
            self.pushButton_9.setStyleSheet('background-color: white')
            self.lcdNumber.setStyleSheet('background-color: white')
            self.listWidget.setStyleSheet('background-color: white')
            self.label_2.setStyleSheet('background-color: white')
            self.pushButton_13.setStyleSheet('background-color: white')

            self.count_for_style -= 1


class CreatePlaylist(QWidget, Ui1):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('CreatePlaylist')
        self.name = ''

        self.songs_list = []

        self.pushButton.clicked.connect(self.confirm)

        self.pushButton_2.clicked.connect(self.cancel)

        self.pushButton_3.clicked.connect(self.download)

        self.pushButton_4.clicked.connect(self.delete)

    def cancel(self):
        self.songs_list = []
        self.listWidget.clear()
        self.close()

    def confirm(self):
        self.tl = self.lineEdit.text()
        if self.songs_list:
            try:
                if self.tl:
                    self.name = self.tl
                else:
                    self.name = 'Playlist'
                    db = sqlite3.connect('playlists.db')
                    cursor = db.cursor()
                    count = cursor.execute('''SELECT count FROM count_list''').fetchall()[0]
                    self.name = self.name + str(count[0])
                    cursor.execute(f'''UPDATE count_list
                                       SET count = {count[0] + 1}''')
                    db.commit()
                    db.close()
                conn = sqlite3.connect('playlists.db')
                cur = conn.cursor()
                cur.execute(f'''CREATE TABLE {self.name}(
                                    song_name STRING);''')
                conn.commit()
                cur.execute(f'''INSERT INTO playlist_names(playlist_name) VALUES('{self.name}')''')
                conn.commit()
                for i in self.songs_list:
                    cur.execute(f'''INSERT INTO {self.name}(song_name) VALUES('{i}')''')
                    conn.commit()
                conn.close()

                self.listWidget.clear()
                self.close()
            except (sqlite3.OperationalError):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('Плейлист с таким именем уже существует')
                msg.setWindowTitle("Error")
                msg.exec_()

    def download(self):
        dl = QFileDialog.getOpenFileName(self, 'Загрузить песню', '', '*.mp3')[0].split('/')[-1]
        if dl != '':
            self.songs_list.append(dl)
            self.listWidget.addItem(dl)

    def delete(self):
        listItems = self.listWidget.selectedItems()
        for item in listItems:
            self.listWidget.takeItem(self.listWidget.row(item))
            self.songs_list.remove(item.text())


class OpenPlayList(QWidget, Ui2):
    def __init__(self, pl=None):
        super().__init__()
        self.setupUi(self)
        self.sl = []
        self.playlist_names = []
        self.pl = pl
        self.setWindowTitle('Playlist')
        self.songsinplaylist = SongsInPlaylist()

        self.listWidget.itemActivated.connect(self.dl_playlist)

        self.pushButton_2.clicked.connect(self.cancel)

        self.pushButton_3.clicked.connect(self.open_pl)

        self.pushButton_4.clicked.connect(self.delete_pl)

    def get_pl_names(self):
        self.listWidget.clear()
        conn = sqlite3.connect('playlists.db')
        cur = conn.cursor()
        text = cur.execute('''SELECT playlist_name FROM playlist_names''').fetchall()
        for i in text:
            self.playlist_names.append(i[0])
            self.listWidget.addItem(i[0])
        conn.close()

    def dl_playlist(self, listitem):
        con = sqlite3.connect('playlists.db')
        cur = con.cursor()
        text = cur.execute(f'''SELECT song_name FROM {listitem.text()}''').fetchall()
        self.pl.get(text)
        con.close()

    def cancel(self):
        self.listWidget.clear()
        self.playlist_names = []
        self.close()

    def open_pl(self):
        listItems = self.listWidget.selectedItems()
        for i in listItems:
            self.songsinplaylist.get(i)
            self.songsinplaylist.show()

    def delete_pl(self):
        listItems = self.listWidget.selectedItems()
        for item in listItems:
            self.listWidget.takeItem(self.listWidget.row(item))
            self.playlist_names.remove(item.text())
            conn = sqlite3.connect('playlists.db')
            cur = conn.cursor()
            cur.execute(f'''DELETE FROM playlist_names
                                WHERE playlist_name = '{item.text()}' ''')
            conn.commit()
            cur.execute(f'''DROP TABLE {item.text()}''')
            conn.close()


class SongsInPlaylist(QWidget, Ui3):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Songs in playlist')
        self.song_names = []

        self.pushButton.clicked.connect(self.back)

        self.pushButton_2.clicked.connect(self.delete)

        self.pushButton_3.clicked.connect(self.add)

    def get(self, item):
        self.listWidget.clear()
        self.playlist_name = item.text()
        con = sqlite3.connect('playlists.db')
        cur = con.cursor()
        names = cur.execute(f'''SELECT song_name FROM {item.text()}''').fetchall()
        for i in names:
            self.listWidget.addItem(i[0])
            self.song_names.append(i[0])

    def back(self):
        self.listWidget.clear()
        self.song_names = []
        self.close()

    def delete(self):
        listItems = self.listWidget.selectedItems()
        for item in listItems:
            self.listWidget.takeItem(self.listWidget.row(item))
            self.song_names.remove(item.text())
            conn = sqlite3.connect('playlists.db')
            cur = conn.cursor()
            cur.execute(f'''DELETE FROM {self.playlist_name}
                                WHERE song_name = '{item.text()}' ''')
            conn.commit()
            conn.close()

    def add(self):
        dl = QFileDialog.getOpenFileName(self, 'Загрузить песню', '', '*.mp3')[0].split('/')[-1]
        con = sqlite3.connect('playlists.db')
        cur = con.cursor()
        if dl != '':
            self.song_names.append(dl)
            self.listWidget.addItem(dl)
            cur.execute(f'''INSERT INTO {self.playlist_name}(song_name) VALUES('{dl}')''')
            con.commit()
        con.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Mp3Player()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
