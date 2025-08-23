import scrapy
from bs4 import BeautifulSoup


# This spider will scrape Springfield locations from the Simpsons Fandom wiki.
# To run this spider, you need to have Scrapy installed and run the command: scrapy runspider crawler/springfield_crawler.py -o data/springfield_locations.json

class SimpsonsSpider(scrapy.Spider):
    name = 'spingfieldspider'
    start_urls = ['https://simpsons.fandom.com/wiki/Category:Springfield']

    def parse(self, response):
        for href in response.css('div.category-page__members')[0].css('a::attr(href)').extract():
            extracted_data = scrapy.Request( "https://simpsons.fandom.com"+href,
                                      callback=self.parse_springfield
                                    )
            yield extracted_data


        for next_page in response.css('a.category-page__pagination-next'):
            yield response.follow(next_page, self.parse)
    
    def parse_springfield(self, response):
        
        location_name = response.css('span.mw-page-title-main::text').extract()[0]
        location_name = location_name.strip()

        div_selector = response.css('div.page-content')[0]
        div_html = div_selector.extract()

        soup = BeautifulSoup(div_html).find('div')

        location_type=""

        if soup.find('aside'):
            aside= soup.find('aside')
            for cell in aside.find_all('div',{'class':'pi-data'}):
                if cell.find('h3'):
                    cell_name = cell.find('h3').text.strip()
                    if cell_name=='Use':
                        location_type = cell.find('div').text.strip()

            soup.find('aside').decompose()

        location_description = soup.text
        location_description = location_description.split('Trivia')[0].strip()


        yield dict(   
                    location_name= location_name,
                    location_type = location_type,
                    location_description=location_description

                )
        
