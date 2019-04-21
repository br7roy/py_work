import requests


def get_html(url):
    global res
    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        res = r.text
    except Exception as e:
        print("error:")
        print(e)
    return res


def get_photo():
    r = requests.get("http://image.ngchina.com.cn/2019/0419/20190419053648496.jpg")
    r.raise_for_status()
    with open("c://Users/Administrator/Desktop/2.jpg", 'xb') as file:
        file.write(r.content)
        file.close()


def get_photo_2():
    import os
    url = "http://image.ngchina.com.cn/2019/0419/20190419053648496.jpg"
    root = "c://Users/Administrator/Desktop/pic"
    path = root + url.split('/')[-1]
    r = requests.get(url)

    try:
        if not os.path.exists(root):
            os.mkdir(root)
        if not os.path.exists(path):
            with open(path, 'wb') as f:
                f.write(r.content)
                f.close()
                print('文件已保存')
        else:
            print('文件已存在')
    except Exception as e:
        print('爬取失败')
        print(e)


if __name__ == '__main__':
    get_photo()
    # print(get_html("https://www.baidu.com"))
