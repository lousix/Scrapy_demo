import scrapy
from scrapy.http import FormRequest
from mySpider.items import MyspiderItem
import re

class ScrapyjdwxSpider(scrapy.Spider):
    name = 'scrapyJDWX'
    #allowed_domains = ['https://wx.jdcloud.com']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        'X-Requested-With': "XMLHttpRequest",
    }
    def start_requests(self):
        font_url = "https://wx.jdcloud.com/search/getDatas?keyword=&charge=2&page="
        for i in range(1,64):
            url = font_url + str(i)
            request = FormRequest(url, callback=self.parse, headers=self.headers, dont_filter=True)
            yield request


    def parse(self, response):
        #filename = "test.html"
        #open(filename, 'wb').write(response.body)
        for each in response.xpath("//li[@class=\"boder_v1\"]"):
            #从主页爬虫部分数据
            item = MyspiderItem()
            name = each.xpath("a/h3/text()").extract()
            price = each.xpath("a/p/text()").extract()
            bro_eval = each.xpath("div/p/text()").extract()
            type = each.xpath("div/ul/li/p/text()").extract()
            item['name'] = name[0].strip()
            item['price'] = price[0].strip()
            item['type'] = type[0].strip()
            p = re.compile(r'[(](.*?)[)]', re.S)
            s = re.findall(p, bro_eval[0].strip())
            item['browse'] = s[0]
            item['evaluation'] = s[1]

            # 进入具体的页面进行爬虫
            href = each.xpath("a").extract()
            p_url = re.compile(r'href="(.*?)"')
            inline_url = "https://wx.jdcloud.com" + re.findall(p_url, href[0].strip())[0]
            #print('inline_url = ', inline_url)
            yield scrapy.Request(url=inline_url, callback=self.inline_parse, headers=self.headers, meta={'item': item})

    def inline_parse(self, response):
        #获取上个界面的item
        item = response.meta['item']

        #爬取页面数据
        entity = response.xpath('//*[@id="app"]')

        data_format = response.xpath('//*[@id="intro"]/ul/li[2]/span[1]').extract()
        file_type = response.xpath('//*[@id="intro"]/ul/li[1]/span[2]').extract()
        size = response.xpath('//*[@id="intro"]/ul/li[1]/span[1]').extract()
        time = response.xpath('//*[@id="intro"]/ul/li[2]/span[2]').extract()
        tag = entity.xpath('section/div[1]/div[1]/div/div[2]/ul/li[2]/span[2]/a/text()').extract()

        p = re.compile(r'[(](.*?)[)]', re.S)
        p_not_api = re.compile(r'</span>(.*)</span>', re.S)

        if 'API' in item['type']:
            trade = response.xpath('//*[@id="detailTab6"]/a/span/text()').extract()
            item['trade'] = trade[0].strip()
            item['tag'] = tag[0].strip()
        else:
            trade = response.xpath('//*[@id="conBox"]/nav/ul/li[3]/text()').extract()
            s = re.findall(p, trade[0].strip())
            item['trade'] = s[0].strip()

            item['data_format'] = re.findall(p_not_api, data_format[0].strip())[0].strip()
            item['file_type'] = re.findall(p_not_api, file_type[0].strip())[0].strip()
            item['size'] = re.findall(p_not_api, size[0].strip())[0].strip()
            item['time'] = re.findall(p_not_api, time[0].strip())[0].strip()
            item['tag'] = tag[0].strip()
        return item
#scrapy crawl scrapyJDWX -o test2.csv