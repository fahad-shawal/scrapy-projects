from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule, Spider
from w3lib.url import url_query_cleaner

from ..utils import clean, next_request_or_item


class IMDBParseSpider(Spider):
    name = 'imdb-parse'

    def parse(self, response, **kwargs):
        item = {
            'url': response.url,
            'id': self.extract_id(response),
            'title': self.extract_title(response),
            'aka_title': self.extract_aka_title(response),
            'studios': self.extract_studios(response),
            'release_date': self.extract_release_date(response),
            'genres': self.extract_genres(response),
            'plot': self.extract_plot(response),
            'start_wrap_schedule': self.extract_start_wrap_schedule(response),
            'photography_start_date': self.extract_photography_start_date(response),
            'project_type': self.extract_project_type(response),
            'meta': {
                'requests_queue': (
                        self.cast_requests(response) +
                        self.production_companies_requests(response) +
                        self.location_requests(response)
                )
            }
        }

        return next_request_or_item(item)

    def parse_cast(self, response):
        item = response.meta['item']
        item['cast'] = self.extract_cast(response)
        item['writers'] = self.extract_writers(response)
        item['directors'] = self.extract_directors(response)
        item['producers'] = self.extract_producers(response)

        return next_request_or_item(item)

    def parse_production_companies(self, response):
        item = response.meta['item']
        item['production_companies'] = self.extract_production_companies(response)

        return next_request_or_item(item)

    def parse_locations(self, response):
        item = response.meta['item']
        item['locations'] = self.extract_locations(response)

        return next_request_or_item(item)

    def extract_id(self, response):
        id_css = '[property="pageId"]::attr(content)'
        return clean(response.css(id_css).extract())[0]

    def extract_title(self, response):
        title_css = '.title_wrapper h1::text'
        return clean(response.css(title_css).extract())[0]

    def extract_aka_title(self, response):
        return

    def extract_directors(self, response):
        direcotors_css = '[name="director"]+table .name ::text'
        return clean(response.css(direcotors_css).extract())

    def extract_writers(self, response):
        writers_css = '[name="writer"]+table .name ::text'
        return clean(response.css(writers_css).extract())

    def extract_producers(self, response):
        producers_css = '[name="producer"]+table .name ::text'
        return clean(response.css(producers_css).extract())

    def extract_production_companies(self, response):
        production_css = '[name="production"]+ul a::text'
        return clean(response.css(production_css).extract())

    def extract_cast(self, response):
        cast_css = '.cast_list .primary_photo ::attr(alt)'
        return clean(response.css(cast_css).extract())

    def extract_studios(self, response):
        return []

    def extract_release_date(self, response):
        release_date_css = '.txt-block:contains("Release Date:")::text'
        release_date = clean(response.css(release_date_css).extract())
        return release_date[0] if release_date else None

    def extract_genres(self, response):
        genre_css = 'div.see-more:contains("Genres:") a::text'
        return clean(response.css(genre_css).extract())

    def extract_plot(self, response):
        plot_css = '.plot_summary .summary_text ::text'
        plot = clean(response.css(plot_css).extract())
        return [plot[0]] if plot else []

    def extract_locations(self, response):
        locations_css = '#filming_locations [itemprop="url"]::text'
        return clean(response.css(locations_css).extract())

    def extract_start_wrap_schedule(self, response):
        return

    def extract_photography_start_date(self, response):
        return

    def extract_project_type(self, response):
        return

    def cast_requests(self, response):
        url = f'{url_query_cleaner(response.url)}fullcredits'
        return [Request(url=url, callback=self.parse_cast)]

    def location_requests(self, response):
        url = f'{url_query_cleaner(response.url)}locations'
        return [Request(url=url, callback=self.parse_locations)]

    def production_companies_requests(self, response):
        url = f'{url_query_cleaner(response.url)}companycredits'
        return [Request(url=url, callback=self.parse_production_companies)]


class IMDBCrawlSpider(CrawlSpider):
    name = 'imdb-crawl'
    parse_spider = IMDBParseSpider()

    allowed_domains = [
        'www.imdb.com'
    ]

    start_urls = [
        'https://www.imdb.com/movies-coming-soon/'
    ]

    rules = [
        Rule(LinkExtractor(restrict_css='.list_item tr h4', ), callback='parse_item'),
        Rule(LinkExtractor(restrict_css='.see-more a:contains("Next")'), callback='parse'),
    ]

    def parse(self, response, **kwargs):
        page = response.meta.get('page') or 0

        # 5 years limit
        if page > 60:
            return

        for request in self._requests_to_follow(response):
            request.meta['page'] = page + 1
            yield request

    def parse_item(self, response):
        return self.parse_spider.parse(response)
