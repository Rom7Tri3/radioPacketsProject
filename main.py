import sys
import modulation

def main():
    print("Welcome to the CLI! Enter '/hello' to print 'Hello world' or '/exit' to quit.")
    while True:
        # Prompt for user input
        user_input = input("> ").strip()

        if user_input == "/help":
            print("[/help] for help\n [/send] to create and play string as QAM .wav file\n [/exit] to quit.")
        elif user_input == "/exit":
            print("Goodbye!")
            sys.exit(0)
        elif user_input == "/send":
            message = input("> ")
            modulation.sendMessage(message)
        else:
            print(f"Unknown command: {user_input}. Try '/help' or '/exit'.")


if __name__ == "__main__":
    main()
