"""ベクターの感情を表すプログラム。
アニメーションから、感情に合いそうなプログラムを当てはめた"""
import nep
import anki_vector
from anki_vector import audio
import time
from anki_vector.util import degrees

args = anki_vector.util.parse_command_args()
HEAD_ANGLE = 45.0

# NEPへの接続
msg_type = "string"
node = nep.node("emo_sub", "nanomsg")
sub = node.new_sub("brain_emo", msg_type)


class Movement():
    def __init__(self, robot, no_emotion=False):
        self.robot = robot
        self.no_emotion = no_emotion

    def curious(self):
        """きょとんとした感じ"""
        print("curious")
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))
        self.robot.anim.play_animation('anim_eyepose_curious', ignore_head_track=True)

    def listen(self):
        print('listen')
        while True:
            try:
                self.robot.audio.stream_wav_file("vector_bell_whistle.wav", 75)
                break
            except anki_vector.exceptions.VectorExternalAudioPlaybackException as e:
                print(e)


def analyze(msg, movement_system):
    if msg == "listen":
        movement_system.listen()
    elif msg == 'curious':
        movement_system.curious()


def main():
    with anki_vector.Robot(args.serial) as robot:
        robot.anim.play_animation('anim_eyepose_curious')
        movement = Movement(robot, no_emotion=False)  # TODO , no_emotion=True
        while True:
            # time.sleep(1)
            s, msg = sub.listen_string()
            if s:
                analyze(msg, movement)


if __name__ == '__main__':
    main()