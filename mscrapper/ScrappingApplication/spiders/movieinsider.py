from ScrappingApplication.utils import clean
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule, Spider


class MovieInsiderParseSpider(Spider):
    name = 'movieinsider-parse'

    def parse(self, response, **kwargs):
        return {
            'url': response.url,
            'id': self.extract_id(response),
            'title': self.extract_title(response),
            'aka_title': self.extract_aka_title(response),
            'directors': self.extract_directors(response),
            'writers': self.extract_writers(response),
            'producers': self.extract_producers(response),
            'cast': self.extract_cast(response),
            'studios': self.extract_studios(response),
            'release_date': self.extract_release_date(response),
            'genres': self.extract_genres(response),
            'plot': self.extract_plot(response),
            'production_companies': self.extract_production_companies(response),
        }

    def extract_id(self, response):
        return response.url.split('/')[-2]

    def extract_title(self, response):
        title_css = '.subpage-head .container h1::text'
        return clean(response.css(title_css).extract())[0]

    def extract_aka_title(self, response):
        aka_title_css = '.sidebar-subnav .list-inline ::text'
        aka_title = clean(response.css(aka_title_css).extract())
        return aka_title[0] if aka_title else None

    def extract_directors(self, response):
        direcotors_css = '.movie-facts [itemprop="director"] ::text'
        return clean(response.css(direcotors_css).extract())

    def extract_writers(self, response):
        writers_css = '.movie-facts .credits ::text'
        return clean(response.css(writers_css).extract())

    def extract_producers(self, response):
        producers_x = '//div[contains(@class, "movie-facts")]//h3[contains(text(),Producers)]/parent::div/text()'
        return clean(response.xpath(producers_x).extract())

    def extract_production_companies(self, response):
        production_x = '//h3[contains(text(), "Production")]/parent::div//p//a/text()'
        return clean(response.xpath(production_x).extract())

    def extract_cast(self, response):
        cast_css = '.cast [itemprop=actor] ::text'
        return clean(response.css(cast_css).extract())

    def extract_studios(self, response):
        studios_x = '//h3[text()="Companies "]/parent::div//p//text()'
        return clean(response.xpath(studios_x).extract())

    def extract_release_date(self, response):
        release_date_x = '//p[text()=" Release Date:"]/parent::div//strong//a//text()'
        release_date = clean(response.xpath(release_date_x).extract())
        return release_date[0] if release_date else None

    def extract_genres(self, response):
        genre_css = '.info-list [itemprop="genre"] ::text'
        return clean(response.css(genre_css).extract())

    def extract_plot(self, response):
        plot_css = '[itemprop="description"] ::text'
        return clean(response.css(plot_css).extract())


class MovieInsiderCrawlSpider(CrawlSpider):
    name = 'movieinsider-crawl'
    parse_spider = MovieInsiderParseSpider()

    allowed_domains = [
        'www.movieinsider.com'
    ]

    start_urls = [
        'https://www.movieinsider.com/production-status/pre-production'
    ]

    rules = [
        Rule(LinkExtractor(restrict_css='.pagination'), ),
        Rule(LinkExtractor(restrict_css='.listing.movie-detail .media-heading'), callback='parse_item'),
    ]

    def parse_item(self, response):
        return self.parse_spider.parse(response)
