# -*- coding: utf-8 -*-
import scrapy


class BbcSpider(scrapy.Spider):
    name = 'bbc'
    allowed_domains = ['bbc.com']
    start_urls = ['http://bbc.com/urdu']

    def parse(self, response):
        links = self.extract_navigation_link(response)
        for link in links:
            req = response.follow(link, self.extract_news_links)
            yield req

    def extract_navigation_link(self, response):
        css = '.navigation-wide-list__link::attr(href)'
        return response.css(css).extract()

    def extract_news_links(self, response):
        css = '.title-link::attr(href)'
        links = response.css(css).extract()
        for link in links:
            req = response.follow(link, self.extract_news_details)
            yield req

    def extract_news_details(self, response):
        item = {}

        item['header'] = self.extract_news_header(response)
        item['author'] = self.extract_author_name(response)
        item['news_intro'] = self.extract_news_intro(response)
        item['content'] = self.extract_news_content(response)

        return item

    def extract_news_header(self, response):
        css = '.story-body__h1::text'
        return response.css(css).extract_first()

    def extract_author_name(self, response):
        css = '.byline__name::text'
        return response.css(css).extract_first()

    def extract_news_intro(self, response):
        css = '.story-body__introduction::text'
        return response.css(css).extract_first()

    def extract_news_content(self, response):
        css = '.story-body__inner p::text'
        return response.css(css).extract()
