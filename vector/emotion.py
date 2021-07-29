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

    def crack(self):
        print("crack")
        self.robot.anim.play_animation('anim_keepaway_pounce_getin_01', ignore_body_track=True, ignore_head_track=True)

    def curious(self):
        """きょとんとした感じ"""
        print("curious")
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))
        self.robot.anim.play_animation('anim_eyepose_curious', ignore_head_track=True)

    def cut(self):
        print('cut')
        self.robot.anim.play_animation_trigger('CubePounceWinHand', ignore_body_track=True)

    def finish(self):
        print('finish')
        self.robot.anim.play_animation('anim_holiday_hyn_confetti_01')

    def getout(self):
        print("getout")
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))
        self.robot.anim.play_animation("anim_howold_getout_01", ignore_head_track=True)

    def giggle(self):
        print('giggle')
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))
        self.robot.anim.play_animation('anim_eyecontact_giggle_01_head_angle_40', ignore_head_track=True)

    def greeting(self):
        print("greeting")
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))
        self.robot.anim.play_animation('anim_greeting_hello_01',
                                       ignore_head_track=True)

    def heat(self):
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))
        self.robot.behavior.set_eye_color(hue=0.05, saturation=0.95)
        # self.robot.anim.play_animation('anim_feedback_iloveyou_01', ignore_head_track=True)
        print("eye color changed")
        time.sleep(2)
        self.robot.behavior.set_eye_color(hue=0.42, saturation=1.00)
        print("heat")

    def lift(self):
        print('lift')
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))
        self.robot.anim.play_animation('anim_pounce_success_03', ignore_head_track=True)

    def listen(self):
        print("listen")
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))
        self.robot.anim.play_animation('anim_onboarding_wakeword_loop_01',
                                       ignore_head_track=True)

    def mix(self):
        print('mix')
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))
        self.robot.anim.play_animation('anim_howold_fastloop_01', ignore_head_track=True)

    def mix2(self):
        print('mix')
        self.robot.anim.play_animation('anim_reacttocliff_wheely_01')

    def smile(self):
        print("smile")
        self.robot.anim.play_animation('anim_eyecontact_smile_01_head_angle_40')

    def pleasure(self):
        print("pleasure")
        self.robot.anim.play_animation_trigger('GreetAfterLongTime')

    def put(self):
        print('put')
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))
        self.robot.anim.play_animation('anim_feedback_goodrobot_02', ignore_head_track=True)
        time.sleep(3)
        self.robot.motors.set_wheel_motors(25, -25)  # 元の位置に戻るため
        time.sleep(0.6)
        self.robot.motors.set_wheel_motors(0, 0)  # 元の位置に戻るため

    def record(self):
        print('record')
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))
        self.robot.anim.play_animation('anim_message_loop_01', ignore_head_track=True)

    def sad(self):
        print('sad')
        self.robot.anim.play_animation('anim_eyepose_sad')

    def say(self):
        print("say")
        self.robot.anim.play_animation('anim_message_announce_toplayer_01')

    def stand_by(self):
        print('stand by')
        self.robot.behavior.set_head_angle(HEAD_ANGLE)

    def stop_sound(self):
        print("stop sound")
        self.robot.audio.set_master_volume(audio.RobotVolumeLevel.LOW)

    def thinking(self):
        print("thinking")
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))
        self.robot.anim.play_animation_trigger('KnowledgeGraphSearching', loop_count=2)
        time.sleep(2)
        self.robot.anim.play_animation_trigger('KnowledgeGraphSearchingGetOutSuccess', loop_count=1, ignore_head_track=True)
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))

    def worried(self):
        print('worried')
        self.robot.anim.play_animation('anim_eyepose_worried')
        self.robot.behavior.set_head_angle(degrees(HEAD_ANGLE))


def analyze(msg, movement_system):
    if msg == 'smile':
        movement_system.smile()
    elif msg == 'pleasure':
        movement_system.pleasure()
    elif msg == 'greeting':
        movement_system.greeting()
    elif msg == "listen":
        movement_system.listen()
    elif msg == 'heat':
        movement_system.heat()
    elif msg == 'say':
        movement_system.say()
    elif msg == 'thinking':
        movement_system.thinking()
    elif msg == 'giggle':
        movement_system.giggle()
    elif msg == 'cut':
        movement_system.cut()
    elif msg == 'mix':
        movement_system.mix()
    elif msg == 'put':
        movement_system.put()
    elif msg == 'mix2':
        movement_system.mix2()
    elif msg == 'lift':
        movement_system.lift()
    elif msg == 'sad':
        movement_system.sad()
    elif msg == 'finish':
        movement_system.finish()
    elif msg == 'worried':
        movement_system.worried()
    elif msg == 'curious':
        movement_system.curious()
    elif msg == 'record':
        movement_system.record()
    elif msg == 'stop sound':
        movement_system.stop_sound()


def main():
    with anki_vector.Robot(args.serial) as robot:
        movement = Movement(robot)  # TODO , no_emotion=True
        while True:
            # time.sleep(1)
            s, msg = sub.listen_string()
            if s:
                analyze(msg, movement)


if __name__ == '__main__':
    main()