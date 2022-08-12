import os
import time
import traceback
from datetime import date
import re



def file_Len(file_path_):
    with open(file_path_, 'r') as f:
        return len(f.readlines())


def new_lines(file_path_, file_len_,):
    with open(file_path_, 'r') as fi:
        newLines_ = fi.readlines()[file_len_:]
    return newLines_


def log_decoder(lines):
    pattern = re.compile("^{2}:{2}:{2}   DropsDetection.+USDT-.+")

    if len(lines) != 0:
        for line in lines:
            pattern.match(line)


if __name__ == '__main__':
    try:
        while True:
            file_path = f'C:\\Users\\Administrator\\Desktop\\BOT Futures - LONG\\' \
                        f'BOT Futures\\logs\\LOG_{date.today()}.txt'
            modifiedOn = os.path.getmtime(file_path)
            file_len = file_Len(file_path)
            time.sleep(0.5)
            modified = os.path.getmtime(file_path)
            size = file_Len(file_path)
            if modified != modifiedOn and size != file_len:
                newLines = new_lines(file_path, file_len)
                modifiedOn = modified
                file_len = size
                log_decoder(newLines)

    except Exception as e:
        print(traceback.format_exc())
