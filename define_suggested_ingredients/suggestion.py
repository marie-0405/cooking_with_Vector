import codecs
import difflib
import matplotlib.pyplot as plt
import mysql.connector
import numpy as np
import pandas as pd
import pandas.io.sql as psql
from resources import utility
import re


def delete_symbol(text):
    new_text = ""
    for t in text:
        if t == '●' or t == '○' or t == '＊' or t == '◆' or t == '★'\
                or t == '☆' or t == '＜' or t == '＞' or t == '\u3000'\
                or t == '・':
            pass
        else:
            new_text += t
    return new_text


def join_ingredient(list_ingredients):
    """材料名の一致を調べるために、|区切りで材料を結合する"""
    ingredients = ""
    for i in range(len(list_ingredients)):
        if i == 0:
            ingredients = list_ingredients[i]
        else:
            ingredients += "|" + list_ingredients[i]
    return ingredients


def grouped(raw_data, title, list_ingredients):
    """メニュー名とカテゴリー名の一致によって抽出を行った後、
    全ての材料が入っているものを抽出する"""
    # カテゴリ名で条件を絞る  # TODO 曖昧検索でtitleを絞る
    grouped_by_title = raw_data.query('title.str.contains(@title, na=False) ', engine='python')  # , engine='python'
    # print('grouped_by_title', grouped_by_title)
    grouped_by_title = grouped_by_title.reset_index(drop=True)
    # 材料名で条件を絞る
    ingredients = join_ingredient(list_ingredients)
    grouped_by_ingredients = grouped_by_title.query('ingredient.str.contains(@ingredients, na=False) ', engine='python')
    grouped_by_ingredients = grouped_by_ingredients.reset_index(drop=True)
    # print('grouped_by_ingredients', grouped_by_ingredients)
    return grouped_by_title, grouped_by_ingredients


def categorize_others(analyze_ingredient):
    """80%まではその値をとり、超えるとその他に分類されるようにする。"""
    # 合計値sumを求める
    sum = 0
    for i in range(len(analyze_ingredient)):
        sum += analyze_ingredient[i][1]
    # 80% を超えた次のインデックスと材料名を求める
    tmp = 0
    for i in range(len(analyze_ingredient)):
        tmp += analyze_ingredient[i][1]
        if tmp >= sum * 0.8:
            index = i + 1
            break
    # その他の値を求める
    others = 0  # その他の値
    for i in range(index, len(analyze_ingredient)):
        others += analyze_ingredient[i][1]

    # その他に分類されるデータを削除
    for i in range(len(analyze_ingredient) - index):
        del analyze_ingredient[index]

    # 新しくその他を分類
    analyze_ingredient.append(('others', others))
    return analyze_ingredient


