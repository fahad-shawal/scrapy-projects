import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from random import randint
import time
import json
from time import sleep


class CompaniesSpider(CrawlSpider):
    name = 'companies'
    allowed_domains = ['www.biznesfinder.pl']
    start_urls = ['']
    meta = {'dont_redirect': True,'handle_httpstatus_list': [302]}


    #user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    user_agent = 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html'

    def start_requests(self):
        yield scrapy.Request(url='https://www.biznesfinder.pl/polska/biuro%20rachunkowe', dont_filter=True)

    rules = (
        #Rule(LinkExtractor(restrict_xpaths='//h2[@class="company-name pull-left pull-default-xxs"]/a'), callback='parse_item', follow=True),
        Rule(LinkExtractor(restrict_xpaths='//h2[@class="company-name pull-left pull-default-xxs"]/a'), callback='parse_item', follow=True, process_request='set_user_agent'),
        Rule(LinkExtractor(restrict_xpaths='//a[@title="następna"]'), process_request='set_user_agent')
    )

    def set_user_agent(self, request, spider):
        request.headers['User-Agent'] = self.user_agent
        return request

    def parse_item(self, response):

        
        json_file = response.xpath('//script[@type="application/ld+json"]/text()').get()
        data = json.loads(json_file)
        try: 
            phone = (data[0]["telephone"])
        except:
            phone =''

        city = str(response.xpath('//span[@class="company-address-city"]/text()').get())
        if city == 'None':
            city = ''

        street = str(response.xpath('//span[@class="company-address-street"]/text()').get())
        if street == 'None':
            street = ''

        building = str(response.xpath('//span[@class="company-address-building"]/text()').get())
        if building == 'None':
            building = ''


        postal_code = str(response.xpath('//span[@class="company-address-postal-code"]/text()').get())
        if postal_code == 'None':
            postal_code = ''

        adress = postal_code + ' ' + city + ', ' + street + ' ' + building

        yield {
            'title' : response.xpath('//h1[@class="company-name"]/text()').get(),
            'category' : response.xpath('//li[@class="company-category"]/a/text()').get(),
            'phone' :  phone,
            'email' : response.xpath('//*[@id="company-emails"]/li/a/@data-expanded').get(),
            'NIP' : response.xpath('//abbr[@title="Numer Identyfikacji Podatkowej"]/parent::dt/following-sibling::dd[1]/text()').get(),
            'REGON' : response.xpath('//abbr[@title="Rejestr Gospodarki Narodowej"]/parent::dt/following-sibling::dd[1]/text()').get(),
            'adress' : adress,
        }