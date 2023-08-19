import scrapy
from bookscraper.items import BookItem
import random


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    
    custom_settings = {#this will overwrite the FEED settings in settings.py 
        'FEEDS':{
            'booksdata.json':{'format' : 'json', 'overwrite' : True}
        }
    }
    
    #these many user_agents are still not enough
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
    ]

    def parse(self, response):#runs when response comes back from webpage
        books = response.css('article.product_pod')
        ##THIS IS THE CODE TO EXTRACT DATA VISIBLE ON WEBPAGE
        # for book in books:
        #     yield{
        #         'name': book.css('h3 a::text').get(),
        #         'price' : book.css('.product_price .price_color::text').get(),
        #         'URL' : book.css('h3 a').attrib['href'],
        #     }
        # next_page = response.css('li.next a::attr(href)').get()
        
        # if next_page is not None:# checking if we have reached last page
        #     if 'catalogue/' in next_page:2
        #         next_page_url = "https://books.toscrape.com/" + next_page
        #     else:
        #         next_page_url = "https://books.toscrape.com/catalogue/" + next_page
        #     yield response.follow(next_page_url, callback = self.parse)#go to next page url callback run once we get the response back
        
        
        ##IN THIS CODE WE WILL ENTER EACH BOOKS URL SEPERATELY AND SCRAP DATA FROM THERE AS WELL
        for book in books:
            relative_url = book.css('h3 a::attr(href)').get()
            if 'catalogue/' in relative_url:
                book_url = "https://books.toscrape.com/" + relative_url
            else:
                book_url = "https://books.toscrape.com/catalogue/" + relative_url
            yield response.follow(book_url, callback = self.parse_book_page, headers = {"User-Agents": self.user_agent_list[random.randint(0, len(self.user_agent_list)-1)]})#callback is used to run a function given in it after url is opened
            
        next_page = response.css('li.next a::attr(href)').get()
        
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = "https://books.toscrape.com/" + next_page
            else:
                next_page_url = "https://books.toscrape.com/catalogue/" + next_page
            yield response.follow(next_page_url, callback = self.parse)
            
    def parse_book_page(self, response):
        table_rows = response.css("table tr")
        book_item = BookItem()
        
        book_item['url'] =             response.url
        book_item['title'] =           response.css('.product_main h1::text').get() 
        book_item['upc'] =             table_rows[0].css('td::text').get()
        book_item['product_type'] =    table_rows[1].css('td::text').get()
        book_item['price_excl_tax'] =  table_rows[2].css('td::text').get()
        book_item['price_incl_tax'] =  table_rows[3].css('td::text').get()
        book_item['tax'] =             table_rows[4].css('td::text').get()
        book_item['availability'] =    table_rows[5].css('td::text').get()
        book_item['num_reviews'] =     table_rows[6].css('td::text').get()
        book_item['stars'] =           response.css('p.star-rating').attrib['class']
        book_item['category'] =        response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get()
        book_item['description'] =     response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()
        book_item['price'] =           response.css('p.price_color::text').get()        
        yield book_item
                