""""
強化学習によって人間がロボットに料理の手順を教える。
ロボットは学習後、好奇心によって人間に新しい材料を提案する。
ロボットの好奇心について考える
"""
from resources import utility
import matplotlib.cm as cm  # color map
import matplotlib.pyplot as plt
import nltk
import numpy as np


class PolicyGradient:
    """方策勾配法を実行する"""
    def __init__(self, num_states, num_actions):
        self.num_actions = num_actions  # Agent の行動を取得
        self.num_states = num_states
        self.theta = np.ones((self.num_states, self.num_actions))  # パラメータthetaを作成]
        # self.theta = np.set_printoptions(precision=3)

    def reset_theta(self):
        # 方策thetaを初期化。行は状態、列は行動を示す。履歴ごと保存する
        # 連続して起こらないことを考慮して、対角上はゼロ
        # アクションがスタートになることはないため、そこもゼロ
        self.theta[:, 0] = np.nan
        size = self.theta.shape[0]
        for i in range(size):
            for j in range(size):
                if i == j:
                    self.theta[i, j] = np.nan
        self.theta[0, size - 1] = np.nan  # Startの次にfinishを予想しないように
        self.theta[size-1, :] = np.nan  # Finish の次はなにもなし

    def update_theta(self, pi, s_history):  # s_history は2次元
        """方策勾配法に従い方策を更新する
        　　theta の更新関数を定義する"""
        ALPHA = 0.7 # 学習率
        # T = 4  # 正解を与えてるので、1にする
        delta_theta = self.theta.copy()  # Δthetaの元を作成
        size = self.theta.shape[0]
        # delta_thetaを要素ごとに決める
        for i in range(size):
            for j in range(size):
                SA_i = []
                SA_ij = []
                for episode in range(len(s_history)):
                    if not (np.isnan(self.theta[i, j])):
                        for index in range(len(s_history[episode]) - 1):
                            if s_history[episode][index] == i:
                                SA_i.append(s_history[episode][index])  # 履歴から状態iのものを取り出す
                            if s_history[episode][index] == i and \
                                    s_history[episode][index + 1] == j:
                                SA_ij.append((s_history[episode][index],
                                              s_history[episode][index + 1]))  # 状態iで行動jをしたものを取り出す
                N_i = len(SA_i)  # 状態iで行動した総回数
                N_ij = len(SA_ij)  # 状態iで行動jをとった回数
                # print('N_I', N_i)
                # print('N_ij', N_ij)
                delta_theta[i, j] = (N_ij - pi[i, j] * N_i)
        self.theta = self.theta + ALPHA * delta_theta

    def softmax_convert_into_pi_from_theta(self):
        beta = 1.0  # TODO 逆温度小さいほど行動がランダムになる
        size = self.theta.shape[0]
        pi = np.zeros((size, size))
        pi = np.array(pi)
        np.set_printoptions(precision=4)  # 小数点以下４桁に設定
        exp_theta = np.exp(beta * self.theta)  # thetaをexp(theta)へと変換
        for i in range(size):
            for j in range(size):
                pi[i, :] = exp_theta[i, :] / np.nansum(exp_theta[i, :])
                # softmaxでの計算
        pi = np.nan_to_num(pi)  # これがないとどうなるのか

        return pi


class MakeInfo:
    """menuの手順を作る"""
    def __init__(self, num_episodes=1):
        self.verbs = ['cut', 'put', 'heat']
        self.menu = input('MENU:').capitalize()
        print("Materials are divided solid, liquid, seasoning.")
        self.solids = input("solid: ")
        if self.solids:
            self.solids = self.solids.split(", ")
        else:
            self.solids = []  # 固体がない場合は、空のリストを返す
        self.liquids = input("liquid: ")
        if self.liquids:
            self.liquids = self.liquids.split(", ")
        else:
            self.liquids = []
        self.seasonings = input("seasoning: ")
        if self.seasonings:
            self.seasonings = self.seasonings.split(", ")
        else:
            self.seasonings = []
        self.tools = input("Input the tools(e.g.: kettle, cup)")
        self.tools = self.tools.split(", ")
        self.tools = self.tools
        self.num_episodes = num_episodes
        # self.tools = ['kettle', 'cup']

    def make_info(self):

        materials = self.solids + self.liquids + self.seasonings
        # for verb in self.verbs:
        #     if verb == 'cut':  # TODO
        #         for solid in self.solids:
        #             procedures.append(" ".join([verb, solid]))
        #     elif verb == 'heat':  # TODO
        #         for tool in self.tools:
        #             procedures.append(" ".join([verb, tool]))
        #     elif verb == 'put':  # TODO
        #         for material in materials:
        #             for tool in self.tools:
        #                 procedures.append(
        #                     " ".join([verb, material, "to", tool]))
        # procedures = dict.fromkeys(procedures)
        procedures = []
        for i in range(self.num_episodes):
            print("エピソード", i + 1)
            procedures.append(["Start"])
            while True:
                state = input('What\'s the step now?')
                state = state.capitalize()
                procedures[-1].append(state)
                if state == 'Finish':
                    break
        # procedures = list(procedures)
        # procedures.append("Finish")
        # data = [self.menu, ', '.join(self.solids), ', '.join(self.liquids),
        #         ', '.join(self.seasonings), ', '.join(self.tools), ', '.join(procedures)]
        data = [self.menu, self.solids, self.liquids, self.seasonings,
                self.tools, procedures]
        return data


