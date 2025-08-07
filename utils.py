import os
import stat
import subprocess

def is_file_readonly(path):
    return not os.access(path, os.W_OK)

def set_file_readonly(path, readonly=True):
    if os.path.isfile(path):
        current_permissions = os.stat(path).st_mode
        if readonly:
            os.chmod(path, current_permissions & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH)
        else:
            os.chmod(path, current_permissions | stat.S_IWUSR)
        return True
    return False

def is_game_running(process_name):
    try:
        tasks = subprocess.check_output(['tasklist'], text=True)
        return process_name.lower() in tasks.lower()
    except subprocess.CalledProcessError:
        return False