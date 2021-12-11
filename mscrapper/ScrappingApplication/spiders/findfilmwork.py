import re
from datetime import datetime

from dateutil.relativedelta import relativedelta

from scrapy import FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Spider, Request, Rule
from scrapy.link import Link

from ..items import Movie


def _sanitize(input_val):
    pattern_re = '\s+'
    repl_re = ' '
    return re.sub(pattern_re, repl_re, input_val, flags=0).strip()


def clean(lst_or_str):
    if not isinstance(lst_or_str, str) and getattr(lst_or_str, '__iter__', False):  # if iterable and not a string like
        return [x for x in (_sanitize(y) for y in lst_or_str if y is not None) if x]
    return _sanitize(lst_or_str)


class FindfilmworkParseSpider(Spider):
    name = 'findfilmwork-parse'

    def parse(self, response):
        movie = Movie()

        movie['url'] = response.url
        movie['id'] = self.id(response)
        movie['title'] = self.title(response)
        movie['aka_title'] = None
        movie['project_type'] = self.project_type(response)
        movie['project_issue_date'] = self.project_issue_date(response)
        movie['project_update'] = self.update(response)
        movie['locations'] = self.location(response)
        movie['photography_start_date'] = None
        movie['writers'] = self.writers(response)
        movie['directors'] = self.directors(response)
        movie['cast'] = self.cast(response)
        movie['producers'] = self.producers(response)
        movie['production_companies'] = self.production_companies(response)
        movie['studios'] = self.studio(response)
        movie['plot'] = self.plot(response)
        movie['genres'] = self.gener(response)
        movie['project_notes'] = None
        movie['release_date'] = None
        movie['start_wrap_schedule'] = self.start_wrap_schedule(response)

        return movie

    def id(self, response):
        return clean(response.css('[name="projectid"] ::attr(value)').extract())[0]

    def title(self, response):
        return clean(response.css('.contentBox h1 ::text').get())

    def project_type(self, response):
        return clean(response.css('.blurbContainer strong ::text').get())

    def project_issue_date(self, response):
        raw_content = ' '.join(clean(response.css('.blurbContainer ::text').extract()))
        raw_date = re.findall('Added\s*:\s*(.*)\s*Last', raw_content)
        return raw_date[0].strip() if raw_date else None

    def update(self, response):
        raw_content = ' '.join(clean(response.css('.blurbContainer ::text').extract()))
        raw_update = re.findall('Status\s*:\s*(.*)\s*Added', raw_content)
        return raw_update[0].strip() if raw_update else None

    def location(self, response):
        raw_content = ' '.join(clean(response.css('.panel:contains("Locations") ::text').extract()))
        raw_loc = re.findall('Locations\s*(.*)', raw_content)
        return raw_loc[0].strip() if raw_loc else None

    def writers(self, response):
        css = '.panel .stageListings tr:contains("writer") td ::text'
        raw_writers = clean(response.css(css).extract())
        return [writer for writer in raw_writers if not 'writer' in writer.lower()]

    def directors(self, response):
        css = '.panel .stageListings tr:contains("Director") td ::text'
        raw_directors = clean(response.css(css).extract())
        return [director for director in raw_directors if not 'director' in director.lower()]

    def cast(self, response):
        css = '.panel .stageListings tr:contains("Actor") td ::text'
        raw_actor = clean(response.css(css).extract())
        return [actor for actor in raw_actor if not 'actor' in actor.lower()]

    def producers(self, response):
        css = '.panel .stageListings tr:contains("Producer") td ::text'
        raw_producer = clean(response.css(css).extract())
        return [prod for prod in raw_producer if not 'producer' in prod.lower()]

    def production_companies(self, response):
        prod_companies = []
        for raw_comp in response.css('table:contains("Company") tr div'):
            raw_name = raw_comp.css('strong[style] ::text').extract_first()
            if not raw_name:
                continue
            raw_text = ' '.join(raw_comp.css(' ::text').extract())
            raw_phone = re.findall('Phone\s*1\s*:\s*([0-9-()\s]*)', raw_text)
            raw_email = re.findall('Email\s*:\s*(.*)', raw_text)
            raw_address = re.findall(f'{raw_name}\s*(.*?)(?:Phone|Email|Fax)', raw_text)
            company = {
                'name': raw_name,
                'phone': clean(raw_phone[0]) if raw_phone else '',
                'email': clean(raw_email[0]) if raw_email else '',
                'address': clean(raw_address[0]) if raw_address else ''
            }

            prod_companies.append(company)

        return prod_companies

    def studio(self, response):
        raw_content = ' '.join(clean(response.css('#main_info ::text').extract()))
        raw_studio = re.findall('Network\s*(.*)', raw_content)
        return raw_studio[0].strip() if raw_studio else None

    def plot(self, response):
        return clean(response.css('p.studioBlurb ::text').extract())

    def gener(self, response):
        raw_content = ' '.join(clean(response.css('#main_info ::text').extract()))
        raw_gene = re.findall('Genre\s*(.*)Network', raw_content)
        return raw_gene[0].strip() if raw_gene else None

    def start_wrap_schedule(self, response):
        raw_content = ' '.join(clean(response.css('#main_info ::text').extract()))
        raw_gene = re.findall('Start\s*(.*)Genre', raw_content)
        return raw_gene[0].strip() if raw_gene else None


class ProductLE():
    def _repalce(self, date):
        replace_map = [
            'st,', 'nd,', 'rd,', 'th,'
        ]
        for to_repalce in replace_map:
            if to_repalce in date:
                return date.replace(to_repalce, ',')

    def extract_links(self, response):
        raw_movies = response.css('#browseTable tr')[1:]
        if not raw_movies:
            return []

        curr_year = datetime.now().year
        years = response.meta['years']

        movie_links = []
        for movie_s in raw_movies:
            raw_date = self._repalce(movie_s.css('.pb-col5::text').get())
            movie_init_year = datetime.strptime(raw_date, '%b %d, %Y').year
            
            if curr_year - movie_init_year <= years:
                raw_link = movie_s.css('.browse-project-link::attr(href)').get()
                movie_links.append(Link(response.urljoin(raw_link)))

        return movie_links
            

class FindfilmworkCrawlSpider(CrawlSpider):
    name = 'findfilmwork-crawl'

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'COOKIES_ENABLED': True,

    }

    allowed_domains = ['findfilmwork.com']
    start_urls = ['https://www.findfilmwork.com/login-2.php']

    movie_parser = FindfilmworkParseSpider()

    email = 'danielkcarter1@gmail.com'
    password = 'Hj56h6&^4jye'

    listings_css = [
        '.resultsNav'
    ]


    def parse(self, response, **kwargs):
        return super()._parse(response)

    rules = [
        Rule(LinkExtractor(restrict_css=listings_css), process_request='set_meta', callback='parse'),
        Rule(ProductLE(), callback=movie_parser.parse, follow=True)
    ]

    def set_meta(self, resquest, spider):
        meta = {
            'years': int(self.years)
        }
        resquest.meta.update(meta)
        return resquest

    def start_requests(self):
        meta = {
            'years': int(self.years)
        }
        form_Data = {
            'userlogin': self.email,
            'userpassword': self.password,
            'submit0': 'Login',
            '_qf__login': '',
            'returnto': '%2Fbrowse.php%3Fp%3D1'
        }
        return [FormRequest(self.start_urls[0], formdata=form_Data, meta=meta.copy(), callback=self.parse)]
