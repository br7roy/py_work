def transform(path):
    lines = ''
    with open(path, 'r', encoding="utf-8") as f:
        for line in f:
            if "," in line:
                line = line.replace(",", "] ")
            lines += line
    with open(path, 'w', encoding="utf-8")as f:
        f.write(lines)


if __name__ == '__main__':
    path = r'C:\Users\Administrator\Desktop\19-09-12-电视多m3u8.txt'
    transform(path)
