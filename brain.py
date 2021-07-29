""""
ベクターが料理の手順を指示するための中枢プログラム
recipe.csvファイルの方策から確率の高い次の手順を抽出して言う。
"""
from vector import agent
import anki_vector
from anki_vector.util import degrees
from resources import utility
import nep
import time

# NEPへの接続
msg_type = "string"  # Message type to listen. "string" or "json"

node = nep.node('brain_pub', "nanomsg")

pub_say = node.new_pub('brain_say', msg_type)  # sayへのpub
pub_emo = node.new_pub('brain_emo', msg_type)  # emoへのpub
pub_subemo = node.new_pub('brain_emosub', msg_type)  # emosubへのpub


# 準備
args = anki_vector.util.parse_command_args()
MY_RECIPE = 'my_recipe.csv'


def main():
    with anki_vector.Robot(args.serial) as robot:
        user_data = utility.CsvFile('Menu_selection.csv').read_all_data()

        vector = agent.Agent(robot, pub_emo=pub_emo, pub_say=pub_say, pub_subemo=pub_subemo)
        vector.stand_by()
        my_recipe = utility.RecipeData(MY_RECIPE)
        # Vector = Agent('robot')
        # 挨拶をして、名前を聞く
        user_name = vector.greeting()
        # user_name = 'Marie Yamamoto'
        # user_name = 'Sohki Masuyama'

        # メニューを取得して、作り始める
        menu = vector.let_make_menu(user_name)
        time.sleep(3)

        # レシピデータのの読み込み
        my_data = my_recipe.load(menu)

        # 使う材料を表示して、新しい材料を提案する
        new_ingredient_num = vector.suggest(my_data, [my_data['RANK1'], my_data['RANK2']])
        # 手順と方策の情報をagentに渡す
        procedures = my_data['PROCEDURE']
        policy = my_data['POLICY' + new_ingredient_num]
        vector.pass_info(procedures, policy)

        # 開始する。最初の手順を言う
        state_num = 0
        vector.start()
        time.sleep(1)
        state_num = vector.instruct(state_num)
        time.sleep(3.5)
        while True:
            if state_num == len(procedures) - 1:
                vector.finish_and_say()
                time.sleep(7)
                break
            # time.sleep(10)
            state_num = vector.recognize_what_saying(state_num)


if __name__ == '__main__':
    main()