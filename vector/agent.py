""""
HRI-cookingを行う上で必要な、ベクターの動きを定義するクラス
"""
import anki_vector
from anki_vector.util import degrees
import cv2
import dlib
import difflib
from vector import listen
import itertools
import math
import nep
import nltk
import pandas as pd
import speech_recognition as sr # 音声認識を行うためのライブラリ
import time
from resources import utility

VECTOR = '[Vector]'

# 準備
args = anki_vector.util.parse_command_args()
HEAD_ANGLE = 45.0


class Agent:
    def __init__(self, robot,  pub_emo="", pub_say="", pub_subemo=""):
        self.r = sr.Recognizer()
        self.robot = robot
        self.face_to_follow = None
        self.pub_emo = pub_emo
        self.pub_subemo = pub_subemo
        self.pub_say = pub_say
        self.listen = listen.Listen(pub_emo, pub_say, pub_subemo)
        self.no_emotion = False
        # csvファイルからデータを取得
        csvfile = utility.CsvFile('Menu_selection.csv')
        self.all_data = csvfile.read_all_data()

    def recognize_what_saying(self, state_num):
        """料理をしている最中に人間が言ったことが、何を示しているのかを認識して、
        それに合った行動をする
        """
        while True:
            event = self.listen.during_cook()
            if event == 'OK':
                self.pub_emo.publish('giggle')
                time.sleep(2)
            if event == 'next':
                next_state_num = self.instruct(state_num)
                break
            if event == 'again':
                state_num = self.instruct(state_num - 1)
            else:
                pass
        return next_state_num

    def greeting(self):
        """挨拶をして名前を聞く。名前は繰り返して確認する"""
        text = "Hello, I'm Vector."
        self.smile_and_say(text)
        print(VECTOR + text)
        # self.pub_subemo.publish('record')
        self.pub_emo.publish("greeting")
        time.sleep(2)
        text = "What's your name?"
        self.pub_say.publish(text)
        print(VECTOR + text)
        # self.pub_emo.publish("listen")
        time.sleep(2)  # no_emotionのときは、2秒くらいがいいかも
        user = self.listen.get_name()
        time.sleep(6)
        confirmed_user = ""
        while True:
            self.pub_say.publish("Your name is " + user + ", right?")
            # self.pub_emo.publish("listen")
            time.sleep(3)
            response = self.listen.ask_yes_no_name()
            if response == 'yes':
                if confirmed_user:
                    pass
                else:
                    confirmed_user = user
                break
            elif response:  # userの名前も言った場合
                user = response
            elif response == 'sorry' :
                pass
            else:  # Noのみだった場合
                confirmed_user = ""
                self.pub_say.publish("What's your name?")
                # self.pub_emo.publish("listen")
                time.sleep(1)
                user = self.listen.get_name()
                time.sleep(5)
        confirmed_user = user.replace(', ', ' ')
        self.listen.first_name = confirmed_user.split(" ")[0]
        return confirmed_user

    def let_make_menu(self, user):
        """メニューを作ろう！という"""
        # ユーザー名で条件指定して、レコードデータを取得
        record = self.all_data.query('Name == @user')

        # データを整形
        menu = record.loc[:, record.columns.str.contains('Menu')]
        menu = menu.reset_index(drop=True)
        menu = menu.dropna(axis=1)

        # メニューを取得
        menu = menu.iat[0, 0]
        menu = menu.capitalize()
        first_name = user.split(' ')[0]
        self.pub_say.publish("Okay{}, let's make {} ".format(first_name, menu))
        self.pub_emo.publish("say")
        time.sleep(3)
        return menu

    def pass_info(self, procedures, policy):
        self.procedures = procedures
        self.policy = policy

    def ask_menu(self):
        """何を作るかを聞く"""
        text = 'What do you make?'
        self.pub_say.publish(text)
        print(VECTOR + text)
        # self.pub_emo.publish("listen")
        menu = self.listen.get_menu()
        print(menu)
        return menu

    def suggest(self, my_data, suggest_ingredients):
        """使う材料を表示して、新しい材料を提案する"""
        new_ingredients = []
        # 既存の材料を述べる
        ingredients = utility.RecipeData().get_ingredients(my_data)
        text_ingredients = ingredients[0] + ', '
        for n, ingredient in enumerate(ingredients):
            if n == len(ingredients) - 2:
                break
            elif n == 0:
                continue
            tmp = ingredient + ', '
            text_ingredients += tmp
        text_ingredients += 'and '+ ingredients[-1]
        # text_ingredients = ', '.join(ingredients)
        text = "Today's ingredients are " + text_ingredients + '.'
        self.pub_say.publish(text)
        print(VECTOR + text)
        self.pub_emo.publish('lift')
        time.sleep(2.5 + len(ingredients))

        # 材料の提案
        for ing in suggest_ingredients:
            while True:
                text = 'Do you want to add ' + ing + '?'
                self.pub_say.publish(text)
                self.pub_emo.publish('curious')
                time.sleep(3)
                response = self.listen.ask_yes_no()
                if response == 'yes':
                    new_ingredients.append(ing)
                    if ing != suggest_ingredients[-1]:
                        self.smile_and_say('OK,')
                        break
                    else:
                        break
                elif response == 'no':
                    if ing != suggest_ingredients[-1]:
                        self.sad_and_say('OK,')
                        break
                    else:
                        break
                elif response == 'again':
                    continue
                else:
                    continue
        if len(new_ingredients) == 2:
            self.pub_say.publish("OK, let's use " + new_ingredients[0] + ' and '
                                 + new_ingredients[1])
            self.pub_emo.publish("say")
            num = 3
        elif len(new_ingredients) == 1:
            self.pub_say.publish("OK, let's use " + new_ingredients[0])
            self.pub_emo.publish("say")
            print(new_ingredients)
            print(ingredients)
            if new_ingredients[0] == suggest_ingredients[0]:
                num = 1
            if new_ingredients[0] == suggest_ingredients[1]:
                num = 2
        else:
            self.sad_and_say("OK, we will not use new ingredients.")
            num = 0
        return str(num)

    def thinking(self):
        """ちょっと考え中"""
        self.pub_emo.publish('thinking')

    def smile_and_say(self, text=""):
        self.pub_say.publish(text)
        self.pub_emo.publish("smile")

        if text != "":
            print(VECTOR + text)
        time.sleep(2)

    def pleasure_and_say(self, text=""):
        self.pub_say.publish(text)
        self.pub_emo.publish("pleasure")
        if text != "":
            print(VECTOR + text)
        time.sleep(len(text)/2)  # すぐ次に行ってしまうので待ち時間が必要

    def crack_and_say(self, text=""):
        self.pub_say.publish(text)
        self.pub_emo.publish("crack")
        if text != "":
            print(VECTOR + text)
        time.sleep(len(text)/2)  # すぐ次に行ってしまうので待ち時間が必要

    def sad_and_say(self, text=""):
        self.pub_say.publish(text)
        self.pub_emo.publish('sad')
        print(VECTOR + text)
        time.sleep(3)

    def heat_and_say(self, text=""):
        """加熱する系のベクターの動作"""
        self.pub_say.publish(text)
        self.pub_emo.publish("heat")
        if text == "":
            print(VECTOR + text)
        time.sleep(2)
        self.pub_emo.publish('giggle')
        # self.smile_and_say()

    def cut_and_say(self, text=""):
        """切る系のベクターの動作"""
        self.pub_say.publish(text)
        self.pub_emo.publish("cut")
        time.sleep(2)
        self.pub_subemo.publish("cut")
        if text == "":
            print(VECTOR + text)
        time.sleep(2)

    def put_and_say(self, text=""):
        """入れる系のベクターの動作"""
        self.pub_emo.publish("put")
        time.sleep(2)
        # self.robot.say_text(text)
        self.smile_and_say(text)

    def mix_and_say(self, text=""):
        """混ぜる系のベクターの動作"""
        self.pub_say.publish(text)
        self.pub_emo.publish("mix")
        time.sleep(5)
        self.pub_subemo.publish("mix")
        if text == "":
            print(VECTOR + text)
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))

    def mix2_and_say(self, text=""):
        """混ぜる系のベクターの動作"""
        self.pub_emo.publish('mix2')
        if text == "":
            print(VECTOR + text)
        time.sleep(3)
        self.smile_and_say(text)
        self.robot.behavior.set_head_angle(degrees(40.0))

    def finish_and_say(self, text="Finish!"):
        # self.pub_emo.publish("finish")
        # print(VECTOR + text)
        # time.sleep(10)
        # self.smile_and_say(text)
        self.pleasure_and_say(text)

    def start(self):
        self.smile_and_say('Let\'s start!')

    def instruct(self, state_num):
        """手順を指示する。確率が高いものを順に言っていく"""
        print(state_num)
        max_index = self.policy[state_num].index(max(self.policy[state_num]))
        print(max(self.policy[state_num]))
        next_state = self.procedures[max_index]
        next_state = next_state.lower()
        # if max_index == len(self.policy) - 1:
        #     self.finish_and_say("Finish!")
            # next_state_num = len(policy) - 1

        if 'mix' in next_state:
            self.mix_and_say(next_state)  # TODO try to change to mix2
        elif 'crack' in next_state:
            self.crack_and_say(next_state)
        elif 'heat' in next_state or 'boil' in next_state:
            self.heat_and_say(next_state)
            # next_state_num = procedures.index(next_state)
        elif 'put' in next_state:
            self.put_and_say(next_state)
        elif 'cut' in next_state or 'mince' in next_state:
            self.cut_and_say(next_state)
        elif 'finish' in next_state:
            pass
        else:
            self.smile_and_say(next_state)
        # print(len(next_state))
        time.sleep(len(next_state)/14)
        next_state = next_state.capitalize()
        next_state_num = self.procedures.index(next_state)
        return next_state_num

    def stand_by(self):
        self.robot.behavior.set_lift_height(0.0)
        self.robot.behavior.set_head_angle(degrees(40.0))
        if self.no_emotion:
            self.pub_emo.publish("curious")

    def face_direction(self, img):
        """ 顔姿勢の検出
        :return theta: direction of face
        """
        ORG_WINDOW_NAME = "org"
        # 準備 #
        predictor = dlib.shape_predictor(
            "shape_predictor_68_face_landmarks.dat")
        detector = dlib.get_frontal_face_detector()
        theta = 40

        # 検出 #
        dets = detector(img, 1)

        for k, d in enumerate(dets):
            shape = predictor(img, d)

            # 顔領域の表示
            color_f = (0, 0, 225)
            color_l_out = (255, 0, 0)
            color_l_in = (0, 255, 0)
            line_w = 3
            circle_r = 3
            fontType = cv2.FONT_HERSHEY_SIMPLEX
            fontSize = 1

            # 重心を導出する箱を用意
            num_of_points_out = 17
            num_of_points_in = shape.num_parts - num_of_points_out
            gx_out = 0
            gy_out = 0
            gx_in = 0
            gy_in = 0
            for shape_point_count in range(shape.num_parts):
                shape_point = shape.part(shape_point_count)
                # print("顔器官No.{} 座標位置: ({},{})".format(shape_point_count, shape_point.x, shape_point.y))
                # 器官ごとに描画
                if shape_point_count < num_of_points_out:
                    # cv2.circle(img, (shape_point.x, shape_point.y), circle_r,
                    #            color_l_out, line_w)
                    gx_out = gx_out + shape_point.x / num_of_points_out
                    gy_out = gy_out + shape_point.y / num_of_points_out
                else:
                    # cv2.circle(img, (shape_point.x, shape_point.y), circle_r,
                    #            color_l_in, line_w)
                    gx_in = gx_in + shape_point.x / num_of_points_in
                    gy_in = gy_in + shape_point.y / num_of_points_in

            # 顔の方位を計算
            radian = math.asin(2 * (gx_in - gx_out) / (d.right() - d.left()))
            theta = radian * 180 / math.pi
            print("顔方位:{} (角度:{}度)".format(radian, theta))

        if theta is None:  # theta がNoneだとまずいから
            theta = 40
        # cv2.imshow(GAUSSIAN_WINDOW_NAME, img_gray)
        return theta, img


def main():
    msg_type = "string"
    node = nep.node("brain_pub")
    pub_emo = node.new_pub("brain_emo", msg_type)
    pub_say = node.new_pub("brain_say", msg_type)
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial) as robot:
        vector = Agent(robot, pub_emo=pub_emo, pub_say=pub_say)
        vector.smile_and_say("Hello world")


if __name__ == '__main__':
    main()