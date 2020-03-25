import os


def run():
    path = r'D:\project\proneteway\ideaprj\video-security\video-security'

    kw = r'Rust'
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".jar") or file.endswith(".class") or file.endswith(".jar.original"):
                    continue
                data = ""
                fp = os.path.join(root, file)
                with open(fp, 'r', encoding='utf-8') as f:
                    for line in f:
                        if kw in line:
                            line = line.replace(kw, 'Tak')
                        data += line
                with open(fp, 'w', encoding='utf-8')as f:
                    f.write(data)
        print("ok")
    except Exception as e:
        print("error happen", e)


if __name__ == '__main__':
    run()
