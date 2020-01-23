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

    res.to_csv(os.environ['HOMEPATH'] + "\\Desktop\\data.csv", encoding='gbk', index=False)
    print(res)


def get_all_stock_data_by_day(date):
    stock_rs = bs.query_all_stock(date)
    stock_df = stock_rs.get_data()
    data_df = pd.DataFrame()
    for code in stock_df["code"]:
        print("Downloading :" + code)
        k_rs = bs.query_history_k_data_plus(code, "date,code,open,high,low,turn,liqaShare,close", date, date)
        data_df = data_df.append(k_rs.get_data())
    data_df.to_csv(r"C:\Users\Administrator\Desktop\data.csv")
    print(data_df)


def open():
    df = pd.DataFrame(pd.read_csv(r"C:\Users\Administrator\Desktop\data.csv", header=0, encoding='gbk'))
    res = df.loc[df["turn"] < "1.0"]
    print(res)


if __name__ == '__main__':
    # run()
    # get_all_stock_data_by_day("2020-01-22")
    open()
