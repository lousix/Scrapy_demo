import scrapy
from scrapy.http import FormRequest
from mySpider.items import MyspiderItem
import re
import datetime


class ScrapyjdwxSpider(scrapy.Spider):
    name = 'scrapyJDWX'
    # allowed_domains = ['https://wx.jdcloud.com']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        'X-Requested-With': "XMLHttpRequest",
    }

    def start_requests(self):
        font_url = "https://wx.jdcloud.com/search/getDatas?keyword=&charge=2&page="
        for i in range(1, 64):
            url = font_url + str(i)
            request = FormRequest(url, callback=self.parse, headers=self.headers, dont_filter=True)
            yield request

    def parse(self, response):
        # filename = "test.html"
        # open(filename, 'wb').write(response.body)
        for each in response.xpath("//li[@class=\"boder_v1\"]"):
            # 从主页爬虫部分数据
            item = MyspiderItem()
            name = each.xpath("a/h3/text()").extract()
            price = each.xpath("a/p/text()").extract()
            bro_eval = each.xpath("div/p/text()").extract()
            type = each.xpath("div/ul/li/p/text()").extract()
            item['name'] = name[0].strip()
            item['type'] = type[0].strip()
            p = re.compile(r'[(](.*?)[)]', re.S)
            s = re.findall(p, bro_eval[0].strip())
            item['browse'] = s[0]
            item['evaluation'] = s[1]
            item['trade'] = 0
            item['trade_year'] = 0
            item['trade_mouth'] = 0
            item['trade_week'] = 0
            if 'API' not in item['type']:
                item['price'] = price[0].strip()

            # 进入具体的页面进行爬虫
            href = each.xpath("a").extract()
            p_url = re.compile(r'href="(.*?)"')
            inline_url = "https://wx.jdcloud.com" + re.findall(p_url, href[0].strip())[0]
            # print('inline_url = ', inline_url)
            yield scrapy.FormRequest(url=inline_url,
                                     callback=self.inline_parse,
                                     headers=self.headers,
                                     meta={'item': item,
                                           'url': inline_url})

    def inline_parse(self, response):
        # 获取上个界面的item
        item = response.meta['item']

        # 爬取页面数据
        entity = response.xpath('//*[@id="app"]')

        data_format = response.xpath('//*[@id="intro"]/ul/li[2]/span[1]').extract()
        file_type = response.xpath('//*[@id="intro"]/ul/li[1]/span[2]').extract()
        size = response.xpath('//*[@id="intro"]/ul/li[1]/span[1]').extract()
        time = response.xpath('//*[@id="intro"]/ul/li[2]/span[2]').extract()
        tag = entity.xpath('section/div[1]/div[1]/div/div[2]/ul/li[2]/span[2]/a/text()').extract()

        p = re.compile(r'[(](.*?)[)]', re.S)  # 正则表达式定义1
        p_not_api = re.compile(r'</span>(.*)</span>', re.S)  # 正则表达式定义2

        if 'API' in item['type']:
            # trade = response.xpath('//*[@id="detailTab6"]/a/span/text()').extract()
            # //*[@id="detailTab6"]/a/span   //*[@id="detailTab5"]/a/span
            trade = response.xpath('//*[@id="detailTab6"]/a/span').extract()
            if len(trade) == 0:
                trade = response.xpath('//*[@id="conBox"]/nav/ul/li[6]/span').extract()
            # trade = response.xpath('//*[@id="app"]/section/div[1]/div[1]/div/div[1]/ul/li[2]/span/text()').extract()
            price = response.xpath('//*[@id="specs"]/div/div[2]/p/span/text()').extract()
            print('trade number = ', trade)
            print('price = ', len(price))
            print('tag = ', len(tag))
            # item['trade'] = trade[0].strip()
            item['price'] = price[0][5::].strip()
            item['tag'] = tag[0].strip()
            url = response.meta['url'].split("/")[-1]
            print(url)
            item = scrapy.FormRequest('https://wx.jdcloud.com/order/orderPageList',
                                      formdata={'pageNow': '1',
                                                'id': url,
                                                'type': '0'},
                                      callback=self.calculate,
                                      headers=self.headers,
                                      dont_filter=True,
                                      meta={'item': item,
                                            'url': url,
                                            'status': '0',
                                            'number': '0'})

        else:
            trade = response.xpath('//*[@id="conBox"]/nav/ul/li[3]/text()').extract()
            s = re.findall(p, trade[0].strip())  # 符合正则表达式1的内容
            item['trade'] = s[0].strip()

            item['data_format'] = re.findall(p_not_api, data_format[0].strip())[0].strip()
            item['file_type'] = re.findall(p_not_api, file_type[0].strip())[0].strip()
            item['size'] = re.findall(p_not_api, size[0].strip())[0].strip()
            item['time'] = re.findall(p_not_api, time[0].strip())[0].strip()
            item['tag'] = tag[0].strip()
        return item

    def calculate(self, response):
        open("test5.html", "wb").write(response.body)
        number = '0'
        int_number = 0
        if response.meta['status'] == '0':
            rule = re.compile(r"totalCount:'(.*?)'", re.S)
            number = re.findall(rule, bytes.decode(response.body))[0]
            int_number = int(number) // 10 + 1
        elif response.meta['status'] == '1':
            int_number = int(response.meta['number'])
        print('int_number = ', int_number)
        item = response.meta['item']
        if int_number >= 2:
            for i in range(1, 11):
                date = response.xpath('/html/body/table/tbody/tr[' + str(i) + ']/td[2]/text()').extract()
                count = response.xpath('/html/body/table/tbody/tr[' + str(i) + ']/td[3]/text()').extract()

                p = re.compile(r'(.*)次', re.S)
                num = re.findall(p, count[0].strip())
                print('num = ', num)
                if len(date) == 0 or len(num) == 0:
                    print('failed')
                    break
                else:
                    today = datetime.date.today()
                    trade_day = datetime.datetime.strptime(date[0].strip(), '%Y/%m/%d').date()
                    day = (today - trade_day).days
                    item['trade'] = item['trade'] + int(num[0].strip())
                    if day <= 365:
                        print("add year")
                        item['trade_year'] = item['trade_year'] + int(num[0].strip())
                    if day <= 30:
                        print("add mouth")
                        item['trade_mouth'] = item['trade_mouth'] + int(num[0].strip())
                    if day <= 7:
                        print("add week")
                        item['trade_week'] = item['trade_week'] + int(num[0].strip())
            int_number = int_number - 1
            item = scrapy.FormRequest('https://wx.jdcloud.com/order/orderPageList',
                                      formdata={'pageNow': str(int_number),
                                                'id': response.meta['url'],
                                                'type': '0'},
                                      callback=self.calculate,
                                      headers=self.headers,
                                      dont_filter=True,
                                      meta={'item': item,
                                            'url': response.meta['url'],
                                            'status': '1',
                                            'number': str(number)})
        return item

# scrapy crawl scrapyJDWX -o test2.csv
