import sys
import modulation


# TODO: Change from path to listening.
# TODO: Start testing
# TODO: Implement FEC
# TODO: More Testing, maybe with radio

def main():
    print("Welcome to the CLI! Enter '/help' for help or '/exit' to quit.")
    while True:
        # Prompt for user input
        user_input = input("> ").strip()

        if user_input == "/help":
            print("[/help] for help\n[/send] to create and play string as QAM .wav file"
                  "\n[/receive] To demodulate a .wav file (will be changed later)"
                  "\n[/exit] to quit.")
        elif user_input == "/exit":
            print("Goodbye!")
            sys.exit(0)
        elif user_input == "/send":
            message = input("> ")
            modulation.sendMessage(message)
        elif user_input == "/receive":
            print("Please enter the path to the audio_file")
            audio_file = input("> ")
            if audio_file != None:
                modulation.recieveMessage(audio_file)
            else:
                print("Error, no audio file specified")
        else:
            print(f"Unknown command: {user_input}. Try '/help' or '/exit'.")


if __name__ == "__main__":
    main()
