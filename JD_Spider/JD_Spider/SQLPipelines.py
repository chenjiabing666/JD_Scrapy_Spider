# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb


# 实现了在数据库存储的功能
class ManhuaPipeline(object):
    def __init__(self):
        self.con = MySQLdb.connect(user="root", passwd="root", host="localhost", db="JD_Spider", charset="utf8")
        self.cursor = self.con.cursor()
        # self.cursor.execute('use python')
        # self.cursor.execute('create table manhua(name varchar(100) primary key,duty varchar(200),location varchar(200),time varchar(100),sallary varchar(100))')

    def process_item(self, item, spider):
        # 定义插入数据的功能
        # self.cursor.execute("insert into manhua(name,duty,location,time,sallary) values(%s,%s,%s,%s,%s)",(item['name'],item['duty'],item['location'],item['time'],item['sallary']))
        self.cursor.execute(
            "insert into JD(id,shop_url,shop_id,clothes_name,cloths_url,img_url,price,person_number)VALUES (NULL,%s,%s,%s,%s,%s,%s,%s)",
            (item['shop_url'], item['shop_id'],item['cloths_name'],item['cloths_url'],item['img_url'],item['price'],item['person_number']))
        self.con.commit()  # 这是必须要提交的
        return item   #必须要返回一个item
