import re

from scrapy.http import FormRequest
from scrapy.spiders import Spider, Request


def clean(lst_or_str):
    if not lst_or_str:
        return

    if not isinstance(lst_or_str, list):
        return lst_or_str.strip()

    return [txt.strip() for txt in lst_or_str if txt.strip()]


class NcesParseSpider(Spider):
    name = 'nces-parse'

    def parse(self, response):
        item = {}
        
        item['url'] = response.url
        item['name'] = self.university_name(response)
        item['type'] = self.university_type(response)
        item['address'] = self.university_address(response)
        item['phone'] = self.university_phone(response)
        item['website'] = self.university_website(response)
        item['total_no_enrollments'] = self.university_enrollments(response)
        item['tution_fee'] = self.university_tution_fee(response)
        item['programs_offered'] = self.university_programs_offered(response)
        
        return item
    
    def university_name(self, response):
        css = '.headerlg::text'
        return clean(response.css(css).get())

    def university_type(self, response):
        css = '.collegedash .layouttab td:contains("Type:") + td::text'
        return clean(response.css(css).get())
    
    def university_address(self, response):
        css = '.divInst + span::text'
        raw_address = clean(response.css(css).get())
        if not raw_address:
            return ''
        
        state = clean(response.css('#MapWrap option[selected]::text').get())
        raw_address = state and raw_address.replace(state, '-|-')
        
        if '-|-' not in raw_address:
            return {'state': state, 'postal_code': '', 'city': raw_address}
        
        raw_city, postal_code = clean(raw_address.split('-|-'))

        raw_city = [txt for txt in raw_city.split(',') if txt]

        if len(raw_city) > 1:
            return {'state': state, 'postal_code': postal_code, 'city': raw_city[-1], 'address': raw_city[0]}
        
        return {'state': state, 'postal_code': postal_code, 'city': raw_city}

    def university_phone(self, response):
        css = '.collegedash .layouttab td:contains("General information:") + td::text'
        return clean(response.css(css).get())

    def university_website(self, response):
        css = '.collegedash .layouttab td:contains("Website:") + td a::text'
        return clean(response.css(css).get())

    def university_enrollments(self, response):
        css = '.collegedash .layouttab td:contains("Student population:") + td::text'
        return clean(response.css(css).get())

    def university_tution_fee(self, response):
        fee_details = {}

        css = '#expenses table:contains("Tuition") tbody tr, #expenses table:contains("tuition and fees") tbody tr'
        
        main_heading = ''
        sub_heading = ''

        for row in response.css(css):
            
            if row.css('.subrow') or row.css('.mainhead2'):
                sub_heading = ''
                main_heading = clean(row.css('td[scope="row"]::text').get())
                fee_details[main_heading] = {}
                continue
            
            if row.css('.odd'):
                sub_heading = clean(row.css('td[scope="row"]::text').get())
                fee_details[main_heading][sub_heading] = {}
                continue

            total_values_s = row.css('td')

            cat_name = clean(total_values_s[0].css('::text').get())

            if len(total_values_s) > 2:
                fees = clean(total_values_s[-2].css('::text').get())
            else:
                fees = clean(total_values_s[-1].css('::text').get())

            if sub_heading:
                fee_details[main_heading][sub_heading][cat_name] = fees
            elif main_heading:
                fee_details[main_heading][cat_name] = fees
            else:
                fee_details[cat_name] = fees

        return fee_details
        

    def university_programs_offered(self, response):
        programs_deatails = {}
        
        css = '#programs thead a::attr(title)'
        program_names = [clean(txt.replace('sort by', '')) for txt in response.css(css).getall()][1:]
        
        for program_s in response.css('#programs tbody .level1indent, #programs tbody .subrow'):
            
            if program_s.css('.subrow'):
                department = clean(program_s.css('td::text').get())
                programs_deatails[department] = {}
                continue
            else:
                name = clean(program_s.css('td[scope="row"]::text').get())
            
            seats = {}
            for index, seat_val in enumerate(clean(program_s.css('td::text').getall())[1:]):
                seats[program_names[index]] = seat_val
            
            programs_deatails[department][name] = seats
        
        return programs_deatails


class NcesCrawlSpider(Spider):
    name = 'nces-crawl'
    allowed_domains = ['nces.ed.gov']
    start_urls = ['https://nces.ed.gov/collegenavigator/']

    parser = NcesParseSpider()

    def parse(self, response):
        css = '[name="ctl00$cphCollegeNavBody$ucSearchMain$ucMapMain$lstState"] option::attr(value)'
        state_codes = response.css(css).getall()

        for code in state_codes[1:]:
            url = f'{self.start_urls[0]}?s={code}'
            yield Request(url, callback=self.parse_pagination)

    def parse_pagination(self, response):
        yield from self.parse_state_results(response)

        css = '#ctl00_cphCollegeNavBody_ucResultsMain_divPagingControls a:contains("Next Page")::attr(href)'
        url = clean(response.css(css).get())
        if not url:
            return 

        yield Request(response.urljoin(url), callback=self.parse_pagination)

    
    def parse_state_results(self, response):
        css = '#ctl00_cphCollegeNavBody_ucResultsMain_tblResults a::attr(href)'
        university_urls = response.css(css).getall()

        for raw_url in university_urls:
            url = f'{self.start_urls[0]}{raw_url}'
            yield Request(url, callback=self.parser.parse)
