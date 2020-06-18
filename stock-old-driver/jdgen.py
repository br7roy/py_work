import os


def run():
    path = r'D:\project\github\hadoop-ecosystem'

    kw = r'com.rust'
    try:
        for root, dirs, files in os.walk(path):
            if ".git "  in root: continue
            for file in files:
                if file.endswith(".jar") or file.endswith(".class") or file.endswith(".jar.original") \
                        or file.endswith(".git"):
                    continue
                if not file.endswith(".java") and not file.endswith(".scala") \
                        and not file.endswith("pom.xml") \
                        and not file.endswith(".jsp"):
                    continue
                data = ""
                fp = os.path.join(root, file)
                with open(fp, 'r', encoding='utf-8') as f:
                    for line in f:
                        if kw in line:
                            line = line.replace(kw, r'tk.tak')
                        data += line
                with open(fp, 'w', encoding='utf-8')as f:
                    f.write(data)
        print("ok")
    except Exception as e:
        print("error happen", e)


if __name__ == '__main__':
    run()
