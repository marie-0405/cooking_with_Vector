""""
レシピデータに関するプログラム。
保存、読み込み、リスト化などを行う。
"""
import csv
import codecs
import difflib
from googletrans import Translator
import itertools
import json
import math
import nltk
import numpy as np
import os
from pykakasi import kakasi
import pandas as pd
import time
import urllib



MY_RECIPE_DATA = 'my_recipe.csv'


def trans_to_ja(english):
    while True:
        time.sleep(1)
        tr = Translator(service_urls=['translate.googleapis.com'])
        # tr = Translator()
        try:
            text = tr.translate(english, src='en', dest="ja").text
            print(tr.detect(text).lang)
            # if tr.detect(text).lang == 'ja':
            break
        except Exception as e:
            time.sleep(2)
            print(e)
            tr = Translator(service_urls=['translate.googleapis.com'])
            print("error")
    return text


def trans_to_en(japanese):
    tr = Translator(service_urls=['translate.googleapis.com'])
    while True:
        try:
            text = tr.translate(japanese, src='ja', dest="en").text
            break
        except Exception as e:
            time.sleep(1)
            tr = Translator(service_urls=['translate.googleapis.com'])
    return text


def convert_to_hira(kanji):
    """カタカナも漢字も全てひらがなに変換"""
    # オブジェクトをインスタンス化
    kaka = kakasi()
    # モードの設定：J(Kanji) to H(Hiragana)
    kaka.setMode('J', 'H')
    # 変換して出力
    conv = kaka.getConverter()
    kata = conv.do(kanji)

    kaka.setMode('K', 'H')
    conv = kaka.getConverter()
    hira = conv.do(kata)
    return hira


def convert_kata_to_hira(kanji):
    """カタカナを全てひらがなに変換"""
    # オブジェクトをインスタンス化
    kaka = kakasi()
    # モードの設定：J(Kanji) to H(Hiragana)
    kaka.setMode('K', 'H')
    # 変換して出力
    conv = kaka.getConverter()
    hira = conv.do(kanji)
    return hira


def convert_to_kanji(hira):
    """全て漢字に変換"""
    url = "http://www.google.com/transliterate?"
    param = {'langpair': 'ja-Hira|ja', 'text': hira}
    paramStr = urllib.parse.urlencode(param)
    # print(url + paramStr)
    readObj = urllib.request.urlopen(url + paramStr)
    response = readObj.read()
    data = json.loads(response)
    fixed_data = json.loads(json.dumps(data[0], ensure_ascii=False))
    return fixed_data[1][0]


