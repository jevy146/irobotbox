# -*- coding: utf-8 -*-
# @Time    : 2020/5/5 14:56
# @Author  : 结尾！！
# @FileName: query_sql.py
# @Software: PyCharm




import pymysql


def query_order_select(sql_str):
    # 连接数据库
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        port=3306,
        password='1234',
        db='operating',  # 运营数据库
        charset='utf8'
    )

    # 创建游标
    cursor = conn.cursor()
    # 书写sql语句

    # #执行sql语句
    try:
        cursor.execute(sql_str)
        # 提交连接
        conn.commit()
        data = cursor.fetchall()

        # data = cursor.fetchone()  #返回第一个

    except Exception as e:

        print('错误查找:',e)
        conn.rollback()
    # 关闭游标，关闭连接
    finally:
        cursor.close()
        conn.close()
        return data


def query_order_insert(sql_str):
    # 连接数据库
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        port=3306,
        password='1234',
        db='operating',  # 运营数据库
        charset='utf8'
    )

    # 创建游标
    cursor = conn.cursor()
    # 书写sql语句

    # #执行sql语句
    try:
        cursor.execute(sql_str)
        # 提交连接
        conn.commit()
        # data = cursor.fetchall()

        # data = cursor.fetchone()  #返回第一个

    except Exception as e:
        print('错误写入:', sql_str)
        print('错误写入:',e)
        conn.rollback()
    # 关闭游标，关闭连接
    finally:
        cursor.close()
        conn.close()



if __name__ == '__main__':
    pass