def count_data(by_title, ingredients, by_ingredients, list_ingredients):
    """ データを集計する。"""
    # レシピIDを取得する。
    # 材料の個数の60%以上のデータが入っているかどうかで判断する
    # ingredient_count = by_ingredients.groupby('recipe_id').count()
    # # print('ingredient_count', ingredient_count)
    # recipe_id = ingredient_count[ingredient_count['title'] >=
    #                              (len(list_ingredients)) * 0.7].index
    # recipe_id = by_title['recipe_id']

    # print('recipe_id', recipe_id)
    # 取得したレシピIDのデータを取得
    # my_recipe = None
    # print('by_title', by_title)
    # for i in range(len(recipe_id)):
        # tmp = by_title.loc[by_title['recipe_id'] == recipe_id[i]]
    #     tmp = by_title.loc[i]
    #     my_recipe = pd.concat([my_recipe, tmp])
    #     print(my_recipe)
    # my_recipe = my_recipe.reset_index(drop=True)
    # my_recipe_copy = my_recipe.copy()
    # print(my_recipe_copy)
    # 辞書型で材料とつくれぽ値(ingredient_tsukurepoを取得----------------------
    ingredient_tsukurepo = {}
    print(by_title)
    # print(my_recipe_copy)
    for i in range(len(by_title)):
        # print(utility.convert_to_hira(by_title['ingredient'][i]))
        by_title['ingredient'][i] = utility.convert_to_hira(by_title['ingredient'][i])
        if by_title['ingredient'][i] in ingredient_tsukurepo.keys():
            # もし材料名が既にanalyze_ingredientに存在していたら、つくれぽ数を足す
            ingredient_tsukurepo[by_title['ingredient'][i]] += \
                by_title['tsukurepo_count'][i]
        else:
            ingredient_tsukurepo[by_title['ingredient'][i]] = \
                by_title['tsukurepo_count'][i]

    # 記号を削除、（）内を削除
    dict_ingredient_tsukurepo = ingredient_tsukurepo.copy()
    ingredient_tsukurepo = {}
    print(dict_ingredient_tsukurepo)
    # re_katakana = re.compile(r'[\u30A1-\u30F4]+')
    for ingredient in dict_ingredient_tsukurepo:
        ingredient_name = delete_symbol(ingredient)
        ingredient_name = re.sub("（.+?）", "", ingredient_name)
        ingredient_name = re.sub("\(.+?\)", "", ingredient_name)
        # if re_katakana.search(ingredient_name):
        #     ingredient_name = utility.convert_kata_to_hira(ingredient_name)
        ingredient_tsukurepo[ingredient_name] = dict_ingredient_tsukurepo[ingredient]
    # print(ingredient_tsukurepo)

    # 曖昧検索にかけて、更に重複を減らす--------------------------------
    # ing_aをリスト内のing_bと比べていく

    # 名前を短い順に並び変える
    list_ingredient_tsukurepo = sorted(ingredient_tsukurepo.items(), key=lambda x: len(x[0]), reverse=False)  # , reverse=True
    if '' in list_ingredient_tsukurepo[0]:
        del list_ingredient_tsukurepo[0]
    # print(list_ingredient_tsukurepo)
    dict = {}  # 辞書型の材料とつくれぽ値
    dict.update(list_ingredient_tsukurepo)
    list_similar = []
    copy = dict.copy()
    copy_drop = dict.copy()  # 消す方
    drop = []  # 消したもの
    # 似た名前同士をまとめて、二次元リストを作る-------------------------------
    # print(list_ingredient_tsukurepo)
    for ing_a, count_a in list(copy.items()):
        if ing_a in copy_drop:
            del copy_drop[ing_a]
            list_similar.append([ing_a])
        ing_a_len = len(ing_a)
        if ing_a in drop:  # 重複を消したものの中に今回調べるものがあれば
            # print('重複したやつ')
            pass
        else:
            for ing_b, count_b in list(copy_drop.items()):
                ing_b_len = len(ing_b)
                if ing_a_len - ing_b_len == -1 or ing_b_len - ing_a_len == -1:
                # if ing_b_len:
                    # range()の中身が0になってしまうので、普通に検索する
                    rate = difflib.SequenceMatcher(None, ing_a, ing_b).ratio()
                else:
                    # リストの小さい方の長さ分ずつ比較して、最大値をとる
                    rate = max([difflib.SequenceMatcher(None, ing_a,
                                                        ing_b[i:i + ing_a_len]).ratio()
                                for i in range(abs(ing_b_len - ing_a_len + 1))])
                border = 0.70 # * (1 - 1/ing_b_len)
                if rate > border:  # 一致率が60%をこえたら
                    # print('--------------')
                    # print(ing_a)
                    # print(ing_b)
                    list_similar[-1].append(ing_b)
                    # print(list_similar)
                    del copy_drop[ing_b]  # 統合された方が重複して調べてしまわないように
                    drop.append(ing_b)
    # del list_similar[0]  # なぜか空が入るので
    print(list_similar)
    dict_similar = {}
    for i in range(len(list_similar)):
        for j in range(1, len(list_similar[i])):
            if list_similar[i][j]:
                dict_similar[list_similar[i][0]] = len(list_similar[i])
    if '' in dict_similar.keys():
        del dict_similar['']
    print(dict_similar)
    # for i in range(len(list_similar)):
    #     for j in range(1, len(list_similar[i])):
    #         if list_similar[i][j]:
    #             dict[list_similar[i][0]] += dict[list_similar[i][j]]
    #             del dict[list_similar[i][j]]
    # if '' in dict.keys():
    #     del dict['']
    # print(dict)
    # カウントが多い順に並び替える
    analyze_ingredient = sorted(dict_similar.items(), key=lambda x: x[1], reverse=True)  # , reverse=True
    # # 80%までは、その値をとり、それ以外は”その他”に分類する
    # print(analyze_ingredient)
    # analyze_ingredient = categorize_others(analyze_ingredient)
    # 既存の材料は削除する
    # 削除するインデックスを取得
    # 英語に全部直してやったほうが精度高いかも？→やめよう
    print(analyze_ingredient)
    # en_ingredients = []
    # en_ingredients = utility.trans_to_en(ingredients)
    drop_index = []
    # en_analyze_ingredient = []
    # for analyze in analyze_ingredient:
    #     en_analyze_ingredient.append(utility.trans_to_en(analyze))
    # print(en_analyze_ingredient)
    for ingredient in ingredients:
        ingredient = utility.convert_to_hira(ingredient)
        ingredient_len = len(ingredient)
        for i in range(len(analyze_ingredient)):
            analyze_len = len(analyze_ingredient[i][0])
            analyze = analyze_ingredient[i][0]
            if ingredient_len - analyze_len == -1 or analyze_len - ingredient_len == -1:
                # range()の中身が0になってしまうので、普通に検索する
                rate = difflib.SequenceMatcher(None, ingredient, analyze).ratio()
            elif ingredient_len <= analyze_len:
                # リストの小さい方の長さ分ずつ比較して、最大値をとる
                rate = max([difflib.SequenceMatcher(None, ingredient, analyze[
                                                                i:i + ingredient_len]).ratio()
                            for i in range(abs(analyze_len - ingredient_len + 1))])
            else:
                rate = max([difflib.SequenceMatcher(None, analyze,
                                                    ingredient[i:i + analyze_len]).ratio()
                            for i in range(abs(analyze_len - ingredient_len + 1))])

            if rate > 0.70:
                drop_index.append(i)
    drop_index = sorted(drop_index, reverse=True)  # 大きい方から削除する
    for i in drop_index:
        analyze_ingredient.pop(i)
    # analyzed_ingredient = []
    # for i in range(len(analyze_ingredient)):
    #     analyzed_ingredient.append(utility.convert_to_kanji(analyze_ingredient[i][0]))
    print(analyze_ingredient)
    return analyze_ingredient


