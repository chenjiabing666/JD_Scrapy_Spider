# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    img_url=scrapy.Field()   #图片url
    price=scrapy.Field()  #价格
    cloths_name=scrapy.Field()  #衣服的名字
    cloths_url=scrapy.Field()   #衣服的链接
    shop_id=scrapy.Field()     #商店的id
    shop_url=scrapy.Field()    #商店的url
    person_number=scrapy.Field()   #评价人数
    # comments=scrapy.Field()




