import argparse


def execute_command(user_input):
    """
    Разбор введенной строки и выполнение заглушек команд.
    Возвращает статус успеха (True/False) и текст ошибки, если она есть.
    """

    parts = user_input.strip().split()
    if not parts:
        return True, None

    cmd = parts[0]
    args = parts[1:]

    if cmd == "exit":
        if args:
            err_msg = f"Ошибка: неверные аргументы '{args}'"
            print(f"Ошибка: неверные аргументы '{args}'")
            return False, err_msg
        else:
            return False, None
    elif cmd in ("ls", "cd"):
        print(f"Заглушка команды '{cmd}' с аргументами: {args}")
        return True, None
    else:
        err_msg = f"Ошибка: неизвестная команда '{cmd}'"
        print(err_msg)
        return False, err_msg


def run_script(vfs_path, script_path):
    """
    Выполнение команд из стартового скрипта с остановкой при ошибке.
    """

    try:
        with open(script_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Ошибка: файл скрипта '{script_path}' не найден!")
        return

    for line in lines:
        command = line.strip()
        if not command:
            continue

        print(f"{vfs_path}> {command}")

        success, err = execute_command(command)
        if not success:
            if err:
                print("Скрипт остановлен из-за ошибки")
            else:
                print("Скрипт завершен по команде exit.")
            break


def run_repl(vfs_path):
    """
    Интерактивный цикл REPL.
    """

    while True:
        try:
            user_input = input(f"{vfs_path}> ")
            success, _ = execute_command(user_input)
            if not success:
                break
        except (KeyboardInterrupt, EOFError):
            break


def main():
    """
    Разбор аргументов командной строки и запуск эмулятора.
    """

    parser = argparse.ArgumentParser(
        description="Эмулятор командной строки UNIX"
    )
    parser.add_argument(
        "--vfs",
        required=True,
        help="Путь к физическому расположению VFS"
    )
    parser.add_argument(
        "--script",
        help="Путь к стартовому скрипту"
    )

    args = parser.parse_args()

    print(f"Путь к VFS: {args.vfs}")
    print(f"Путь к скрипту: {args.script}")

    if args.script:
        run_script(args.vfs, args.script)
    else:
        run_repl(args.vfs)


if __name__ == "__main__":
    main()
