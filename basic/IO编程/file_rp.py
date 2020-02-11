# 修改文件目录下所有文件，将文件中内容匹配的字符串进行替换
import sys
import os


def run():
    path = r'E:\Developer\project\github\experiment\src\main\java'
    # path = r'E:\hello'
    for root, dirs, files in os.walk(path):
        for file in files:
            data = ""
            fp = os.path.join(root, file)
            with open(fp, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'rust' in line:
                        line = line.replace('rust', 'tak')
                    data += line
            with open(fp, 'w', encoding='utf-8')as f:
                f.write(data)


if __name__ == '__main__':
    run()
