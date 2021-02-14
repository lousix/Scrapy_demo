# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MyspiderItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()   #数据名称
    type = scrapy.Field()   #数据类型
    tag = scrapy.Field()    #数据标签
    size = scrapy.Field()   #数据大小
    time = scrapy.Field()   #时间范围
    file_type = scrapy.Field()    #数据数量
    data_format = scrapy.Field()    #数据格式
    trade = scrapy.Field()  #交易量
    browse = scrapy.Field() #浏览量
    evaluation = scrapy.Field() #评价
    price = scrapy.Field()  #价格
    pass
