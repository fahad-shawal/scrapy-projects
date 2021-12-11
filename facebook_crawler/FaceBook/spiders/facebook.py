import json
import re
import logging

from scrapy.spiders import Spider, CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


def _sanitize(input_val):
    pattern_re = '\s+'
    repl_re = ' '
    return re.sub(pattern_re, repl_re, input_val, flags=0).strip()


def clean(lst_or_str):
    if not isinstance(lst_or_str, str) and getattr(lst_or_str, '__iter__', False):  # if iterable and not a string like
        return [x for x in (_sanitize(y) for y in lst_or_str if y is not None) if x]
    return _sanitize(lst_or_str)


logger = logging.getLogger('Facebook_Scrapper')


class FacebookParseSpider(Spider):
    name = 'facebook-parse'

    def parse(self, response):
        if 'login' in response.url:
            logger.warning("Droping Job due to required login :: " + response.url)
            return

        parseV2 = False
        if not response.css('[type="application/ld+json"]'):
            parseV2 = True
        else:
            raw_product = self.raw_product(response)

        return {
            'url': response.url,
            'name': self.name(raw_product) if not parseV2 else self.nameV2(response),
            'location': self.location(raw_product) if not parseV2 else self.locationV2(response),
            'datePosted': self.date_posted(raw_product) if not parseV2 else 'N\A',
            'description': self.description(raw_product) if not parseV2 else 'N\A',
            'qualification': self.qualification(raw_product)if not parseV2 else self.qualificationV2(response),
            'responsibilities': self.responsibilities(raw_product)if not parseV2 else self.responsibilitiesV2(response)
        }

    def raw_product(self, response):
        css = '[type="application/ld+json"]::text'
        return json.loads(clean(response.css(css).extract_first()))

    def name(self, raw_product):
        return clean(raw_product['title'])
    
    def nameV2(self, response):
        return clean(response.css('[property="og:title"]::attr(content)').extract_first())

    def location(self, raw_product):
        return clean(raw_product['jobLocation'].get('name', 'N/A'))
    
    def locationV2(self, response):
        css = 'i :contains("Location pin icon") + div ::text'
        return ''.join(clean(response.css(css).extract())[:3] or [])

    def date_posted(self, raw_product):
        return clean(raw_product.get('datePosted', 'N/A'))

    def description(self, raw_product):
        return clean(raw_product.get('description', 'N/A'))

    def qualification(self, raw_product):
        return clean(raw_product.get('qualifications', 'N/A'))

    def qualificationV2(self, response):
        css = 'div:contains(Qualifications) + div ul ::text'
        return clean(response.css(css).extract())

    def responsibilities(self, raw_product):
        return clean(raw_product.get('responsibilities', 'N/A'))
    
    def responsibilitiesV2(self, response):
        css = 'div:contains(Responsibilities) + div ul ::text'
        return clean(response.css(css).extract())


class FacebookCrawlSpider(CrawlSpider):
    name = 'facebook-crawl'
    job_parser = FacebookParseSpider()

    allowed_domains = ['facebook.com']
    start_urls = ['https://www.facebook.com/careers/jobs/']

    listing_css = [
        'a[role="button"]'
    ]
    jobs_css = [
        '#search_result'
    ]

    rules = [
        Rule(LinkExtractor(restrict_css=listing_css)),
        Rule(LinkExtractor(restrict_css=jobs_css), callback=job_parser.parse)
    ]
