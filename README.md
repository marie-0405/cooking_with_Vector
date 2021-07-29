# cooking_with_Vector

## How to execute
### for behavior robot(行動ありのロボットの場合)
1. sub_emo.py のTODO箇所、no_emotion=Falseになっていることを確認する(Make sure that no_emotion=False in the TODO section of sub_emo.py)
2. listen.pyのTODOの3箇所、record=Trueになっていることを確認する(Make sure that record=True in three places in TODO in listen.py)
2. NEPを開く(Open the NEP)
3. 3つのプログラム(say_text.py, emotion.py, sub_emo.py)を実行する（execute say_text.py, emotion.py, sub_emo.py in vector folder)
4. brain.pyを実行する(execute brain.py)

## for non-behavior robot(行動なしのロボットの場合)
1. sub_emo.py のTODO箇所、no_emotion=Trueになっていることを確認する(Make sure that no_emotion=True in the TODO section of sub_emo.py)
2. listen.pyのTODO3箇所、record=Falseになっていることを確認する(Make sure that record=False in three places in TODO in listen.py)
2. NEPを開く(Open the NEP)
3. vectorフォルダー内の3つのプログラムを実行する（say_text.py, no_emotion.py, sub_emo.py in vector folder)
4. brain.pyを実行する(execute brain.py)

