from scrapy.http import FormRequest
from scrapy.spiders import Spider, Request

from ..settings import citys_list

def clean(lst_or_str):
    if not lst_or_str:
        return ''
    if not isinstance(lst_or_str, str) and getattr(lst_or_str, '__iter__', False):  # if iterable and not a string like
        return [x.strip() for x in lst_or_str if x is not None]
    return lst_or_str.strip()

class BrokerageCrawlSpider(Spider):
    name = 'reco_brokerage-crawl'
    allowed_domains = ['reco.on.ca']
    start_urls = ['https://www.reco.on.ca/RegistrantSearch/RegistrantSearch/Salesperson']

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 60000,
        'DOWNLOAD_MAXSIZE': 12406585060,
        'DOWNLOAD_WARNSIZE': 0,
        'FEED_URI': 'brokage.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_FIELDS': [
                            'Brokerage Name',
                            'Legal Name',
                            'Status',
                            'EXPIRY',
                            'Branch Manager',
                            'Broker of Record',
                            'Address',
                            'City',
                            'Postal',
                            'Province',
                            'Email',
                            'Phone',
                            'Fax',
                        ],
    }

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '^\\^',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'https://www.reco.on.ca',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.reco.on.ca/RegistrantSearch',
        'Accept-Language': 'en-US,en;q=0.9',
    }


    def start_requests(self):
        for city in citys_list:
            form_data = {
                'category': 'Brokerage/Branch',
                'CategoryCity': city,
                'action': 'searchCategory'
            }

            yield FormRequest(self.start_urls[0], headers=self.headers, formdata=form_data)

    def parse(self, response):
        
        for item in response.css('.card'):
            brokage = {}

            brokage['Brokerage Name'] = self.brokage_name(item)
            brokage['Legal Name'] = self.legal_name(item)
            brokage['Status'] = self.status(item)
            brokage['EXPIRY'] = self.expiry(item)
            brokage['Branch Manager'] = self.branch_manager(item)
            brokage['Broker of Record'] = self.broker_of_record(item)
            brokage['Email'] = self.email(item)
            brokage['Phone'] = self.phone(item)
            brokage['Fax'] = self.fax(item)
            
            brokage.update(self.address(item))
            yield brokage
    
    def brokage_name(self, response):
        return clean(response.css('h4::text').extract_first()) or ''

    def legal_name(self, response):
        raw_data = clean(response.css('p:contains("Legal")::text').extract())
        return raw_data[-1] if raw_data else 'N\A'

    def status(self, response):
        raw_data = clean(response.css('p:contains("Registration :")::text').extract())
        return raw_data[-1] if raw_data else 'N\A'

    def expiry(self, response):
        raw_data = clean(response.css('p:contains("Registration Expiry ")::text').extract())
        return raw_data[-1] if raw_data else 'N\A'

    def branch_manager(self, response):
        raw_data = clean(response.css('p:contains("Manager")::text').extract())
        return raw_data[-1] if raw_data else 'N\A'
    
    def broker_of_record(self, response):
        raw_data = clean(response.css('p:contains("Broker of Record")::text').extract())
        return raw_data[-1] if raw_data else 'N\A'
    
    def address(self, response):
        city = clean(response.css('h5::text').extract()[0].split(':')[-1])
        raw_address = clean(response.css('p:contains("Address")::text').extract())
        
        if not raw_address: 
            return {}

        try:
            addr1, addr2 = raw_address[-1].split(f'{city},')
        except:
            try:
                addr1, _, addr2 = raw_address[-1].split(f'{city},')
            except:
                return {
                'Address': 'N\A',
                'City': city,
                'Postal': 'N\A',
                'Province': 'Ontario'
            }

        addr2 = addr2.replace(',', '').split()

        if len(addr2) == 2 and addr2[0].lower() == 'on':
            addr2 = addr2[1:]
        else:
            if addr2 and len(addr2[0]) != 3:
                addr2 = addr2[1:]

            if addr2 and len(addr2[-1]) != 3:
                addr2 = addr2[:-1]

        return {
            'Address': clean(addr1),
            'City': city,
            'Postal': ' '.join(addr2),
            'Province': 'Ontario'
        }
    
    def email(self, response):
        raw_data = clean(response.css('p:contains("Email")::text').extract())
        return raw_data[-1] if raw_data else 'N\A'

    def phone(self, response):
        raw_data = clean(response.css('p:contains("Phone")::text').extract())
        return raw_data[-1] if raw_data else 'N\A'
    
    def fax(self, response):
        raw_data = clean(response.css('p:contains("Fax")::text').extract())
        return raw_data[-1] if raw_data else 'N\A'
