from scrapy import Request, Spider
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate("./spiders/hj-mvp-firebase-adminsdk-9cexo-e0798ead61.json")
    firebase_admin.initialize_app(cred)


class nutritionSpider(Spider):
    name = 'nutrition_spider'
    start_urls = ['https://nutritiondata.self.com/']
    category_url = 'https://nutritiondata.self.com/foods-{}000000000000000000.html'
    custom_settings = {
            'RETRY_TIMES': 10,
            'RETRY_HTTP_CODES' : [503],
            'CONCURRENT_REQUESTS': 1,
            'DOWNLOAD_DELAY': 3
    }

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    def parse(self, response):
        categories = response.xpath("//td/select[contains(@class,'catList')]/option/@value").extract()
        for category in categories[1:]:
            yield Request(url=self.category_url.format(category),
                          callback=self.data_page,
                          headers=self.headers
                          )

    def data_page(self, response):
        data_page_links = response.xpath("//td/a[contains(@class,'list')]/@href").extract()
        for link in data_page_links:
            yield Request(url='https://nutritiondata.self.com{}'.format(link),
                          callback=self.parse_data,
                          headers=self.headers
                          )
        next_page = response.css("td+ td a::attr(href)").extract()
        if next_page:
            next_page = next_page[0].split("('")[-1].split("')")[0]
            yield Request(url='https://nutritiondata.self.com{}'.format(next_page),
                          callback=self.data_page,
                          headers=self.headers,
                          dont_filter=False
                          )

    def parse_data(self, response):
        name = response.xpath('//div[contains(@class,"facts-heading")]/text()').get() or response.xpath('//title/text()').get().strip()
        res = response.xpath('//script[@type="text/javascript"]').extract()[33]
        data = {
            'Calories': res.split('NUTRIENT_0:')[-1].split('"')[0],
            'Total Carbohydrate': res.split(', NUTRIENT_4:"')[-1].split('"')[0],
            'Dietary Fiber': res.split(', NUTRIENT_5:"')[-1].split('"')[0],
            'Starch': res.split(', NUTRIENT_6:"')[-1].split('"')[0],
            'Sugars': res.split(', NUTRIENT_7:"')[-1].split('"')[0],
            'Sucrose': res.split(', NUTRIENT_8:"')[-1].split('"')[0],
            'Glucose': res.split(', NUTRIENT_9:"')[-1].split('"')[0],
            'Fructose': res.split('NUTRIENT_10:"')[-1].split('"')[0],
            'Lactose': res.split('NUTRIENT_11:"')[-1].split('"')[0],
            'Maltose': res.split('NUTRIENT_12:"')[-1].split('"')[0],
            'Galactose': res.split('NUTRIENT_13:"')[-1].split('"')[0],
            'Total fat': res.split('NUTRIENT_14:"')[-1].split('"')[0],
            'Saturated Fat': res.split('NUTRIENT_15:"')[-1].split('"')[0],
            '4:00': res.split('NUTRIENT_16:"')[-1].split('"')[0],
            '6:00': res.split('NUTRIENT_17:"')[-1].split('"')[0],
            '8:00': res.split('NUTRIENT_18:"')[-1].split('"')[0],
            '10:00': res.split('NUTRIENT_19:"')[-1].split('"')[0],
            '12:00': res.split('NUTRIENT_20:"')[-1].split('"')[0],
            '13:00': res.split('NUTRIENT_21:"')[-1].split('"')[0],
            '14:00': res.split('NUTRIENT_22:"')[-1].split('"')[0],
            '15:00': res.split('NUTRIENT_23:"')[-1].split('"')[0],
            '16:00': res.split('NUTRIENT_24:"')[-1].split('"')[0],
            '17:00': res.split('NUTRIENT_25:"')[-1].split('"')[0],
            '18:00': res.split('NUTRIENT_26:"')[-1].split('"')[0],
            '19:00': res.split('NUTRIENT_27:"')[-1].split('"')[0],
            '20:00': res.split('NUTRIENT_28:"')[-1].split('"')[0],
            '22:00': res.split('NUTRIENT_29:"')[-1].split('"')[0],
            '24:00:00': res.split('NUTRIENT_30:"')[-1].split('"')[0],
            'Monounsaturated Fat': res.split('NUTRIENT_31:"')[-1].split('"')[0],
            '14:01': res.split('NUTRIENT_32:"')[-1].split('"')[0],
            '15:01': res.split('NUTRIENT_33:"')[-1].split('"')[0],
            '16:1 undifferentiated': res.split(', NUTRIENT_34:"')[-1].split('"')[0],
            '16:1 c': res.split(', NUTRIENT_35:"')[-1].split('"')[0],
            '16:1 t': res.split(', NUTRIENT_36:"')[-1].split('"')[0],
            '17:01': res.split(', NUTRIENT_37:"')[-1].split('"')[0],
            '18:1 undifferentiated': res.split(', NUTRIENT_38:"')[-1].split('"')[0],
            '18:1 c': res.split(', NUTRIENT_39:"')[-1].split('"')[0],
            '18:1 t': res.split(', NUTRIENT_40:"')[-1].split('"')[0],
            '20:01': res.split(', NUTRIENT_41:"')[-1].split('"')[0],
            '22:1 undifferentiated': res.split(', NUTRIENT_42:"')[-1].split('"')[0],
            '22:1 c': res.split(', NUTRIENT_43:"')[-1].split('"')[0],
            '22:1 t': res.split(', NUTRIENT_44:"')[-1].split('"')[0],
            '24:1 c': res.split(', NUTRIENT_45:"')[-1].split('"')[0],
            'Polyunsaturated Fat': res.split(', NUTRIENT_46:"')[-1].split('"')[0],
            '16:2 undifferentiated': res.split(', NUTRIENT_47:"')[-1].split('"')[0],
            '18:2 undifferentiated': res.split(', NUTRIENT_48:"')[-1].split('"')[0],
            '18:2 n-6 c,c': res.split(', NUTRIENT_49:"')[-1].split('"')[0],
            '18:2 c,t': res.split(', NUTRIENT_50:"')[-1].split('"')[0],
            '18:2 t,c': res.split(', NUTRIENT_51:"')[-1].split('"')[0],
            '18:2 t,t': res.split(', NUTRIENT_52:"')[-1].split('"')[0],
            '18:2 i': res.split(', NUTRIENT_53:"')[-1].split('"')[0],
            '18:2 t not further defined': res.split(', NUTRIENT_54:"')[-1].split('"')[0],
            '18:03': res.split(', NUTRIENT_55:"')[-1].split('"')[0],
            '18:3 n-3, c,c,c': res.split(', NUTRIENT_56:"')[-1].split('"')[0],
            '18:3 n-6, c,c,c': res.split(', NUTRIENT_57:"')[-1].split('"')[0],
            '18:4 undifferentiated': res.split(', NUTRIENT_58:"')[-1].split('"')[0],
            '20:2 n-6 c,c': res.split(', NUTRIENT_59:"')[-1].split('"')[0],
            '20:3 undifferentiated': res.split(', NUTRIENT_60:"')[-1].split('"')[0],
            '20:3 n-3': res.split(', NUTRIENT_61:"')[-1].split('"')[0],
            '20:3 n-6': res.split(', NUTRIENT_62:"')[-1].split('"')[0],
            '20:4 undifferentiated': res.split(', NUTRIENT_63:"')[-1].split('"')[0],
            '20:4 n-3': res.split(', NUTRIENT_64:"')[-1].split('"')[0],
            '20:4 n-6': res.split(', NUTRIENT_65:"')[-1].split('"')[0],
            '20:5 n-3': res.split(', NUTRIENT_66:"')[-1].split('"')[0],
            '22:02': res.split(', NUTRIENT_67:"')[-1].split('"')[0],
            '22:5 n-3': res.split(', NUTRIENT_68:"')[-1].split('"')[0],
            '22:6 n-3': res.split(', NUTRIENT_69:"')[-1].split('"')[0],
            'Total trans fatty acids': res.split(', NUTRIENT_70:"')[-1].split('"')[0],
            'Total trans-monoenoic fatty acids': res.split(', NUTRIENT_71:"')[-1].split('"')[0],
            'Total trans-polyenoic fatty acids': res.split(', NUTRIENT_132:"')[-1].split('"')[0],
            'Total Omega-3 fatty acids': res.split(', NUTRIENT_139:"')[-1].split('"')[0],
            'Total Omega-6 fatty acids': res.split(', NUTRIENT_140:"')[-1].split('"')[0],
            'Cholesterol': res.split(', NUTRIENT_72:"')[-1].split('"')[0],
            'Phytosterols': res.split(', NUTRIENT_73:"')[-1].split('"')[0],
            'Campesterol': res.split(', NUTRIENT_74:"')[-1].split('"')[0],
            'Stigmasterol': res.split(', NUTRIENT_75:"')[-1].split('"')[0],
            'Beta-sitosterol': res.split(', NUTRIENT_76:"')[-1].split('"')[0],
            'Protein': res.split(', NUTRIENT_77:"')[-1].split('"')[0],
            'Tryptophan': res.split(', NUTRIENT_78:"')[-1].split('"')[0],
            'Threonine': res.split(', NUTRIENT_79:"')[-1].split('"')[0],
            'Isoleucine': res.split(', NUTRIENT_80:"')[-1].split('"')[0],
            'Leucine': res.split(', NUTRIENT_81:"')[-1].split('"')[0],
            'Lysine': res.split(', NUTRIENT_82:"')[-1].split('"')[0],
            'Methionine': res.split(', NUTRIENT_83:"')[-1].split('"')[0],
            'Cystine': res.split(', NUTRIENT_84:"')[-1].split('"')[0],
            'Phenylalanine': res.split(', NUTRIENT_85:"')[-1].split('"')[0],
            'Tyrosine': res.split(', NUTRIENT_86:"')[-1].split('"')[0],
            'Valine': res.split(', NUTRIENT_87:"')[-1].split('"')[0],
            'Arginine': res.split(', NUTRIENT_88:"')[-1].split('"')[0],
            'Histidine': res.split(', NUTRIENT_89:"')[-1].split('"')[0],
            'Alanine': res.split(', NUTRIENT_90:"')[-1].split('"')[0],
            'Aspartic acid': res.split(', NUTRIENT_91:"')[-1].split('"')[0],
            'Glutamic acid': res.split(', NUTRIENT_92:"')[-1].split('"')[0],
            'Glycine': res.split(', NUTRIENT_93:"')[-1].split('"')[0],
            'Proline': res.split(', NUTRIENT_94:"')[-1].split('"')[0],
            'Serine': res.split(', NUTRIENT_95:"')[-1].split('"')[0],
            'Hydroxyproline': res.split(', NUTRIENT_96:"')[-1].split('"')[0],
            'Vitamin A': res.split(', NUTRIENT_97:"')[-1].split('"')[0],
            'Retinol': res.split(', NUTRIENT_98:"')[-1].split('"')[0],
            'Retinol Activity Equivalent': res.split(', NUTRIENT_99:"')[-1].split('"')[0],
            'Alpha Carotene': res.split(', NUTRIENT_133:"')[-1].split('"')[0],
            'Beta Carotene': res.split(', NUTRIENT_134:"')[-1].split('"')[0],
            'Beta Cryptoxanthin': res.split(', NUTRIENT_135:"')[-1].split('"')[0],
            'Lycopene': res.split(', NUTRIENT_136:"')[-1].split('"')[0],
            'Lutein+Zeaxanthin': res.split(', NUTRIENT_137:"')[-1].split('"')[0],
            'Vitamin C': res.split(', NUTRIENT_100:"')[-1].split('"')[0],
            'Vitamin D': res.split(', NUTRIENT_101:"')[-1].split('"')[0],
            'Vitamin E (Alpha Tocopherol)': res.split(', NUTRIENT_102:"')[-1].split('"')[0],
            'Vitamin K': res.split(', NUTRIENT_103:"')[-1].split('"')[0],
            'Beta Tocopherol': res.split(', NUTRIENT_104:"')[-1].split('"')[0],
            'Gamma Tocopherol': res.split(', NUTRIENT_105:"')[-1].split('"')[0],
            'Delta Tocopherol': res.split(', NUTRIENT_106:"')[-1].split('"')[0],
            'Thiamin': res.split(', NUTRIENT_107:"')[-1].split('"')[0],
            'Riboflavin': res.split(', NUTRIENT_108:"')[-1].split('"')[0],
            'Niacin': res.split(', NUTRIENT_109:"')[-1].split('"')[0],
            'Vitamin B6': res.split(', NUTRIENT_110:"')[-1].split('"')[0],
            'Folate': res.split(', NUTRIENT_111:"')[-1].split('"')[0],
            'Food Folate': res.split(', NUTRIENT_112:"')[-1].split('"')[0],
            'Folic Acid': res.split(', NUTRIENT_113:"')[-1].split('"')[0],
            'Dietary Folate Equivalents': res.split(', NUTRIENT_114:"')[-1].split('"')[0],
            'Vitamin B12': res.split(', NUTRIENT_115:"')[-1].split('"')[0],
            'Pantothenic Acid': res.split(', NUTRIENT_116:"')[-1].split('"')[0],
            'Choline': res.split(', NUTRIENT_143:"')[-1].split('"')[0],
            'Betaine': res.split(', NUTRIENT_144:"')[-1].split('"')[0],
            'Calcium': res.split(', NUTRIENT_117:"')[-1].split('"')[0],
            'Iron': res.split(', NUTRIENT_118:"')[-1].split('"')[0],
            'Magnesium': res.split(', NUTRIENT_119:"')[-1].split('"')[0],
            'Phosphorus': res.split(', NUTRIENT_120:"')[-1].split('"')[0],
            'Potassium': res.split(', NUTRIENT_121:"')[-1].split('"')[0],
            'Sodium': res.split(', NUTRIENT_122:"')[-1].split('"')[0],
            'Zinc': res.split(', NUTRIENT_123:"')[-1].split('"')[0],
            'Copper': res.split(', NUTRIENT_124:"')[-1].split('"')[0],
            'Manganese': res.split(', NUTRIENT_125:"')[-1].split('"')[0],
            'Selenium': res.split(', NUTRIENT_126:"')[-1].split('"')[0],
            'Fluoride': res.split(', NUTRIENT_145:"')[-1].split('"')[0],
            'Alcohol': res.split(', NUTRIENT_127:"')[-1].split('"')[0],
            'Water': res.split(', NUTRIENT_128:"')[-1].split('"')[0],
            'Ash': res.split(', NUTRIENT_129:"')[-1].split('"')[0],
            'Caffeine': res.split(', NUTRIENT_130:"')[-1].split('"')[0],
            'Theobromine': res.split(', NUTRIENT_131:"')[-1].split('"')[0]
        }
        db = firestore.client()
        doc_ref = db.collection(u'Nutritions').document(name)
        doc_ref.set(data)

        return data
