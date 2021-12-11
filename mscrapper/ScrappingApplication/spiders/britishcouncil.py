import re
from scrapy.spiders import CrawlSpider, Rule, Request, Spider
from scrapy.linkextractors import LinkExtractor

from ..items import Movie
from ..utils import clean


class BritishCouncilParseSpider(Spider):
    name = 'britishcouncil-parse'

    def parse(self, response):
        movie = Movie()

        movie['url'] = response.url
        movie['title'] = self.extract_title(response)
        movie['plot'] = self.extract_plot(response)
        movie['directors'] = self.extract_directors(response)
        movie['producers'] = self.extract_producers(response)
        movie['cast'] = self.extract_cast(response)
        movie['genres'] = self.extract_genres(response)
        movie['production_companies'] = self.extract_production_comapnies(response)
        movie['project_type'] = self.extract_project_type(response)
        movie['release_date'] = self.extract_project_issue_date(response)

        return movie

    def extract_title(self, response):
        return clean(response.css('.page-subtitle h1 ::text').extract_first())

    def extract_plot(self, response):
        return clean(response.css('.standfirst ::text').extract_first())

    def extract_project_issue_date(self, response):
        year_xpath = '//dl[@class="details"]//dt[contains(text(),"Year")]/following-sibling::dd[1]/text()'
        return clean(response.xpath(year_xpath).extract_first())

    def extract_project_type(self, response):
        project_type_xpath = '//dl[@class="details"]//dt[contains(text(),"Type of film")]/following-sibling::' \
                             'dd[1]/text()'
        return clean(response.xpath(project_type_xpath).extract_first())

    def extract_directors(self, response):
        directors_xpath = '//dl[@class="details"]//dt[text()="Director" or text()="Director of Photography"]/' \
                          'following-sibling::dd[1]/text()'
        return clean(response.xpath(directors_xpath).extract())

    def extract_producers(self, response):
        producers_xpath = '//dl[@class="details"]//dt[text()="Producer" or text()="Co-Producer" or ' \
                          'text()="Executive Producer"]/following-sibling::dd[1]/text()'
        return clean(response.xpath(producers_xpath).extract())

    def extract_genres(self, response):
        return clean(response.css('.genres li::text').extract())

    def extract_production_comapnies(self, response):
        return clean(response.css('#production-info address ::text').extract_first())

    def extract_cast(self, response):
        cast_xpath = '//dl[@class="details"]//dt[text()="Principal Cast"]/following-sibling::dd[1]/text()'
        return clean(response.xpath(cast_xpath).extract_first()).split(',')


class BritishCouncilCrawlSpider(CrawlSpider):
    name = 'britishcouncil-crawl'
    allowed_domains = ['film-directory.britishcouncil.org']

    parse_spider = BritishCouncilParseSpider()

    start_urls = ['http://film-directory.britishcouncil.org/british-films-directory/in-production']

    rules = [
        Rule(LinkExtractor(restrict_css='.pager li'), ),
        Rule(LinkExtractor(restrict_css='#directory-list li'), callback='parse_item'),
    ]

    def parse_item(self, response):
        return self.parse_spider.parse(response)
