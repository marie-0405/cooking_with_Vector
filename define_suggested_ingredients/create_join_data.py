# import mysql.connector
# import pandas.io.sql as psql
#
# # mySQLに接続
# conn = mysql.connector.connect(host='127.0.0.1', user='root',
#                                password='ma9ri4ru5@yu24ma05ka19',
#                                database='mycookpad_data')
# cursor = conn.cursor()
# # cursor.execute('CREATE TABLE persons('
# #                'id int NOT NULL AUTO_INCREMENT,'
# #                'name varchar(14) NOT NULL,'
# #                'PRIMARY KEY(id))')
# # cursor.execute('CREATE DATABASE test_mysql')
# # conn.commit()
# df = psql.read_sql('SELECT * from recipes LIMIT 50000', conn)
# print(df)
# cursor.close()
# conn.close()

#  材料を集計する
import matplotlib.pyplot as plt

# 取得したrecipe_idのデータを取得
# for i in range(len(recipe_id)):
#     tmp = my_menu.loc[my_menu['recipe_id'] == recipe_id[i]]
#     my_recipe = pd.concat([my_recipe, tmp])
# my_recipe = my_recipe.reset_index(drop=True)
# analyze_ingredient = {}
# analyze_ingredient['aa'] = 1
# analyze_ingredient['aa'] += 2
# print(type(my_recipe['tsukurepo_count'][0]))
# for i in range(len(my_recipe)):
#     analyze_ingredient[my_recipe['ingredient'][i]] = my_recipe['tsukurepo_count'][i]
# label = list(analyze_ingredient.keys())
plt.rcParams["font.family"] = "MS Gothic"
label = ['紅茶ティーバッグ', '水', '紅茶のティーバッグ', 'イオンのベストプライス\u3000紅茶ティーバッグ', 'ティーバッグ', '氷、水、レモンの輪切り']
print(label)
# data = list(analyze_ingredient.values())
data = [1, 1, 20, 33, 39, 39]
data.sort()
print(data)
plt.pie(data, labels=label, startangle=90, autopct="%1.1f%%")
plt.axis('equal')
plt.show()
