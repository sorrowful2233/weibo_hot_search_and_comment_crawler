import datetime
import json
import random

import requests
import pymysql

# 建立数据库连接
cnx = pymysql.connect(host='localhost', port=3306, user='root', password='2233',
                      db='weibo', charset='utf8mb4')

# 创建游标
cursor = cnx.cursor()

# 删除表
drop_table_sql = '''
    drop table if exists hot_search;
'''
cursor.execute(drop_table_sql)

# 创建一个名为hot_search的表
create_table_sql = '''
    CREATE TABLE hot_search (
    date DATE NOT NULL,
    time TIME NOT NULL,
    hot_index INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    raw_hot INT NOT NULL,
    label_name VARCHAR(255) NOT NULL,
    url VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
'''
cursor.execute(create_table_sql)
# UA池
ua_all = [
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/531.2 (KHTML, like Gecko) Chrome/41.0.872.0 Safari/531.2",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows CE; Trident/4.0)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0) AppleWebKit/531.11.4 (KHTML, like Gecko) Version/5.0.2 Safari/531.11.4",
    "Mozilla/5.0 (compatible; MSIE 7.0; Windows 98; Trident/3.1)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 10.0; Trident/5.1)",
    "Opera/8.89.(Windows NT 10.0; lb-LU) Presto/2.9.175 Version/10.00",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/532.2 (KHTML, like Gecko) Chrome/51.0.800.0 Safari/532.2",
    "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/532.16.1 (KHTML, like Gecko) Version/4.0.1 Safari/532.16.1",
    "Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1; Trident/4.0)",
    "Mozilla/5.0 (compatible; MSIE 5.0; Windows NT 5.1; Trident/4.0)",
    "Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.2; Trident/4.1)",
    "Opera/8.96.(Windows CE; yue-HK) Presto/2.9.187 Version/10.00",
    "Mozilla/5.0 (Windows; U; Windows CE) AppleWebKit/534.27.7 (KHTML, like Gecko) Version/4.0.3 Safari/534.27.7",
    "Mozilla/5.0 (compatible; MSIE 5.0; Windows NT 4.0; Trident/5.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.01; Trident/5.1)",
    "Mozilla/5.0 (Windows NT 6.2; sid-ET; rv:1.9.1.20) Gecko/2013-03-13 19:12:24 Firefox/3.6.7",
    "Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 6.1; Trident/5.1)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows CE; Trident/3.1)",
    "Mozilla/5.0 (Windows; U; Windows 95) AppleWebKit/532.41.1 (KHTML, like Gecko) Version/5.1 Safari/532.41.1",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.0; Trident/5.1)",
    "Mozilla/5.0 (Windows NT 6.0; wo-SN; rv:1.9.0.20) Gecko/2012-07-06 02:36:31 Firefox/3.8",
    "Mozilla/5.0 (compatible; MSIE 6.0; Windows 95; Trident/3.1)",
    "Mozilla/5.0 (Windows 95; sc-IT; rv:1.9.0.20) Gecko/2016-03-02 10:47:38 Firefox/3.6.7",
    "Mozilla/5.0 (compatible; MSIE 5.0; Windows NT 5.1; Trident/4.0)",
    "Mozilla/5.0 (compatible; MSIE 7.0; Windows CE; Trident/3.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.0; Trident/5.1)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows 95; Trident/5.1)",
    "Opera/8.39.(Windows 95; da-DK) Presto/2.9.178 Version/10.00",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1) AppleWebKit/535.25.5 (KHTML, like Gecko) Version/4.0 Safari/535.25.5",
    "Opera/9.22.(Windows NT 5.1; szl-PL) Presto/2.9.170 Version/11.00",
    "Opera/8.69.(Windows NT 6.1; ff-SN) Presto/2.9.166 Version/10.00",
    "Mozilla/5.0 (Windows 98) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/27.0.895.0 Safari/535.1",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.2; Trident/3.0)",
    "Opera/9.97.(Windows NT 10.0; uz-UZ) Presto/2.9.170 Version/11.00",
    "Mozilla/5.0 (Windows CE) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/17.0.897.0 Safari/535.1",
    "Opera/9.49.(Windows NT 5.01; ar-MR) Presto/2.9.187 Version/10.00",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.2; Trident/5.0)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 4.0; Trident/5.1)",
    "Opera/9.81.(Windows NT 5.01; ar-OM) Presto/2.9.169 Version/10.00",
    "Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.2; Trident/4.0)",
    "Mozilla/5.0 (compatible; MSIE 5.0; Windows NT 5.0; Trident/5.0)",
    "Opera/9.75.(Windows NT 5.1; ps-AF) Presto/2.9.178 Version/11.00",
    "Opera/8.22.(Windows NT 4.0; tcy-IN) Presto/2.9.181 Version/10.00",
    "Opera/9.91.(Windows NT 5.0; ga-IE) Presto/2.9.177 Version/10.00",
    "Opera/8.70.(Windows NT 5.1; ti-ER) Presto/2.9.163 Version/12.00",
    "Opera/8.35.(Windows 98; Win 9x 4.90; sc-IT) Presto/2.9.186 Version/11.00",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.0 (KHTML, like Gecko) Chrome/55.0.809.0 Safari/535.0",
    "Opera/9.50.(Windows NT 6.0; xh-ZA) Presto/2.9.180 Version/10.00",
    "Mozilla/5.0 (compatible; MSIE 5.0; Windows NT 6.2; Trident/5.1)",
    "Opera/9.28.(Windows NT 5.0; yi-US) Presto/2.9.165 Version/11.00"]

