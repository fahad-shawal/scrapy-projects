import json
import re

from scrapy import Spider, FormRequest
from scrapy.selector import Selector


class AolsSpiderSpider(Spider):
    name = 'aols-spider'
    allowed_domains = ['aols.org']
    start_urls = ['https://www.aols.org/find-a-surveyor']

    def parse(self, response):
        regex = 'var data\s*=\s*(\[.*\];)var clusterStyles'
        raw_data = response.css(' :contains("var data") ::text').re_first(regex)
        
        for item in json.loads(raw_data.split(';var clusterStyles')[0]):
            surveyor = {}
            raw_content = Selector(text=item['content'])

            surveyor['name'] = self.surveyor_name(item)
            surveyor['phone'] = self.surveyor_phone(raw_content)
            surveyor['city'] = self.surveyor_city(raw_content)
            surveyor['province'] = self.surveyor_province(raw_content)
            surveyor['country'] = self.surveyor_country(raw_content)

            surveyor.update(self.street_info(raw_content))

            surveyor['meta'] = {'request_queue': self.postal_code_request(surveyor['name'])}

            yield self.next_request_or_item(surveyor)

    def next_request_or_item(self, surveyor):
        if surveyor['meta']['request_queue']:
            req = surveyor['meta']['request_queue'].pop()
            req.meta.setdefault('surveyor', surveyor) 
            return req
        
        surveyor.pop('meta')
        return surveyor

    def surveyor_name(self, item):
        return item['name']
    
    def surveyor_phone(self, response):
        raw_phone = response.css('.phone ::text').extract_first()
        if not raw_phone:
            return ''
        return raw_phone.split(':')[-1].strip()

    def surveyor_city(self, response):
        raw_city = response.css('.city ::text').extract_first()
        if not raw_city:
            return ''
        return raw_city.strip()

    def surveyor_province(self, response):
        raw_province = response.css('.province ::text').extract_first()
        if not raw_province:
            return ''
        return raw_province.strip()
    
    def surveyor_country(self, response):
        raw_country = response.css('.country ::text').extract_first()
        if not raw_country:
            return ''
        return raw_country.strip()

    def street_info(self, response):
        street_info = {
            'unit_number': '',
            'street_name': '',
            'street_number': ''
        }

        raw_data = response.css('.street ::text').getall()
        
        if not raw_data:
            return street_info
        raw_data = ''.join(raw_data)

        if 'unit' in raw_data.lower():
            raw_data, street_unit = raw_data.split('Unit')
            street_info['unit_number'] = street_unit.strip()
        
        street_number = re.findall('\d+', raw_data)
        if street_number:
            street_info['street_number'] = street_number[0].strip()
            raw_data = raw_data.replace(street_info['street_number'], '')

        street_info['street_name'] = raw_data.strip()

        return street_info

    def parse_postal_code(self, response):
        surveyor = response.meta['surveyor']
        surveyor['postal_code'] = self.postal_code(response, surveyor['phone'])
        
        return self.next_request_or_item(surveyor)

    def postal_code(self, response, phone):
        for raw_item in response.css('.ctn.border-bottom'):
            raw_phone = raw_item.css('a:contains("Tel")::attr("href")').get()
            if not raw_phone:
                continue
                
            raw_phone = raw_phone.split(':')[-1].strip()
            if phone == raw_phone:
                return response.css('.postal::text').get().strip()
            
        return ''


    def postal_code_request(self, name):

        cookies = {
            'LangCode_': 'en-ca',
            '_ga': 'GA1.2.1519462933.1633054851',
            '_gid': 'GA1.2.1608041393.1636138097',
            'RequestID_': 'mrjrc0cny0xepnmdjoyiypk1637717884309640042XhW3K1eVgfEIjz3X5eLspgfHXQ1IhduL',
            '_a3_': 'c_95_0_w_1_1920_1080_1.0_0_:B2C453BB',
            '_gat_gtag_UA_44364514_1': '1',
        }

        headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cache-Control': 'no-cache',
            'X-Requested-With': 'XMLHttpRequest',
            'X-MicrosoftAjax': 'Delta=true',
            'sec-ch-ua-platform': '"Windows"',
            'Accept': '*/*',
            'Origin': 'https://www.aols.org',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.aols.org/find-a-surveyor',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        data = {
            's': 'c1$guC$c$r0$guC|c1$guC$c$r0$guC$c$bc$bc$txtSearch',
            's_HiddenField': '',
            'hp': 'XhW3K1eVgfEIjz3X5eLspgfHXQ1IhduL',
            'bs': 'submit',
            'HdnField': '{"__Page":{"LangCode_":"en-ca","_sID":"/find-a-surveyor"}}',
            'c0$guC$c$r0$guC$c$r0$guC$c$r0$guC$c$r1$guC$c$gdrMenu$ctl00$btnMobileMenu': '',
            'c1$guC$c$r0$guC$c$hn': '',
            'c1$guC$c$r0$guC$c$bc$hdnIsInitial': '',
            'c1$guC$c$r0$guC$c$bc$hdnSelTab': 'list',
            'c1$guC$c$r0$guC$c$bc$bc$txtSearch': name,
            'c1$guC$c$r0$guC$c$bc$bc$txtSearch_': name,
            'c1$guC$c$r0$guC$c$bc$bc$gdrpItems$ctl00$btnSurvey': '',
            'c1$guC$c$r0$guC$c$bc$bc$pgrBottom$hdnPage': '0',
            'c1$guC$c$r0$guC$c$bc$pgrBottom$hdnPage': '0',
            'hdngooglemap': '',
            '__EVENTTARGET': 'c1$guC$c$r0$guC$c$bc$bc$txtSearch',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': '',
            '__ASYNCPOST': 'true'
        }

        return [FormRequest(url="https://www.aols.org/find-a-surveyor", 
                            formdata=data, 
                            callback=self.parse_postal_code, 
                            cookies=cookies, 
                            headers=headers,
                            dont_filter=True)
                        ]
        