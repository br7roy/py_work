import random
import sys

import psycopg2

conn = None
cursor = None


def create_custom_flow():
    val = []
    for _ in range(1000):
        val.append((get_random_device_id(), get_random_time(), get_random_day()))

    # 单条插入
    # cursor.execute("insert into custom_flow values ('%s','%sa','%s')")

    # sql = "insert into custom_flow values (%s,%s,%s)"
    sql = "insert into device_distance values (%s,%s)"

    cursor.executemany(sql, val)
    conn.commit()


def get_random_device_id():
    prefix = "uid"
    seed = random.randint(10, 30)
    return prefix + str(seed)


def get_random_day():
    dayArr = ["20200201", "20200202", "20200203", "20200204", "20200205", "20200206"]
    idx = random.randint(0, 5)
    return dayArr[idx]


def get_random_time():
    return random.randint(0, 23)


def close():
    if conn:
        conn.close()


def create_connection(argv):
    global conn, cursor
    conn = psycopg2.connect(database=argv[1], user=argv[2], password=argv[3], host=argv[4],
                            port=argv[5])
    cursor = conn.cursor()
    print("connect ok")

def get_random_distance_label():
    label = ['3公里以内','3~5公里','5~8公里','8~30公里','30公里以外']
    return label[random.randint(0,4)]


def create_device_distance():
    val = []
    for _ in range(1000):
        val.append((get_random_device_id(), get_random_distance_label()))

    sql = "insert into device_distance values (%s,%s)"

    cursor.executemany(sql, val)
    conn.commit()


if __name__ == '__main__':
    create_connection(sys.argv)
    # create_custom_flow()
    create_device_distance()
    close()
