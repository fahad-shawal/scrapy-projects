import re

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Spider, Rule, Request


def clean(lst_or_str):
    if not lst_or_str:
        return None
    
    if isinstance(lst_or_str, list):
        return [x.strip() for x in lst_or_str if x.strip()]
    return lst_or_str.strip()


class JeChercheUnAssureurParseSpider(CrawlSpider):
    name = 'assureur-crawler'
    allowed_domains = ['jechercheunassureur.com']
    start_urls = ['http://jechercheunassureur.com/']

    def parse(self, response):
        for item_s in response.css('.info-societe'):
            insurance = {}

            insurance['name'] = self.name(item_s)
            insurance['email'] = self.email(item_s)
            insurance['contact'] = self.contact_info(item_s)
            insurance['address'] = self.address(item_s)
            insurance['speciality'] = self.speciality(item_s)
            insurance['Web_site'] = self.web(item_s)

            yield insurance

    def name(self, item):
        return clean(item.css('h3 ::text').get())

    def address(self, item):
        return clean(item.css('#adresse::text').get())

    def contact_info(self, item):
        return clean(item.css('[title="No. téléphone"] ::text').get())

    def email(self, item):
        return clean(item.css('[title="E-mail adresse"] ::text').get())

    def speciality(self, item):
        return clean(item.css('[title="Spécialités"] ::text').get())

    def web(self, item):
        return clean(item.css('[title="Site web"] ::text').get())


class JeChercheUnAssureurCrawlSpider(CrawlSpider):
    name = 'assureur-crawler'
    allowed_domains = ['jechercheunassureur.com']
    start_urls = ['http://jechercheunassureur.com/']

    parse_insurance = JeChercheUnAssureurParseSpider()

    insurance_css = [
        '#les_departement'
    ]

    rules = (
        Rule(LinkExtractor(restrict_css=insurance_css), callback=parse_insurance.parse),
    )