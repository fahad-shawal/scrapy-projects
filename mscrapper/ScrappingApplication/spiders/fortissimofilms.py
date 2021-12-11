from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from ScrappingApplication.utils import clean


class FortissimoFilmsParseSpider(CrawlSpider):
    name = 'fortissimofilms-parse'

    def parse(self, response, **kwargs):
        movie = {
            'title': clean(response.css('.row h1 ::text').extract(), True),
            'project_notes': clean(response.css('.filmdetailSynopsis ::text').extract(), True),
            'release_date': self.get_detail(response, "Year"),
            'duration': self.get_detail(response, "Duration"),
            'genres': self.get_detail(response, "Genre"),
            'directors': self.get_detail(response, "Director"),
            'producers': self.get_detail(response, "Producers"),
            'cast': self.get_detail(response, "Cast")
        }

        add_credit_css = '.filmdetailHeading:contains("Additional Credits") + div ::text'
        movie['additional_credits'] = ': '.join(clean(response.css(add_credit_css).extract()))

        return movie

    def get_detail(self, response, heading):
        return clean(response.css(f'.filmdetailHeading:contains("{heading}") + p ::text').extract(), True)


class FortissimoFilmsCrawlSpider(CrawlSpider):
    name = 'fortissimofilms-crawl'
    allowed_domains = ['fortissimofilms.com']
    start_urls = ['https://fortissimofilms.com/films']

    movie_parser = FortissimoFilmsParseSpider()

    listings_css = ['.row a']

    rules = (
        Rule(LinkExtractor(restrict_css=listings_css), callback=movie_parser.parse),
    )
