# import agent
import nep
import anki_vector
# import logging
import time

# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s")
args = anki_vector.util.parse_command_args()

# NEPへの接続
msg_type = "string"  # Message type to listen. "string" or "json"
node = nep.node("say_sub", "nanomsg")  # Create a new node
sub = node.new_sub("brain_say", msg_type)


def display(who = "", text = ""):
    """Vectorとのコミュニケーション内容を可視化する"""
    print('[' + who + ']' + text)


def main():
    with anki_vector.Robot(args.serial) as robot:
        while True:
            # time.sleep(1)
            s, msg = sub.listen_string()
            if s:
                # print("say", end="")
                while True:
                    try:
                        robot.behavior.say_text(msg, use_vector_voice=False)
                        display('Vector', msg)
                        break
                    except anki_vector.exceptions.VectorConnectionException as e:
                        pass
                        # print("Failed to say text")

                # logging.debug(msg)


if __name__ == '__main__':
    main()