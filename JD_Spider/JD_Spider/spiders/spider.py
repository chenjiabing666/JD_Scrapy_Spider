# -*- coding: utf-8 -*-
import scrapy
from JD_Spider.items import JdSpiderItem
import scrapy.shell
from bs4 import BeautifulSoup
import lxml
import time


class SpiderSpider(scrapy.Spider):
    name = "spider"
    #allowed_domains = ["jd.com"]
    #start_urls = ['http://jd.com/']
    count=1
    start_url= 'https://search.jd.com/Search?keyword=%E8%A3%A4%E5%AD%90&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&offset=5&wq=%E8%A3%A4%E5%AD%90&page='
    search_url='https://search.jd.com/s_new.php?keyword=%E8%A3%A4%E5%AD%90&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&offset=3&wq=%E8%A3%A4%E5%AD%90&page={0}&s=26&scrolling=y&pos=30&show_items={1}'
    #comments_url="https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv1049&productId={0}&score=0&sortType=5&page={1}&pageSize=10"
    #这是准备用来抓取评论的，但是懒得写了

    def start_requests(self):
        for i in range(1,101):
            page=i*2-1
            url=self.start_url+str(page)
            yield scrapy.Request(url,meta={'search_page':page+1},callback=self.parse_url)   #这里使用meta想回调函数传入数据，回调函数使用response.meta['search-page']接受数据



    def parse_url(self,response):
        if response.status==200:
            # print response.url
            pids = set()
            try:
                all_goods = response.xpath("//div[@id='J_goodsList']/ul/li")

                for goods in all_goods:
                    # scrapy.shell.inspect_response(response,self)
                    items = JdSpiderItem()
                    img_url_src = goods.xpath("div/div[1]/a/img/@src").extract()  # 如果不存在就是一个空数组[]，因此不能在这里取[0]
                    img_url_delay = goods.xpath(
                        "div/div[1]/a/img/@data-lazy-img").extract()  # 这个是没有加载出来的图片，这里不能写上数组取第一个[0]
                    price = goods.xpath("div/div[3]/strong/i/text()").extract()  #价格
                    cloths_name = goods.xpath("div/div[4]/a/em/text()").extract()
                    shop_id = goods.xpath("div/div[7]/@ data-shopid").extract()
                    cloths_url = goods.xpath("div/div[1]/a/@href").extract()
                    person_number = goods.xpath("div/div[5]/strong/a/text()").extract()
                    pid = goods.xpath("@data-pid").extract()
                    # product_id=goods.xpath("@data-sku").extract()
                    if pid:
                        pids.add(pid[0])
                    if img_url_src:  # 如果img_url_src存在
                        print img_url_src[0]
                        items['img_url'] = img_url_src[0]
                    if img_url_delay:  # 如果到了没有加载完成的图片，就取这个url
                        print img_url_delay[0]
                        items['img_url'] = img_url_delay[0]  # 这里如果数组不是空的，就能写了
                    if price:
                        items['price'] = price[0]
                    if cloths_name:
                        items['cloths_name'] = cloths_name[0]
                    if shop_id:
                        items['shop_id'] = shop_id[0]
                        shop_url = "https://mall.jd.com/index-" + str(shop_id[0]) + ".html"
                        items['shop_url'] = shop_url
                    if cloths_url:
                        items['cloths_url'] = cloths_url[0]
                    if person_number:
                        items['person_number'] = person_number[0]
                    # if product_id:
                    #     print "************************************csdjkvjfskvnk***********************"
                    #     print self.comments_url.format(str(product_id[0]),str(self.count))
                    #     yield scrapy.Request(url=self.comments_url.format(str(product_id[0]),str(self.count)),callback=self.comments)
                    #yield scrapy.Request写在这里就是每解析一个键裤子就会调用回调函数一次
                    yield items
            except Exception:
                print "********************************************ERROR**********************************************************************"

            yield scrapy.Request(url=self.search_url.format(str(response.meta['search_page']),",".join(pids)),callback=self.next_half_parse)

    #分析异步加载的网页
    def next_half_parse(self,response):
        if response.status==200:
            print response.url
            items=JdSpiderItem()
            #scrapy.shell.inspect_response(response,self)    #y用来调试的
            try:
                lis=response.xpath("//li[@class='gl-item']")
                for li in lis:
                    cloths_url=li.xpath("div/div[1]/a/@href").extract()
                    img_url_1=li.xpath("div/div[1]/a/img/@src").extract()
                    img_url_2=li.xpath("div/div[1]/a/img/@data-lazy-img").extract()
                    cloths_name=li.xpath("div/div[4]/a/em/text()").extract()
                    price=li.xpath("div/div[3]/strong/i/text()").extract()
                    shop_id=li.xpath("div/div[7]/@data-shopid").extract()
                    person_number=li.xpath("div/div[5]/strong/a/text()").extract()
                    if cloths_url:
                        print cloths_url[0]
                        items['cloths_url']=cloths_url[0]
                    if img_url_1:
                        print img_url_1[0]
                        items['img_url']=img_url_1
                    if img_url_2:
                        print img_url_2[0]
                        items['img_url']=img_url_2[0]
                    if cloths_name:
                        items['cloths_name']=cloths_name[0]
                    if price:
                        items['price']=price[0]
                    if shop_id:
                        items['shop_id']=shop_id[0]
                        items['shop_url']="https://mall.jd.com/index-" + str(shop_id[0]) + ".html"
                    if person_number:
                        items['person_number']=person_number[0]
                    yield items
            except Exception:
                print "**************************************************"

    def comments(self,response):
        pass








