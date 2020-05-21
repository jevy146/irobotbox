# -*- coding: utf-8 -*-
# @Time    : 2020/5/5 14:09
# @Author  : 结尾！！
# @FileName: add_data_irobotbox.py
# @Software: PyCharm


#调用赛盒的数据

from query_sql import query_order_select,query_order_insert
import time
import requests
def get_data(StartTime,EndTime,NextToken):
    url = 'http://sgt.irobotbox.com/Api/API_Irobotbox_Orders.asmx?op=GetOrders'
    data_raw = f'''<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <GetOrders xmlns="http://tempuri.org/"><orderRequest>
                <CustomerID>1275</CustomerID>
                <UserName>S046</UserName>
                <Password>Jw369</Password>
                <StartTime>{StartTime}</StartTime>
                <EndTime>{EndTime}</EndTime>
                <NextToken>{NextToken}</NextToken>
              </orderRequest>
            </GetOrders>
          </soap:Body>
        </soap:Envelope>'''
    response = requests.post(url=url, data=data_raw, headers={'Content-Type': 'text/xml'})
    print(response.status_code)
    return response.text

from xml.etree import ElementTree as ET

def parse_xml(res_text):
    root = ET.fromstring(res_text) #传入一个字符串
    Body=root.getchildren()
    GetOrdersResponse = Body[0].getchildren()
    GetOrdersResult = GetOrdersResponse[0].getchildren()
    OrderInfoList = GetOrdersResult[0].getchildren()
    ApiOrderInfo = OrderInfoList[1].getchildren()
    NextToken = OrderInfoList[2].text  #获取下一页的钥匙
    count = 0
    info_data = []
    for OrderInfo in ApiOrderInfo:
        #     print(OrderInfo.getchildren())
        data_info = {}  # 保存支付每个订单的信息
        for each_OrderInfo in OrderInfo:
            # print(each_OrderInfo.tag)
            # print(each_OrderInfo.text)  {http://tempuri.org/}OrderCode
            if 'OrderCode' == each_OrderInfo.tag[21:]:
                #赛盒订单号
                data_info["OrderCode"] = each_OrderInfo.text

            if 'ClientOrderCode' in each_OrderInfo.tag:
                #平台订单号
                data_info["ClientOrderCode"] = each_OrderInfo.text

            if 'OrderSourceName' in each_OrderInfo.tag:
                #来源渠道名称  Amazon-D1-ES
                data_info["OrderSourceName"] = each_OrderInfo.text

            if 'TotalPrice' in each_OrderInfo.tag:
                #订单金额
                data_info["TotalPrice"] = each_OrderInfo.text
            if 'Country' in each_OrderInfo.tag:
                #收货人国家
                data_info["Country"] = each_OrderInfo.text
            if 'Currency' in each_OrderInfo.tag:
                #货币
                data_info["Currency"] = each_OrderInfo.text

            if 'Province' in each_OrderInfo.tag:
                #收货人省份
                data_info["Province"] = each_OrderInfo.text
            if 'City' in each_OrderInfo.tag:
                #收货人城市
                data_info["City"] = each_OrderInfo.text
            if 'PostCode' in each_OrderInfo.tag:
                #邮编
                data_info["PostCode"] = each_OrderInfo.text

            if 'PayTime' in each_OrderInfo.tag:
                #订单支付时间
                data_info["PayTime"] = each_OrderInfo.text

            if 'OrderList' in each_OrderInfo.tag:
                OrderList = each_OrderInfo.getchildren()
                for each_Order in OrderList:
                    # print('each_Order', each_Order)
                    ApiOrderList = {}  # 将每个订单的详细信息保存为字典
                    for each in each_Order.getchildren():
                        # print(each.tag[21:],each.text)
                        ApiOrderList[each.tag[21:]] = each.text
                    data_info.update(ApiOrderList)
                    count += 1
                    #print(data_info)
                    info_data.append(data_info)
                    # print('*' * 20, count)
    print('*' * 20, count)

    return {'NextToken':NextToken,'info_data':info_data}



def save_data_to_sql(dict_each):

    # 用赛盒的订单号作为唯一的标识，ClientOrderCode有重复的None
    sql_select = f"SELECT ClientOrderCode ,OrderCode FROM irobotbox_data WHERE ClientOrderCode='{dict_each['ClientOrderCode']}'; "
    #1.查询，是否已经有数据了。
    print('查询语句\n', sql_select)
    return_select=query_order_select(sql_select)
    print('return_select',return_select)
    #1.1如果没有查找到，就将数据写入
    if len(return_select) == 0:
        sql_insert = f'''INSERT INTO irobotbox_data (ClientOrderCode,PayTime,ClientSKU,SellerSKU,ASIN,ProductNum,ItemTitle,ProductLinks,BusinessAdminName,PayDate,Country,TotalPrice,OrderSourceName,Province,City,PostCode,OrderCode)  VALUES("{dict_each['ClientOrderCode']}","{dict_each['PayTime']}","{dict_each['ClientSKU']}","{dict_each['SellerSKU']}","{dict_each['ASIN']}",{int(dict_each['ProductNum'])},"{dict_each['ItemTitle']}","{dict_each['ProductLinks']}","{dict_each['BusinessAdminName']}","{dict_each['PayTime'].split(' ')[0]}","{dict_each['Country']}","{float(dict_each['TotalPrice'])}","{dict_each['OrderSourceName']}","{dict_each['Province']}","{dict_each['City']}","{dict_each['PostCode']}","{dict_each['OrderCode']}");'''
        print("插入数据--付款日期",dict_each['PayTime'].split(' ')[0])
        #2.执行插入的sql语句。
        query_order_insert(sql_insert)
    else:
        print("数据已有。。。",dict_each['ClientOrderCode'],dict_each['OrderCode'])


def save_data(dict_list):
    file_name=dict_list['NextToken']
    print(f"正在保存相应的NextToken为{file_name}文件")
    for dict_each in dict_list['info_data']:
        #执行将数据保存到mysql数据库中
        save_data_to_sql(dict_each)


def main(NextToken):
    if int(NextToken) >=0:
        StartTime, EndTime="2020-02-01","2020-03-01"  #输入开始时间和结束时间,时间不能相同
        print('NextToken',NextToken)
        xml_text = get_data(StartTime, EndTime, NextToken) #1.传入下一页的钥匙
        data_save = parse_xml(xml_text) #2.解析响应的xml文件
        Next_Token = data_save['NextToken']  #
        save_data(data_save) #3.保存到本地 将需要保存的数据整体传入
        time.sleep(1.5)
        main(Next_Token)
    else:
        return


if __name__ == '__main__':
    #NextToken 起始值设置为0,最后的值为-1,运行结束
    NextToken=0
    main(NextToken)

