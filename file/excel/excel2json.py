from decimal import Decimal

import xlrd
import json
import codecs
import os


def excel2json(file_path):
    # 打开excel文件
    if get_data(file_path) is not None:
        book = get_data(file_path)
        # 抓取所有sheet页的名称
        worksheets = book.sheet_names()
        print("该Excel包含的表单列表为：\n")
        for sheet in worksheets:
            print('%s,%s' % (worksheets.index(sheet), sheet))
        inp = 0
        sheet = book.sheet_by_index(int(inp))
        row_0 = sheet.row(0)  # 第一行是表单标题
        nrows = sheet.nrows  # 行号
        ncols = sheet.ncols  # 列号

        tmp = {}
        for i in range(nrows):
            if i == 0:
                continue
            cur_day = sheet.row_values(i)[8]
            for j in range(ncols):
                title = row_0[j].value
                # 获取单元格的值 i: 行    j:  列
                value = sheet.row_values(i)[j]
                if title == 'hour' or title =='count' or title == 'day':
                    if value != 'null':
                        value = int(value)
                if title == 'percent' and type(value) == float:
                    value = str(Decimal.from_float(value).quantize(Decimal('0.0000')))
                if title == 'hour' and value == 'null':
                    value = ''
                if title == 'sub_label' and type(value) == float:
                    value = int(value)
                tmp[title] = value
            json_data = json.dumps(tmp)
            saveFile(os.getcwd(), worksheets[int(inp)], json_data,cur_day)
            print(json_data)


def get_data(file_path):
    try:
        data = xlrd.open_workbook(file_path)
        return data
    except Exception as e:
        print(u'excel表格读取失败：%s' % e)
        return None


def saveFile(file_path, file_name, data,day):
    output = codecs.open(file_path + "/" + file_name + "-" + str(int(day)) + ".json", 'a', "utf-8")
    output.write(data)
    output.write("\r\n")
    output.close()


if __name__ == '__main__':
    file_path = r"C:\Users\Tak\Documents\youdu\14664168-104213-futx\file\ssxs1103-1116.xlsx"
    excel2json(file_path)

