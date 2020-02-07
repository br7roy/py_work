# 修改文件中的字符串
import sys
import os


def run():
    path = r'E:\Developer\project\pronetway\combat-platform\src'
    # path = r'E:\hello'
    for root, dirs, files in os.walk(path):
        for file in files:
            data = ""
            fp = os.path.join(root, file)
            with open(fp, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'Rust' in line:
                        line = line.replace('Rust', 'Tak')
                    data += line
            with open(fp, 'w', encoding='utf-8')as f:
                f.write(data)


if __name__ == '__main__':
    run()
