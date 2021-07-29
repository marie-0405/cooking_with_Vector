""""
ベクターが人の顔を追従する
"""
import anki_vector
from anki_vector.util import degrees
import nep
import time

# 準備
args = anki_vector.util.parse_command_args()

# NEPへの接続
# msg_type = 'string'
# node = nep.node("face_sub" , "nanomsg")
# sub = node.new_sub("emo_facetracking", msg_type)


def main():
    with anki_vector.Robot(args.serial, enable_face_detection=True) as robot:
        robot.behavior.set_head_angle(degrees(45.0))
        robot.behavior.set_lift_height(0.0)
        face_to_follow = None
        try:
            while True:
                turn_future = None
                # s, msg = sub.listen_string()
                # if not s:
                if face_to_follow:
                    # start turning towards the face
                    turn_future = robot.behavior.turn_towards_face(
                        face_to_follow)

                if not (face_to_follow and face_to_follow.is_visible):
                    # find a visible face, timeout if nothing found after a short while
                    for face in robot.world.visible_faces:
                        face_to_follow = face
                        print("follow")
                        break

                # if turn_future != None:
                    # Complete the turn action if one was in progress
                    # turn_future.result()

                time.sleep(.1)
            # else:
            #     time.sleep(5)
            #     print('5')
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()