def dic_pie(dictionary):
    """dictionary型を円グラフにして表示する"""
    plt.rcParams["font.family"] = "MS Gothic"
    label = [dictionary[i][0] for i in range(len(dictionary))]
    grouped_data = [dictionary[i][1] for i in range(len(dictionary))]
    plt.pie(grouped_data, labels=label, startangle=90, autopct="%1.1f%%")
    plt.show()
    plt.axis('equal')


def get_cookppad_data():
    # mySQLに接続
    conn = mysql.connector.connect(host='127.0.0.1', user='root',
                                   password='ma9ri4ru5@yu24ma05ka19',
                                   database='mycookpad_data')
    cursor = conn.cursor()  # カーソルに接続

    # データを取得
    row_data = psql.read_sql('SELECT * from my_ingredients', conn)
    # print(row_data)
    # mySQLとの接続終了
    cursor.close()
    conn.close()

    return row_data


def main():
    # クックパッドデータを取得
    raw_data = get_cookppad_data()
    # print(raw_data)

    # 料理名と材料をcsvファイルから取得する
    # メニュー名の読み込み
    my_recipe = utility.RecipeData('my_recipe_日本語.csv')
    menus = my_recipe.get_menu()

    # メニュー名をfor文で回し、RANKカラムに値の入っていないレコードを探す。
    for menu in menus:
        print("--------{}---------".format(menu))
        dic_recipe = {'MENU': menu}
        dic_recipe.update(my_recipe.load(menu))
        if dic_recipe['RANK1'] == "":  # 欠損値の判定
            # 材料とメニュー名を取得
            # ingredients = my_recipe.get_ingredients(dic_recipe, translate=True)  # 材料を日本語で取得
            # print(ingredients)
            ingredients = my_recipe.get_ingredients(dic_recipe)
            # menu_ja = utility.trans_to_ja(menu)  # メニュー名を日本語に翻訳

            # print(menu_ja)

            # 材料とメニュー名を用いてデータを絞り込み、材料の数を数える
            # grouped_by_title, grouped_by_ingredients = grouped(raw_data, menu_ja, ingredients)
            grouped_by_title, grouped_by_ingredients = grouped(raw_data, menu, ingredients)
            # print(grouped_by_title, 'grouped_by_title')
            # print(grouped_by_ingredients, 'grouped_by_ingredients')
            analyzed_ingredient = count_data(grouped_by_title, ingredients,
                                             grouped_by_ingredients,
                                             ingredients)
            # print(analyzed_ingredient)
            # 集計結果から提案する材料をcsvファイルに保存する（3位まで英語に訳して）
            # print(analyzed_ingredient)
            # dic_recipe['RANK1'] = utility.trans_to_en(analyzed_ingredient[0])
            # print("1位：", dic_recipe['RANK1'])
            print("1位：", analyzed_ingredient[0][0])

            # dic_recipe['RANK2'] = utility.trans_to_en(analyzed_ingredient[1])
            # print("2位", dic_recipe['RANK2'])
            print("2位", analyzed_ingredient[1][0])
            # dic_recipe['RANK3'] = utility.trans_to_en(analyzed_ingredient[2])
            # print(dic_recipe['POLICY0'])
            my_recipe.save(dic_recipe)


if __name__ == '__main__':
    main()


