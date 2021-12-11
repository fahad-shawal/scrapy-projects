import re
import json

from six.moves.urllib.parse import urlencode
from scrapy import FormRequest, Request, Spider, Selector
from w3lib.url import add_or_replace_parameter, add_or_replace_parameters
from scrapy.item import Item, Field

seen_ids = set()


def clean(lst_or_str):
    if not lst_or_str:
        return ''

    if not isinstance(lst_or_str, str) and getattr(lst_or_str, '__iter__', False):
        return [x for x in (y.strip() for y in lst_or_str if y is not None) if x]
    return lst_or_str.strip()


class Part(Item):
    part_id = Field()
    url = Field()
    name = Field()
    brand = Field()
    prices = Field()
    vehicles = Field()
    oe_number = Field()
    image_urls = Field()
    description = Field()
    sub_assembly = Field()
    specifications = Field()
    parent_assembly = Field()
    filters = Field()


class FitinspiderParseSpider(Spider):
    name = 'fitinpart-parse'

    def parse(self, response):
        part = self.new_part(re.findall('product_id=(.*)', response.url)[0])

        if not part:
            return

        part['url'] = response.url
        part['name'] = self.product_name(response)
        part['brand'] = self.brand(response)
        part['prices'] = self.quotes_info(response)
        part['vehicles'] = self.vehicles_info(response)
        part['oe_number'] = self.oe_number_info(response)
        part['image_urls'] = self.image_urls(response)
        part['description'] = self.description(response)
        part['sub_assembly'] = self.sub_assembly_info(response)
        part['specifications'] = self.specifications_info(response)
        part['parent_assembly'] = self.parent_assembly_info(response)
        part['filters'] = self.filters(response)

        return part

    def new_part(self, product_id):
        if product_id in seen_ids:
            return None

        seen_ids.add(product_id)
        return Part(part_id=product_id)

    def product_name(self, response):
        css = '#right_title h1::text'
        return clean(response.css(css).extract_first())

    def brand(self, response):
        css = '[itemprop="brand"]::attr(content)'
        return clean(response.css(css).extract_first())

    def quotes_info(self, response):
        quotes = []
        for raw_quote in response.css('.ProductQuotes tr')[1:]:
            quote = {
                'vendor': clean(raw_quote.css('.vendor_col ::text').extract_first()),
                'price': clean(raw_quote.css('.price_col ::text').extract_first()),
                'days': clean(raw_quote.css('td:nth-child(2) ::text').extract_first()),
                'qty': clean(raw_quote.css('td:nth-child(3) ::text').extract_first())
            }
            quotes.append(quote)

        return quotes

    def vehicles_info(self, response):
        vehicles = []

        for raw_vehicle in response.css('#tab-specification .panel')[1:]:
            vehicle = {
                'brand': clean(raw_vehicle.css('.panel-title .row div:nth-child(1)::text').extract_first()),
                'model': clean(raw_vehicle.css('.panel-title .row div:nth-child(3)::text').extract_first())
            }
            for raw_info in raw_vehicle.css('.panel-body tr')[1:]:
                info = vehicle.copy()

                info['placement'] = clean(raw_info.css('[data-field="placement"] ::text').extract_first())
                info['production'] = clean(raw_info.css('[data-field="production"] ::text').extract_first())
                info['application'] = clean(raw_info.css('[data-field="application"] ::text').extract_first())
                info['body'] = clean(raw_info.css('[data-field="body"] ::text').extract_first())
                info['eng'] = clean(raw_info.css('[data-field="eng"] ::text').extract_first())
                info['note'] = clean(raw_info.css('[data-field="note"] ::text').extract_first())

                vehicles.append(info)

        return vehicles

    def oe_number_info(self, response):
        oe_numbers = []
        for raw_num in response.css('table:contains("OE Numbers") tbody tr')[1:]:
            oe_num = {
                'owner': clean(raw_num.css('td:nth-child(1) ::text').extract_first()),
                'part_number': clean(raw_num.css('td:nth-child(2) ::text').extract_first())
            }
            oe_numbers.append(oe_num)

        return oe_numbers

    def image_urls(self, response):
        return ' | '.join(clean(response.css('.thumbnail img::attr(src)').extract()))

    def description(self, response):
        return '\n'.join(clean(response.css('#tab-description ::text').extract()))

    def sub_assembly_info(self, response):
        sub_assembly = []
        for spec in response.css('h3:contains("Sub Assembly:") + div tr')[1:]:
            info = {
                'brand': clean(spec.css('td:nth-child(1) ::text').extract_first()),
                'part': clean(spec.css('td:nth-child(2) ::text').extract_first()),
                'type': clean(spec.css('td:nth-child(3) ::text').extract_first())
            }
            sub_assembly.append(info)

        return sub_assembly

    def specifications_info(self, response):
        specifaction = {}
        fields = ['Location', 'Height', 'Length-1', 'Pcs In Set', 'Thickness-1', 'Width-1', 'O-Ring gasket',
                  'Structure Material', 'Thread', 'type', 'Valves', 'Out']
        for field in fields:
            raw_val = response.css(f'h3:contains("Specifications:") + div td:contains("{field}") + td')
            specifaction[field.lower()] = clean(raw_val.css(' ::text').extract_first()) if raw_val else ''

        return specifaction

    def parent_assembly_info(self, response):
        parent_assembly = []
        for spec in response.css('h3:contains("Parent Assembly:") + div tr')[1:]:
            info = {
                'brand': clean(spec.css('td:nth-child(1) ::text').extract_first()),
                'part': clean(spec.css('td:nth-child(2) ::text').extract_first()),
                'type': clean(spec.css('td:nth-child(3) ::text').extract_first())
            }
            parent_assembly.append(info)

        return parent_assembly

    def filters(self, response):
        filters = {}
        keys = ['brand', 'model', 'years', 'body', 'engine', 'engin_no']
        for key in keys:
            filters[key] = response.meta[key]

        return filters


