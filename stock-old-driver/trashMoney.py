import baostock as bs
import pandas as pd
import os


# http://baostock.com/baostock/index.php/%E9%A6%96%E9%A1%B5

def run():
    lg = bs.login(user_id="anonymous", password="123456")
    lg.error_msg

    # history data
    rs = bs.query_history_k_data("sh.603121",
                                 "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus , pctChg, peTTM, pbMRQ, psTTM, pcfNcfTTM, isST",
                                 start_date='2020-01-13', end_date='2020-01-22', frequency="d", adjustflag="3")

    rs.error_msg

    total = []

    while (rs.error_code == '0') & rs.next():
        total.append(rs.get_row_data())
    res = pd.DataFrame(total, columns=rs.fields)

    # res.to_csv(os.environ['HOME'] + "\\Desktop\\data.csv", encoding='gbk', index=False)
    print(res)


if __name__ == '__main__':
    run()
