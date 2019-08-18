import re

total = {'': [[], 0]}


def something():
    pattern = re.compile('.*uid=(?P<uid>.*?),.*custId=(?P<custId>.*?),.*')
    # str = '[sid=5087716][custId=30418710]uid=3cdbe063ebce8681160312be09db4b7e, clientIp=125.124.66.227, ' \
    #       'custId=30418710, sessionId=5087716, goldCoin=0, diamond=0, exp=0[0, 0, 1, 0, 3, 0, 14, 0] '
    # res = pattern.search(str)
    # print(res.group(1))
    # print(res.group(2))
    # print(res.groupdict())
    path = r'C:\Users\Administrator\Desktop\test2.log'
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            res = pattern.search(line)
            if not res:
                continue
            groupdict = res.groupdict()
            uid = groupdict['uid']
            custId = groupdict['custId']
            if uid in total.keys():
                val = total[uid]
                custIds = val[0]
                custIds.append(custId)
                cnt = val[1]
                val[1] = cnt + 1
            else:
                total.update({uid: [[custId], 1]})


if __name__ == '__main__':
    something()
    print(total)
