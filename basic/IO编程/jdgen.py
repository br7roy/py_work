import sys
import os


def run():
    path = r''

    kw = r'/rust'
    try :
        for root, dirs, files in os.walk(path):
            for file in files:
                data = ""
                fp = os.path.join(root, file)
                with open(fp, 'r', encoding='utf-8') as f:
                    for line in f:
                        if kw in line:
                            line = line.replace(kw, '')
                        data += line
                with open(fp, 'w', encoding='utf-8')as f:
                    f.write(data)
        print("ok")
    except e:
        print("error happen")





# if __name__ == '__main__':

run()