header = {
    "referer": "https://weibo.com/hot/search",
    "User-Agent": random.choice(ua_all),
}

a = requests.get('https://weibo.com/ajax/statuses/hot_band', headers=header)
response = json.loads(a.text)
data = response['data']['band_list']    #取出data键对应的值，然后再从该值中取出band_list键对应的值
for i in data:
    # 获取当前日期和时间
    now = datetime.datetime.now()  #2023-05-08 17:55:16.678888
    # 提取年、月、日
    year = now.year
    month = now.month
    #一直到name变量都是在格式化日期和时间
    if len(str(month)) == 1:
        month = '0' + str(month)
    day = now.day
    if len(str(day)) == 1:
        day = '0' + str(day)
    hour = now.hour
    if len(str(hour)) == 1:
        hour = '0' + str(hour)
    minute = now.minute
    if len(str(minute)) == 1:
        minute = '0' + str(minute)
    second = now.second
    if len(str(second)) == 1:
        second = '0' + str(second)
    date = '{}-{}-{}'.format(year, month, day)
    time = '{}:{}:{}'.format(hour, minute, second)
    name = i['word']  #word是json文件中数据的标题   将i中word的值赋值给变量name  注意i还是所有
    if 'raw_hot' in i:  #raw_hot是热点值  如果这次循环的i中有row_raw_hot将会开始提取这次循环i的数据
        #提取数据到变量,之后会再将数据保存到数据库
        hot_index = i['realpos']
        raw_hot = i['raw_hot']
        label_name = i['label_name']
        datail_name = str(i['word_scheme']).replace('#', '%23')
        url = f'https://s.weibo.com/weibo?q={datail_name}'
        #将变量储存的数据整理好放入data字典
        data = {'date': date, 'time': time, 'hot_index': hot_index, 'name': name, 'raw_hot': raw_hot,
                'label_name': label_name, 'url': url}
        print(data)
        data_tuple = tuple(data.values())  #将数据元祖化   预防SQL注入攻击
        #通过使用占位符（%s）指定了需要插入的值的位置
        add_data = "INSERT INTO hot_search (date, time,hot_index, name, raw_hot, label_name, url) VALUES (%s, %s,%s, %s, %s,%s, %s)"
        cursor.execute(add_data, data_tuple)   #这个代码会将 data_tuple 中的数据按照顺序插入到 add_data 所指定的表中
        cnx.commit()
    else:
        pass

# 关闭游标和数据库连接
cursor.close()
cnx.close()
