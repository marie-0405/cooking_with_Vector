"""ベクターの感情を表すサブシステム
emotion.pyだけでは足りない動きを補う"""


import anki_vector
import nep
import time
from anki_vector.util import degrees

# NEPへの接続
msg_type = "string"
node = nep.node("emosub_sub", "nanomsg")
sub = node.new_sub("brain_emosub", msg_type)
# sub = node.new_sub('emo_emosub', msg_type)

# sub = node.new_sub('io_subemo', msg_type)

args = anki_vector.util.parse_command_args()
HEAD_ANGLE = 45.0


class SubMovement():
    def __init__(self, robot, no_emotion=False):
        self.robot = robot
        self.no_emotion = no_emotion

    def default(self):
        print('default')
        self.robot.anim.play_animation('anim_eyepose_default')
        time.sleep(3)

    def stand_by(self):
        print('stand_by')
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))

    def record(self):
        print("record")
        if self.no_emotion:
            while True:
                try:
                    self.robot.audio.stream_wav_file("早送り・時間経過trim.wav", 25)
                    break
                except Exception as e:
                    pass
        else:
                self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))
                self.robot.anim.play_animation("anim_message_loop_01", loop_count=2,
                                               ignore_head_track=True)

    def cut(self):
        print("cut")
        if self.no_emotion:
            pass
        else:
            self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))
            self.robot.behavior.set_lift_height(0.0, accel=5.0)
            self.robot.anim.play_animation(
                'anim_eyecontact_giggle_01_head_angle_40',
                ignore_head_track=True)

    def mix(self):
        if not self.no_emotion:
            print("mix_out")
            self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))
            self.robot.anim.play_animation('anim_howold_getout_01', ignore_head_track=True)
        else:
            pass


def main():
    with anki_vector.Robot(args.serial) as robot:
        sub_movement = SubMovement(robot, no_emotion=False)  # TODO
        while True:
            s, msg = sub.listen_string()
            if s:
                if msg == 'stand_by':
                    sub_movement.stand_by()
                elif msg == 'record':
                    sub_movement.record()
                elif msg == 'cut':
                    sub_movement.cut()
                elif msg == 'mix':
                    sub_movement.mix()
                elif msg == 'default':
                    sub_movement.default()


if __name__ == '__main__':
    main()
