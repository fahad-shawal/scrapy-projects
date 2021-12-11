# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class NcesPipeline:

    def process_item(self, item, spider):
        
        if not item['name']:
            raise DropItem(f"Missing Name in {item}")
        
        return item
        

class NcesPriceCleanerPipeline:
    wrong_values = ['-', 'X']

    def process_item(self, item, spider):
        new_prices = {}
        raw_prices = item['tution_fee'].copy()

        for name, val in raw_prices.items():
            if not val or not name or val in self.wrong_values or name == 'null' :
                continue
            
            new_prices[name] = val

        item['tution_fee'] = new_prices

        return item


class NcesSetProgramStatusPipeline:
    def process_item(self, item, spider):
        
        for dept in item['programs_offered'].keys():
            for key in item['programs_offered'][dept].keys():
                for sub_key, sub_val in item['programs_offered'][dept][key].items():
                    if sub_val == '-':
                        item['programs_offered'][dept][key][sub_key] = 'Inactive'
                    else:
                        item['programs_offered'][dept][key][sub_key] = 'Active'

        return item