class Environment:
    """cooking-HRIを実行する環境のクラス。人間側"""
    def __init__(self, procedures, num_episodes=1):
        self.num_states = len(procedures[0])
        self.num_actions = len(procedures[0]) # stateとactionは同じ
        self.policy_gradient = PolicyGradient(self.num_states, self.num_actions)
        self.procedures = procedures[0]
        self.num_episodes = num_episodes # TODO

    def get_state_index(self, s):
        # while True:
        #     task = input("What are you doing now?\n")
        #     # task = task.lower()  # i が名詞だと認識されてしまうから
        #     if task == "finish":
        #         state_index = len(self.procedures) - 1
        #         return state_index
        #     task_word_tokenize = nltk.word_tokenize(task)  # 分かち書き
        #     task_pos = nltk.pos_tag(task_word_tokenize)
        #     # print(task_pos)
        #     verbs = ""
        #     A = ""
        #     B = ""
        #     TO_index = 999  # 大きい数にしておく。なかった場合に拾えるように
        #     # for index, word in enumerate(task_pos):
        #     #     if "V" in word[1]:
        #     #         verbs = word[0]
        #     #     if "TO" in word[1]:
        #     #         TO_index = int(index)
        #     #
        #     # for index, word in enumerate(task_pos):
        #     #     if ("NN" in word[1]) and (int(index) < TO_index):
        #     #         A += word[0] + " "
        #     #     if ("NN" in word[1]) and (int(index) > TO_index):
        #     #         B += word[0] + " "
        #     # A = A.strip()
        #     # B = B.strip()
        #     # if A != "" and B == "":
        #     #     procedure = " ".join([verbs, A])
        #     # else:
        #     #     procedure = " ".join([verbs, A, 'to', B])
        #     # 入力したのが手順になかった場合エラーを表示してもう一度聞く
        #     if procedure not in self.procedures:
        #         print("Not Found: Input correctly")
        #         pass
        #     else:
        #         state_index = self.procedures.index(procedure)
        #         break
        print(self.procedures)
        state_index = self.procedures[s]
        print('state_index', state_index)
        return state_index

    def get_s_history(self, *args):
        s_history = []
        print("shape:", self.policy_gradient.theta.shape)
        # procedures の一番最初（Start)を初期状態として定義
        real_procedures = args[0]
        # print('real_procedures', real_procedures)
        print(real_procedures)
        print(type(real_procedures))
        for procedure in real_procedures:
            s_history.append([])
            # print("エピソード" + str(episode + 1))
            for task in procedure:
                print(task)
                state_num = self.procedures.index(task)
                s_history[-1].append(state_num)
        print('s_history', s_history)
        return s_history


class Display:
    """確率の変化を可視化する"""
    def __init__(self):
        plt.rcParams["font.family"] = "Times New Roman"
        self.fig = plt.figure(figsize=(5, 5))
        self.ax = plt.gca()

    def show(self, theta, file_name='aaa'):
        size = theta.shape[0]
        self.ax.set_xlim(-0.55, size-0.45)
        self.ax.set_ylim(size-0.45, -0.55 )
        self.ax.set_xlabel('Action', fontsize=16)
        self.ax.set_ylabel('State', fontsize=16)

        plt.xticks(np.arange(0, size-0.45, 1))
        plt.yticks(np.arange(size-1, -0.01, -1))
        for s in range(size):
            for t in range(size):
                self.ax.plot([t], [s], marker="s",color=cm.gray(theta[s, t]),
                             markersize=240 / size)
        # self.fig.savefig(file_name + '.png')
        plt.show()


def policy():
    # データを作る
    # Create information
    list_data = MakeInfo(num_episodes=1).make_info()
    print(list_data)
    procedures = list_data[-1]
    env = Environment(procedures, num_episodes=1)
    # env = Environment(data[0][-1].split(', '), 1)  # procedureリストに戻して渡す
    s_history = env.get_s_history(procedures)
    print(s_history)
    env.policy_gradient.reset_theta()  # 方策をリセット
    pi_0 = env.policy_gradient.softmax_convert_into_pi_from_theta()  # thetaをpiに変換
    env.policy_gradient.update_theta(pi_0, s_history)  # thetaを更新
    pi = env.policy_gradient.softmax_convert_into_pi_from_theta()  # thetaをpiに変換
    # print(pi)
    list_data.append(pi)
    # RANKのところにNoneを入れておかないとエラーになるので入れる
    for i in range(7):
        list_data.append("")

    anim = Display()
    anim.show(pi, 'T=4')
    # print(data)

    # メニューや方策をファイルに保存する
    columns = ('MENU', 'SOLID', 'LIQUID', 'SEASONING', 'TOOL',
               'PROCEDURE', 'POLICY0','POLICY1', 'POLICY2', 'POLICY3','RANK1',
               'RANK2', 'RANK3', 'ING_PRO')  # 列名をタプルで定義
    file = utility.RecipeData('my_recipe.csv', *columns)
    # print(type(list_data))
    # print(list_data)
    file.save(data=list_data)


if __name__ == '__main__':
    policy()
