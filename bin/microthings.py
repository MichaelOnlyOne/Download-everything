from . import language
import os
def setlang(lang=None):
    language.load(lang)
def write_if_empty(file_path, text):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
def read_links_from_file(file_path):
    links = []
    if not os.path.exists(file_path):
        return links
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            clean_line = line.strip()
            if not clean_line or clean_line.startswith('#'):
                continue
                
            if ' #' in clean_line:
                clean_line = clean_line.split(' #')[0].strip()
            elif '#' in clean_line and not clean_line.startswith('http'):
                clean_line = clean_line.split('#')[0].strip()
                
            if clean_line:
                links.append(clean_line)
    return links
def makesafename(safe_name):
    safe_name = safe_name.replace('/', '-').replace('\\', '-').replace(':', ' -')
    safe_name = regex.sub(r'[^\p{L}\p{N}\s\-\_ \(\)\[\]]', '', safe_name)
    safe_name = regex.sub(r'\s+', ' ', safe_name).strip()
    if len(safe_name) > 100:
        safe_name = safe_name[:100].strip()
    return safe_name
def inputnumber(a,b=None):
    if b == None:
        b,a = a,1
    while True:
        inp = input("> ")
        if not inp.isdigit():
            print(language.getword("inputnumber.neutralnumber"))
            continue
        val = int(inp)
        if val not in range(a, b+1): 
            print(language.getword("inputnumber.range",{"a":a,"b":b}))
            continue
        return val