# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from forex_python.converter import CurrencyRates
import pymongo

class BookscraperPipeline:
    def process_item(self, item, spider):
        
        ## Strip all whitespaces from strings
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != 'description':
                value = adapter.get(field_name)
                if value is not None:
                    adapter[field_name] = value.strip()  
        
        ## Category & Product Type --> Switch to Lowercase
        lowercase_keys = ['category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            if value is not None:
                adapter[lowercase_key] = value.lower()
            
        ## Price --> convert to float
        price_keys = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            if value is not None:
                value = value.replace('£', '')
                print(value)
                adapter[price_key] = CurrencyRates().convert("GBP", "INR", float(value))
        
        ##Availability --> extract number of books in stock
        availability_string = adapter.get('availability')
        split_string_array = availability_string.split('(')
        if availability_string is not None:
            if len(split_string_array) < 2:
                adapter['avalability'] = 0
            else:
                availability_array = split_string_array[1].split(' ') 
                adapter['availability'] = int(availability_array[0])     
            
            
        ## Reviews --> convert string to int
        num_reviews_string = adapter.get('num_reviews')
        adapter['num_reviews'] = int(num_reviews_string)  
        
        ##star rating to integer
        stars_string = adapter.get('stars')
        split_stars_array = stars_string.split(' ')
        star_text_value = split_stars_array[1].lower()
        
        if star_text_value == "zero":
            adapter['stars'] = 0
        elif star_text_value == "one":
            adapter['stars'] = 1
        elif star_text_value == "two":
            adapter['stars'] = 2
        elif star_text_value == "three":
            adapter['stars'] = 3
        elif star_text_value == "four":
            adapter['stars'] = 4
        elif star_text_value == "five":
            adapter['stars'] = 5
            
        return item

class SaveToMongoDBPipeline:
    
    def __init__(self):
        self.conn = pymongo.MongoClient(
           <connection string>#use localhost, 27017 to store in local host
        )
        db = self.conn['Books']
        self.collection = db['Books_tb']
        
    def process_item(self, item, spider):
        # book = {
        #     "url": item["url"], 
        #     "title": item["title"], 
        #     "upc": item["upc"], 
        #     "product_type": item["product_type"],
        #     "price_excl_tax": item["price_excl_tax"], 
        #     "price_incl_tax": item["price_incl_tax"], 
        #     "tax": item["tax"], 
        #     "availability": item["availability"], 
        #     "num_reviews": item["num_reviews"], 
        #     "stars": item["stars"], 
        #     "category": item["category"], 
        #     "description": item["description"], 
        #     "price": item["price"]
        # }
        
        self.collection.insert_one(dict(item)).inserted_id
        return item
    
    def close_spider(self, spider):
        self.conn.close()
        
