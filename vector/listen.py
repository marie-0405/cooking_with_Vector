""""
音声認識のためのモジュール
ベクターには接続していないため、独立
"""
import difflib
import itertools
import nltk
import pyaudio
import speech_recognition as sr # 音声認識を行うためのライブラリ
from resources import utility
import time


# 準備
device_id = 1  # 1: Web camera
r = sr.Recognizer()
mic = sr.Microphone(device_index=device_id)


class Listen():
    def __init__(self, pub_emo="", pub_say="", pub_subemo = "", language='en'):
        self.language = language
        self.first_name = "You"
        self.pub_emo = pub_emo
        self.pub_say = pub_say
        self.pub_subemo = pub_subemo

    def _speech_to_text(self, record=True):
        """
        :param thinking: if Vector thinking or not.
        :param second_ask:
        :return:
        """
        # results = input()
        while True:
            with mic as source:
                r.adjust_for_ambient_noise(source, duration=0.8)  # 雑音対策
                print("Say...")
                self.pub_emo.publish("listen")
                time.sleep(0.7)
                # self.robot.audio.stream_wav_file("vector_bell_whistle.wav", 100)
                audio = r.listen(source)
                print("Now to recognize it...")
            try:
                if record:
                    self.pub_subemo.publish('record')
                results = r.recognize_google(audio, language=self.language)
                print('['+ self.first_name + ']', results)
                self.pub_emo.publish("curious")
                break
            except sr.RequestError as e:
                print("Could not request results from Google Speech "
                      "Recognition service; {0}".format(e))
                results = ""
            except sr.UnknownValueError as e:
                print("UnknownValueError")
                # pub_say.publish('One more please')
                results = ""
        morph = nltk.word_tokenize(results)
        pos = nltk.pos_tag(morph)
        return results, pos

    def during_cook(self):
        """テキストから、人間の意図を読み取る
        ①次の手順は？(What is the next?)
        ②え？(Sorry, Excuse me?)"""
        text, pos = self._speech_to_text(record=True)  # TODO
        event = ""
        # if self.language == 'ja':
        #     # text = utility.convert_to_hira(text)
        #     print(text)
        # if self.language == 'en':
        text = text.lower()
        if 'next' in text:
            event = 'next'
        elif 'sorry' in text or 'excuse' in text:
            event = 'again'
        elif 'okay' in text or 'OK' in text:
            event = 'OK'
        return event

    def extract_name(self, pos):
        user = ""
        for i in range(len(pos)):
            if 'NN' in pos[i][1]:
                if 'name' != pos[i][0]:
                    user += pos[i][0] + " "
        user = user.rstrip(" ")
        user = user.title()
        return user

    def get_name(self, name=""):
        """事前アンケートファイルの名前を取得して、その名前とあいまい検索の中で
        最も確率が高い名前を選択する"""
        if not name:
            results, pos = self._speech_to_text()
            user = self.extract_name(pos)
        else:
            user = name
        self.pub_emo.publish("thinking")
        user_file = utility.UserData('Menu_selection.csv')
        user_data = user_file.read_all_data()
        confirmed_username = user_file.get_name(user_data, user)
        # スペースを「, 」に置き換える(ベクターが発音しやすくするため）
        confirmed_username = confirmed_username.replace(" ", ", ")
        return confirmed_username

    def ask_yes_no(self):
        results, pos = self._speech_to_text(record=True)  # TODO
        if 'yes' in results or 'yeah' in results:
            return 'yes'
        elif 'no' in results:
            return 'no'
        elif 'excuse' in results or 'sorry'in results:
            return 'again'
        else:
            return 'again'

    def ask_yes_no_name(self):
        results, pos = self._speech_to_text(record=True)   # TODO
        print(results)
        if 'yes' in results or 'yeah' in results:
            return 'yes'
        if 'sorry' in results:
            return 'sorry'
        else:
            user = self.extract_name(pos)
            if user:
                user = self.get_name(user)
                return user
            else:
                return False


if __name__ == '__main__':
    audio = pyaudio.PyAudio()
    for i in range(audio.get_device_count()):
        print(audio.get_device_info_by_index(i))
    listen = Listen()
    speech = listen._speech_to_text()
    # print(speech)