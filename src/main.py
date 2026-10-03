import argparse
import json
import sys


def load_vfs(vfs_path):
    """
    Загрузка структуры VFS из JSON-файла с обработкой ошибок.
    """
    try:
        with open(vfs_path, "r", encoding="utf-8") as f:
            vfs_data = json.load(f)
            return vfs_data
    except FileNotFoundError:
        print(f"Ошибка: Файл VFS '{vfs_path}' не найден!")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Ошибка: Файл VFS '{vfs_path}' содержит некорректный JSON!")
        sys.exit(1)


def get_current_dir(vfs_data, current_path):
    """
    Достает словарь текущей папки по списку путей current_path.
    """
    curr = vfs_data
    for folder in current_path:
        curr = curr[folder]
    return curr


def resolve_path(vfs_data, current_path, path_str):
    """
    Функция resolve_path находит объект в VFS по любому пути.
    Поддерживает: '.', '..', '/', относительные и абсолютные пути.
    Возвращает (node, new_path_list) или (None, None), если путь не найден.
    """
    if not path_str or path_str == ".":
        return get_current_dir(vfs_data, current_path), list(current_path)

    if path_str.startswith("/"):
        temp_path = []
    else:
        temp_path = list(current_path)

    parts = [p for p in path_str.split("/") if p]

    for part in parts:
        if part == ".":
            continue
        elif part == "..":
            if temp_path:
                temp_path.pop()
        else:
            curr = get_current_dir(vfs_data, temp_path)
            if isinstance(curr, dict) and part in curr:
                temp_path.append(part)
            else:
                return None, None

    node = get_current_dir(vfs_data, temp_path)
    return node, temp_path

def cmd_exit(args):
    """Логика команды exit."""
    if args:
        err_msg = f"Ошибка: неверные аргументы '{args}'"
        print(err_msg)
        return False, err_msg
    return False, None


def cmd_pwd(args, current_path):
    """Команда pwd (показать текущий путь)."""
    if args:
        err_msg = "Ошибка: команда pwd не принимает аргументы"
        print(err_msg)
        return False, err_msg

    if not current_path:
        print("/")
    else:
        print("/" + "/".join(current_path))
    return True, None


def cmd_ls(args, vfs_data, current_path):
    """Команда ls (показать содержимое)."""
    target_path = args[0] if args else "."
    node, _ = resolve_path(vfs_data, current_path, target_path)

    if node is None:
        err_msg = f"Ошибка: ls: нет такого файла или каталога '{target_path}'"
        print(err_msg)
        return False, err_msg

    if isinstance(node, dict):
        items = list(node.keys())
        if items:
            print("  ".join(items))
        return True, None
    else:
        filename = target_path.split("/")[-1]
        print(filename)
        return True, None


def cmd_cd(args, vfs_data, current_path):
    """Команда cd (изменить текущий каталог)."""
    if not args or args[0] == "/":
        current_path.clear()
        return True, None

    target = args[0]
    node, new_path = resolve_path(vfs_data, current_path, target)

    if node is None or not isinstance(node, dict):
        err_msg = f"Ошибка: cd: нет такого каталога '{target}'"
        print(err_msg)
        return False, err_msg

    current_path.clear()
    current_path.extend(new_path)
    return True, None


def cmd_tac(args, vfs_data, current_path):
    """Логика команды tac (ввод с клавиатуры или чтение файла)."""
    if not args:
        lines = []
        try:
            while True:
                lines.append(input())
        except (EOFError, KeyboardInterrupt):
            pass

        for line in reversed(lines):
            print(line)
        return True, None

    target_path = args[0]
    node, _ = resolve_path(vfs_data, current_path, target_path)

    if node is None:
        err_msg = f"Ошибка: tac: файл '{target_path}' не найден"
        print(err_msg)
        return False, err_msg

    if isinstance(node, dict):
        err_msg = f"Ошибка: tac: '{target_path}' является каталогом"
        print(err_msg)
        return False, err_msg

    if isinstance(node, str):
        lines = node.splitlines()
        for line in reversed(lines):
            print(line)
        return True, None

    return False, "Ошибка чтения файла"


def execute_command(user_input, vfs_data, current_path):
    """
    Разбор введенной строки и вызов соответствующей подфункции команды.
    """
    parts = user_input.strip().split()
    if not parts:
        return True, None

    cmd = parts[0]
    args = parts[1:]

    if cmd == "exit":
        return cmd_exit(args)
    elif cmd == "pwd":
        return cmd_pwd(args, current_path)
    elif cmd == "ls":
        return cmd_ls(args, vfs_data, current_path)
    elif cmd == "cd":
        return cmd_cd(args, vfs_data, current_path)
    elif cmd == "tac":
        return cmd_tac(args, vfs_data, current_path)
    else:
        err_msg = f"Ошибка: неизвестная команда '{cmd}'"
        print(err_msg)
        return False, err_msg


def run_script(vfs_path, script_path, vfs_data, current_path):
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

        success, err = execute_command(command, vfs_data, current_path)
        if not success:
            if err:
                print("Скрипт остановлен из-за ошибки")
            else:
                print("Скрипт завершен по команде exit.")
            break


def run_repl(vfs_path, vfs_data, current_path):
    """
    Интерактивный цикл REPL.
    """
    while True:
        try:
            user_input = input(f"{vfs_path}> ")
            success, _ = execute_command(user_input, vfs_data, current_path)
            if not success:
                break
        except (KeyboardInterrupt, EOFError):
            break


def main():
    """
    Разбор аргументов командной строки и запуск эмулятора.
    """
    parser = argparse.ArgumentParser(
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

    vfs_data = load_vfs(args.vfs)
    current_path = []

    if args.script:
        run_script(args.vfs, args.script, vfs_data, current_path)
    else:
        run_repl(args.vfs, vfs_data, current_path)


if __name__ == "__main__":
    main()