class FitinspiderCrawlSpider(Spider):
    name = 'fitinpart-crawl'
    allowed_domains = ['fitinpart.sg']
    start_urls = ['https://fitinpart.sg']

    item_parser = FitinspiderParseSpider()

    brand_request_url = 'https://www.fitinpart.sg/index.php?route=module/appsearch/getBrand'
    model_request_url = 'https://www.fitinpart.sg/index.php?route=module/appsearch/getModel'
    year_request_url = 'https://www.fitinpart.sg/index.php?route=module/appsearch/getYears'
    body_request_url = 'https://www.fitinpart.sg/index.php?route=module/appsearch/getBody'
    engine_request_url = 'https://www.fitinpart.sg/index.php?route=module/appsearch/getEngine'
    engine_no_request_url = 'https://www.fitinpart.sg/index.php?route=module/appsearch/getEngineNo'
    parts_request_url = 'https://www.fitinpart.sg/index.php?route=product/category/appSearch&' \
                        'b=0&c=&m=0&e_v=0&e_n=0&y=0&b_v=0&veh=1&sg_only=&cat=0&p_type=&show=1&init_search=1'

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    def start_requests(self):
        form_data = {
            'veh_type': '1'
        }
        yield FormRequest(url=self.brand_request_url, method="POST", headers=self.headers, formdata=form_data)
        

        # yield req
        # form_data = {
        #         'model[]': '112',
        #         'years': '1998',
        #         'body': '0',
        #         'engine': '0',
        #         'engineno': '0',
        #         'car_no': ''
        # }
        
        # req = FormRequest(url=self.body_request_url, method="POST", headers=self.headers, callback=self.parse, formdata=form_data)
        # #req.headers[b'Content-Type'] = b'application/x-www-form-urlencoded; charset=UTF-8'
        # yield req

    def parse(self, response):
        selector = Selector(text=response.text)
        meta = response.meta.copy()

        for raw_brand in selector.css('option'):
            meta = {
                'brand': raw_brand.css('::text').extract_first(),
                'brand_val': raw_brand.css('::attr(value)').extract_first().replace('\\"', '')
            }
            form_data = {
                'brand': raw_brand.css('::attr(value)').extract_first().replace('\\"', ''),
                'class': '0',
                'veh_type': '1'
            }
            yield FormRequest(url=self.model_request_url, method="POST", headers=self.headers, 
                            meta=meta.copy(),callback=self.parse_models, formdata=form_data)

    def parse_models(self, response):
        selector = Selector(text=response.text)
        meta = response.meta.copy()

        for raw_model in selector.css('option'):
            meta['model'] = raw_model.css('::text').extract_first()
            meta['model_val'] = raw_model.css('::attr(value)').extract_first().replace('\\"', '')

            form_data = {
                'model[]': raw_model.css('::attr(value)').extract_first().replace('\\"', ''),
            }

            yield FormRequest(url=self.year_request_url, method="POST",
                              headers=self.headers, meta=meta.copy(),
                              callback=self.parse_years, formdata=form_data)

    def parse_years(self, response):
        selector = Selector(text=response.text)
        meta = response.meta.copy()

        for raw_body in selector.css('option'):
            meta['years'] = raw_body.css('::attr(value)').extract_first().replace('\\"', '')

            form_data = {
                'model[]': meta['model_val'],
                'years': raw_body.css('::attr(value)').extract_first().replace('\\"', ''),
                'body': '-1',
                'engine': '-1',
                'engineno': '-1'
            }

            yield FormRequest(url=self.body_request_url, method="POST",
                              headers=self.headers, meta=meta.copy(),
                              callback=self.parse_body, formdata=form_data)

    def parse_body(self, response):
        selector = Selector(text=response.text)
        meta = response.meta.copy()

        for raw_body in selector.css('option'):
            meta['body'] = raw_body.css('::attr(value)').extract_first().replace('\\"', '')

            form_data = {
                'model[]': meta['model_val'],
                'years': meta['years'],
                'body': raw_body.css('::attr(value)').extract_first().replace('\\"', ''),
                'engine': '-1',
                'engineno': '-1'
            }
            yield FormRequest(url=self.engine_request_url, method="POST",
                              headers=self.headers, meta=meta.copy(),
                              callback=self.parse_engine, formdata=form_data)

    def parse_engine(self, response):
        selector = Selector(text=response.text)
        meta = response.meta.copy()

        for raw_body in selector.css('option'):
            meta['engine'] = raw_body.css('::attr(value)').extract_first().replace('\\"', '')

            form_data = {
                'model[]': meta['model_val'],
                'years': meta['years'],
                'body': meta['body'],
                'engine': raw_body.css('::attr(value)').extract_first().replace('\\"', ''),
                'engineno': '-1'
            }
            yield FormRequest(url=self.engine_no_request_url, method="POST", headers=self.headers,
                              meta=meta.copy(), callback=self.parse_engine_no, formdata=form_data)

    def parse_engine_no(self, response):
        selector = Selector(text=response.text)
        meta = response.meta.copy()

        for raw_body in selector.css('option'):
            meta['engin_no'] = raw_body.css('::attr(value)').extract_first().replace('\\"', '')

            params = {
                'b': meta['brand_val'],
                'm': meta['model_val'],
                'y': meta['years'],
                'b_v': meta['body'],
                'e_v': meta['engine'],
                'e_n': raw_body.css('::attr(value)').extract_first().replace('\\"', '')
            }

            url = add_or_replace_parameters(self.parts_request_url, params)
            yield Request(url, meta=meta.copy(), callback=self.parse_pagination)

    def parse_pagination(self, response):
        yield from self.item_request(response)

        url = add_or_replace_parameter(self.parts_request_url, 'limit', '1000')
        yield Request(url, meta=response.meta.copy(), callback=self.item_request)

    def item_request(self, response):
        return [Request(url, callback=self.item_parser.parse, meta=response.meta.copy())
                for url in response.css('.active .brand_layer ::attr(href)').extract()]
