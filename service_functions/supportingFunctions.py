import datetime
import os
import shutil


def decorator(func):
    def wrapper(*args, **kwargs):
        start = datetime.datetime.now()
        result = func(*args, **kwargs)
        stop = datetime.datetime.now()
        c = stop - start
        with open("allData/report/reportFuncDuration.txt", "a") as fRep:
            fRep.write(f"\n{func.__name__} duration:  {c}")
        return result

    return wrapper


def isNull(*args):
    for var in args:
        if len(var) == 0:
            return True
        elif len(var) > 0:
            return False


def checkEmptyFile(filename, repFile):
    with open(filename, "r") as file:
        lines = file.readlines()
        if lines.__len__() == 0 or str("Report for " + repFile) not in lines[0]:
            file.close()
            return True
