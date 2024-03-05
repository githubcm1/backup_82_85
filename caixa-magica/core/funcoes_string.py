import re

def remove_special(string):
    string = string.strip()
    cleanString = re.sub('\W+',' ', string )
    return cleanString

def ucase(string, rem_special = True):
    if rem_special == True:
        return remove_special(string).upper()
    else:
        return string.strip().upper()

