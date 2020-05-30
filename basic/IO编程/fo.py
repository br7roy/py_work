def run():
    path = r'C:\Users\Administrator\Desktop\new.txt'
    kw = 'https:'
    text = ''
    with open(path, 'r', encoding='utf8') as rf:
        for line in rf:
            if kw in line:
                sin = line.index(kw)
                try:
                    ein = line.index("</")
                    text += line[sin:ein]
                except:
                    text += line[sin:]
                    pass

                text += '\n'
    with open(path, 'w', encoding='utf8') as wf:
        for t in text:
            wf.write(t)


if __name__ == '__main__':
    run()
