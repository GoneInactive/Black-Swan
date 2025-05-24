from src.handler.CommandHandler import CommandHandler

def main():
    command_handler = CommandHandler()
    while True:
        command = input('> ')
        command_handler.command(command)

if __name__ == '__main__':
    main()
