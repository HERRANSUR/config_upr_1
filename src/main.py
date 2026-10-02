
def execute_command(user_input):
    """
    Разбор введенной строки и выполнение заглушек команд.
    """
    parts = user_input.strip().split()
    if not parts:
        return True

    cmd = parts[0]
    args = parts[1:]

    if cmd == "exit":
        if args:
            print(f"Ошибка: неверные аргументы '{args}'")
        else:
            return False
    elif cmd in ("ls", "cd"):
        print(f"Заглушка команды '{cmd}' с аргументами: {args}")
    else:
        print(f"Ошибка: неизвестная команда '{cmd}'")

    return True


def run_repl(vfs_name):
    """
    Основной цикл REPL (Read-Eval-Print Loop).
    """
    while True:
        try:
            user_input = input(f"{vfs_name}> ")
            if not execute_command(user_input):
                break
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    run_repl("my_vfs")
