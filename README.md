# SCrapy爬虫大战京东商城

## 引言
>**上一篇已经讲过怎样获取链接，怎样获得参数了，详情请看[python爬取京东商城普通篇](https://chenjiabing666.github.io/2017/04/23/python%E7%88%AC%E8%99%AB%E5%A4%A7%E6%88%98%E4%BA%AC%E4%B8%9C%E5%95%86%E5%9F%8E/)**

## 代码详解

>* **首先应该构造请求，这里使用[scrapy.Request](http://scrapy-chs.readthedocs.io/zh_CN/0.24/topics/spiders.html),这个方法默认调用的是`start_urls`构造请求，如果要改变默认的请求，那么必须重载该方法，这个方法的返回值必须是一个可迭代的对象，一般是用`yield`返回，代码如下：**

```python
    def start_requests(self):
        for i in range(1,101):
            page=i*2-1    #这里是构造请求url的page,表示奇数
            url=self.start_url+str(page)
            yield scrapy.Request(url,meta={'search_page':page+1},callback=self.parse_url)   #这里使用meta想回调函数传入数据，回调函数使用response.meta['search-page']接受数据
```

>**下面就是解析网页了，从上面看出这里的解析回调函数是`parse_url`,因此在此函数中解析网页。这里还是和上面说的一样，这个`url`得到的仅仅是前一半的信息，如果想要得到后一半的信息还有再次请求，这里还有注意的就是一个技巧：一般先解析出一个数据的数组，不急着取出第一个数，先要用if语句判断，因为如果得到的是`[]`，那么直接取出`[0]`是会报错的，这只是一个避免报错的方法吧，代码如下:**

```python
    def parse_url(self,response):
        if response.status==200:   #判断是否请求成功
            # print response.url
            pids = set()    #这个集合用于过滤和保存得到的id,用于作为后面的ajax请求的url构成
            try:
                all_goods = response.xpath("//div[@id='J_goodsList']/ul/li")   #首先得到所有衣服的整个框架，然后从中抽取每一个框架

                for goods in all_goods:   #从中解析每一个
                    # scrapy.shell.inspect_response(response,self)   #这是一个调试的方法，这里会直接打开调试模式
                    items = JdSpiderItem()   #定义要抓取的数据
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

            yield scrapy.Request(url=self.search_url.format(str(response.meta['search_page']),",".join(pids)),callback=self.next_half_parse)    #再次请求，这里是请求ajax加载的数据，必须放在这里，因为只有等到得到所有的pid才能构成这个请求，回调函数用于下面的解析
```

>* **从上面代码的最后可以看出最后就是解析`ajax`加载的网页了，这里调用的`next_half_parse`函数，和解析前面一个网页一样，这里需要的注意的是，如果前面定义的数据没有搜索完毕是不能使用`yield items`的，必须将items通过meta传入下一个回调函数继续完善后才能`yield items`,这里就不需要了，代码如下：**

```python
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
                    yield items   #又一次的生成，这里是完整的数据，因此可以yield items
            except Exception:
                print "**************************************************"
```

>* **当然这里还用到了设置请求池，`mysql`存储，没有使用到`ip`代理，这个在我前面的博客中又讲到，这里就不再赘述了，想看源代码的朋友请[点击这里](https://github.com/chenjiabing666/JD_Scrapy_Spider)**

## 小技巧
>* **人们会抱怨为什么自己的爬虫在中途断开就要重头开始爬，为什么不能从断开那里开始爬呢，这里提供一个方法：在配置文件`settings.py`中加入`JOBDIR=file_name`,这里的`file_name`是一个文件的名字**

>* **设置下载延迟防止被`ban`:`DOWNLOAD_DELAY = 2`:设置每一次的间隔时间   `RANDOMIZE_DOWNLOAD_DELAY = True`:这个是随机设置延迟时间  在设置的时间的`0.5-1.5`倍之间，这样可以更有效的防止被ban,一般是配套使用的**

>* **`ROBOTSTXT_OBEY = False` :这里是表示不遵循`robots.txt`文件，默认是`True`表示遵循，这里将之改成`False`**

>* **`CONCURRENT_REQUESTS` :设置最大请求数，这里默认的时`16`，我们可以根据自己电脑的配置改的大一点来加快请求的速度**

