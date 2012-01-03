# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import MapCompose, TakeFirst, Join
from scrapy.item import Item, Field

class CyespiderItem(Item):
    # define the fields for your item here like:
    # name = Field()
    pass

class CyeProductItem(Item):
    pkey = Field()
    title = Field()
    url = Field()
    
    origin_image_url = Field()
    image = Field()
    
    price = Field()
    
    price_image_url = Field() 
    detail = Field()
    is_update_detail = Field()
    crawl_time = Field()
    
    """"
    add_time = Field()
    producer = Field()
    production_place = Field()
    gross_weight = Field()
    name = Field()
    """
    pass

    
class CyeProductLoader(XPathItemLoader):
    default_item_class = CyeProductItem
    default_input_processor = MapCompose(lambda s: s.strip())
    default_output_processor = TakeFirst()
    description_out = Join()
    

