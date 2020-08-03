import baostock as bs
import pandas as pd
import os


# http://baostock.com/baostock/index.php/%E9%A6%96%E9%A1%B5

# 获取单只股票某一日数据
def get_one_stock_data_by_day(stime, etime, stock_name):
    lg = bs.login(user_id="anonymous", password="123456")
    lg.error_msg

    # history data
    rs = bs.query_history_k_data(stock_name,
                                 "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus , pctChg, peTTM, pbMRQ, psTTM, pcfNcfTTM, isST",
                                 start_date=stime, end_date=etime, frequency="d", adjustflag="3")

    rs.error_msg

    total = []

    while (rs.error_code == '0') & rs.next():
        total.append(rs.get_row_data())
    res = pd.DataFrame(total, columns=rs.fields)

    res.to_csv(r"C:\Users\Administrator\Desktop\data.csv", encoding='gbk', index=False)
    print(res)


# 获取一天所有股票数据
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


# 读取csv
def read():
    df = pd.DataFrame(pd.read_csv(r"C:\Users\Administrator\Desktop\data.csv", header=0, encoding='gbk'))
    res = df.loc[df["turn"] < "1.0"]
    print(res)


if __name__ == '__main__':
    get_one_stock_data_by_day('2020-07-25','2020-08-03' ,'sh.603121')
    # get_all_stock_data_by_day("2020-01-22")
    # read()
