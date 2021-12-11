# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from logging import getLogger


logger = getLogger()

class IclosePipeline:
    
    seen_ids = set()
    
    def process_item(self, item, spider):
        
        if item['item_id'] in self.seen_ids:
            logger.warning(f'Dropping Item {item}')
            return {}
        
        self.seen_ids.add(item['item_id'])
        
        return item