class CsvFile():
    def __init__(self, file_name, *args, **kwargs):
        resource_dir = self._get_resource_dir_path()
        # print(args)
        self.file_name = resource_dir + '\\' + file_name
        if len(args) > 1: # argsに値があったら
            self.columns = args
        else:
            self.columns = self._get_columns()

    def _get_columns(self):
        # カラム名を取得する
        recipe_data = pd.read_csv(self.file_name, encoding="shift-jis")
        return recipe_data.columns

    def _get_resource_dir_path(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        resources_dir_path = os.path.join(base_dir, 'resources')
        # print(resources_dir_path)
        return resources_dir_path

    def read_all_data(self):
        all_data = pd.read_csv(self.file_name, encoding="shift-jis")
        return all_data


class UserData(CsvFile):
    def __init__(self, file_name, *args, **kwargs):
        super().__init__(file_name, *args, **kwargs)

    def get_name(self, all_data, user):
        """csv ファイルから曖昧検索して、最もrateの高い名前を正解とする"""
        # csvファイルから名前のリストを検索
        name_list = all_data.loc[:, all_data.columns.str.contains('Name')]

        # データの整形
        name_list = name_list.dropna()  # 欠損値があったらdrop
        name_list = name_list.values.tolist()  # でーたふれーむからリストへ変換
        name_list = list(itertools.chain.from_iterable(name_list))  # 2次元リストを平坦化
        dic_name_rate = {}
        user_len = len(user)
        confirmed_user = ""
        for name in name_list:
            name_len = len(name)
            name = name.title()
            if name_len - user_len == -1:
                # range()の中身が0になってしまうので、普通に検索する
                rate = difflib.SequenceMatcher(None, user, name).ratio()
            else:
                # リストの小さい方の長さ分ずつ比較して、最大値をとる
                rate = max([difflib.SequenceMatcher(None, user, name[
                                                                i:i + user_len]).ratio()
                            for i in range(abs(name_len - user_len + 1))])
            print(name, rate)
            dic_name_rate[name] = rate
        confirmed_user = max(dic_name_rate, key=dic_name_rate.get)
        self.user = confirmed_user
        return confirmed_user


class RecipeData(CsvFile):
    def __init__(self, file_name=MY_RECIPE_DATA, *args, **kwargs):
        super().__init__(file_name, *args, **kwargs)

    def save(self, data):
        """レシピデータをメニューごとに保存する。辞書型でない場合は、辞書型
        に変更する。辞書型やリスト型で受け取る場合がある."""
        if type(data) is list:
            dict_data = dict(zip(self.columns, data))
        else:
            dict_data = data
        menu = dict_data['MENU']
        del dict_data["MENU"]
        # print(dict_data)
        if not os.path.exists(self.file_name):
            df = pd.DataFrame(dict_data.values(), index=dict_data.keys()).T
            df = df.set_index(self.columns[0])
            df.to_csv(self.file_name, encoding='Shift-JIS')
        else:
            with codecs.open(self.file_name, "r", "Shift-JIS",
                             "ignore") as file:
                recipe_data = pd.read_csv(file, index_col=0)  # MENUをindexとして読み込む
            recipe_data = recipe_data.fillna("")  # 欠損値を空白文字列で埋める
            # print(recipe_data)
            # print(len(recipe_data.columns))
            recipe_data.loc[menu] = dict_data  # MENU以降を変更する
            recipe_data.to_csv(self.file_name, encoding='Shift-JIS')

    def load(self, menu):
        """特定のメニューのデータ1行分のみ取得する
        辞書型で返す"""
        # print(resource_dir + '\\' + self.file_name)
        with codecs.open(self.file_name, "r", "Shift-JIS", "ignore") as file:
            all_data = pd.read_csv(file, index_col=0)
        all_data = all_data.fillna("")
        recipe_data = all_data.loc[menu]
        recipe_data = recipe_data.to_dict()  # 辞書型で取得する
        # print(recipe_data)
        for i, column in enumerate(self.columns):  # カラム分回して、全てリストにする
            # print("recipe_data", recipe_data[i])

            if column == 'MENU' or i >= 10:
                pass
            elif 'POLICY' in column:
                if not recipe_data[column] == np.nan:
                    # print(column)
                    recipe_data[column] = self._convert_int_from_str(recipe_data[column])
                else:
                    pass
            else:
                recipe_data[column] = self._convert_list_from_str(recipe_data[column])
        return recipe_data

    def get_menu(self):
        """全てのメニュー名を取得する"""
        with codecs.open(self.file_name, "r", "Shift-JIS", "ignore") as file:
            all_data = pd.read_csv(file, index_col=0)
        return all_data.index.values

    def get_ingredients(self, dic_recipe, translate=False):
        """辞書型のレシピデータから、材料リストを英語で作成する。"""
        ingredients = dic_recipe['SOLID'] + dic_recipe['LIQUID'] + dic_recipe['SEASONING']
        ingredients = [a for a in ingredients if a != '']  # 空の要素削除
        # print(ingredients)
        if translate:
            # 日本語に翻訳する
            trans_ingredients = []
            # while True:
            for ingredient in ingredients:
                trans_ingredients.append(trans_to_ja(ingredient))
            ingredients = trans_ingredients
                    # print(ingredients)
                    # print(type(ingredients))
                # tr = Translator(service_urls=['translate.googleapis.com'])
                # detected = tr.detect(ingredients[0])
                    # print(detected)
                # if detected.lang == 'ja':
                #     break
        return ingredients

    def _convert_int_from_str(self, policy):
        """文字列で保存されたリスト（[]含む）をint型に変換する"""
        policy = [i for i in policy if i != '[' and i != ', ' and i != ',']   # 記号を取り除く
        if len(policy):
            del policy[-1]
            # print("削除")
        # policy = policy.replace('\n', '')
        # print(policy)
        new_policy = [[]] # 変換に用いる方策
        j = 0
        for i in range(len(policy)):  #リストに変換する
            if i == len(policy) - 1:
                break
            if policy[i] == ']':
                new_policy.append([])
                j += 1
                continue
            new_policy[j].append(policy[i])
        policy = [[]]  # 最終的な方策
        for i in range(len(new_policy)):
            if i != 0:
                policy.append([])
            # print(new_policy[i])
            new_policy[i] = ''.join(new_policy[i])  # 全てジョインする
            # print(new_policy[i])
            new_policy[i] = new_policy[i].split()  # リストに分ける
            # print(new_policy)
            for j in range(len(new_policy[i])):
                # print(new_policy[i][j])
                new_policy[i][j] = float(new_policy[i][j])  # float型にする
            policy[i] = new_policy[i]
        return policy

    def _convert_list_from_str(self, string):
        """文字列型からリスト型に変換する"""
        # 記号を取り除く
        string_data = [s for s in string if s != '[' and s != ']' and s != '\'']
        # print(string_data)
        string_data = ''.join(string_data)
        # print(string_data)
        list_data = string_data.split(', ')
        # print(list_data)
        return list_data


def main():
    print(convert_to_hira("あいうえお"))


if __name__ == '__main__':
    main()
