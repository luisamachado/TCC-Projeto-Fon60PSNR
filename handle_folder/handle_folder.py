import os


def is_folder(dir_name):
    return os.path.isdir(dir_name)


def check_folder(dir_name):
    if not is_folder(dir_name):
        print(f"Diretório '{dir_name}' não encontrado")
        return


def create_folder(dir_name):
    if is_folder(dir_name):
        return

    os.mkdir(dir_name)