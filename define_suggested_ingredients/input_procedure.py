"""
提案する材料が決まった後、その材料を加えた場合の手順を入力する
変更した手順と、方策を追加して、csvファイルに保存する
"""
import pandas as pd
from resources import utility
import numpy as np
from learning.basic_recipe import Environment


def insert_procedure_policy(ingredient, procedures, policy):
    """手順と方策に新しい手順を足してそれぞれを返す。
    同時に、どの材料にどの手順が対応しているのかを返す"""
    dic_ing_pro = {}
    while True:
        before = input("何番の後に手順を入れますか？\n"
                       "なければ'q'を入力してください\n")
        if before == 'q':
            break
        else:
            before = int(before)
        pro = input("手順を入力してください").capitalize()

        # 手順に新しい手順を挿入
        procedures.insert(before + 1, pro)
        # 方策に新しい手順を挿入。値は、np.nanとする。
        length = len(policy[0])  # TODo I changed
        line = []
        for i in range(length):
            line.append(0.0)
        print(line)
        policy.insert(before + 1, line)
        print(policy)
        for row in policy:
            row.insert(before + 1, 0.0)
        print(policy)
        # 辞書型に材料とそれに対応する手順を格納する
        if ingredient in dic_ing_pro.keys():  # もしその材料に対して2つめの手順であった場合
            dic_ing_pro[ingredient].append(pro)
        else:  # 1つめの手順であった場合
            dic_ing_pro[ingredient] = [pro]
        for i, procedure in enumerate(procedures):
            print(i, procedure)  # 手順を表示
    return procedures, dic_ing_pro  # TODO policyを取り除いた


def main():
    my_recipe = utility.RecipeData('my_recipe.csv')
    menus = my_recipe.get_menu()
    for menu in menus:
        dic_ing_pro = {menu: {}}
        dic_recipe = {'MENU': menu}
        dic_recipe.update(my_recipe.load(menu))
        if dic_recipe['ING_PRO'] == "":  # 空白の文字列かどうか判定
            print("[MENU]:", menu)
            for i, procedure in enumerate(dic_recipe['PROCEDURE']):
                print(i, procedure)  # 手順を表示
            print('****' + dic_recipe['RANK1'] + "があるときの手順****")
            dic_recipe['PROCEDURE'], tmp = \
                insert_procedure_policy(dic_recipe['RANK1'],
                                        dic_recipe['PROCEDURE'],
                                        dic_recipe['POLICY0'])
            dic_ing_pro[menu].update(tmp)
        # if dic_recipe['POLICY3'] == "":  # 空白の文字列かどうか判定
            print('****' + dic_recipe['RANK2'] + "があるときの手順****")
            # dic_recipe['PROCEDURE'], tmp, dic_recipe['POLICY'] = \
            dic_recipe['PROCEDURE'], tmp = \
                insert_procedure_policy(dic_recipe['RANK2'],
                                        dic_recipe['PROCEDURE'],
                                        dic_recipe['POLICY0'])
            dic_ing_pro[menu].update(tmp)
            dic_recipe['ING_PRO'] = dic_ing_pro

            # POLICY1, POLICY2, POLICY3(12)を作る
            ingredient1 = dic_recipe['RANK1']
            ingredient2 = dic_recipe['RANK2']
            pro1 = dic_ing_pro[menu][ingredient1]
            pro2 = dic_ing_pro[menu][ingredient2]
            s_history1 = dic_recipe['PROCEDURE'].copy()
            s_history2 = dic_recipe['PROCEDURE'].copy()
            s_history3 = dic_recipe['PROCEDURE'].copy()
            print(type(s_history1))
            for p in pro2:
                s_history1.remove(p)
            for p in pro1:
                s_history2.remove(p)
            procedures = dic_recipe['PROCEDURE'].copy()
            procedures = [procedures]
            # print(procedures)
            env = Environment(procedures, 1)
            s_history = [s_history1, s_history2, s_history3]
            # print(s_history)
            for i, list_history in enumerate(s_history):
                print(list_history)
                list_history = [list_history]
                s_history = env.get_s_history(list_history)
                env.policy_gradient.reset_theta()  # 方策をリセット
                pi_0 = env.policy_gradient.softmax_convert_into_pi_from_theta()  # thetaをpiに変換
                env.policy_gradient.update_theta(pi_0, s_history)  # thetaを更新
                pi = env.policy_gradient.softmax_convert_into_pi_from_theta()  # thetaをpiに変換
                dic_recipe['POLICY' + str(i + 1)] = pi
            my_recipe.save(dic_recipe)


if __name__ == '__main__':
    main()
