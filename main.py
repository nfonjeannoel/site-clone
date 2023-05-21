import os
import scrapy


class MyScraperSpider(scrapy.Spider):
    name = 'my_scraper'
    allowed_domains = ['example.com']  # Add the domain(s) you want to scrape
    start_urls = ['http://example.com']  # Add the starting URL(s) for scraping

    def parse(self, response):
        # Create the directory based on the URL
        base_path = response.url.split('//')[-1].replace('/', '_')
        os.makedirs(base_path, exist_ok=True)

        # Save the HTML content
        filename = 'index.html'
        filepath = os.path.join(base_path, filename)
        with open(filepath, 'wb') as file:
            file.write(response.body)

        # Extract and download CSS files
        css_links = response.css('link[rel="stylesheet"]::attr(href)').getall()
        for css_link in css_links:
            css_url = response.urljoin(css_link)
            yield scrapy.Request(css_url, callback=self.save_file, meta={'base_path': base_path})

        # Extract and download JavaScript files
        js_links = response.css('script[src]::attr(src)').getall()
        for js_link in js_links:
            js_url = response.urljoin(js_link)
            yield scrapy.Request(js_url, callback=self.save_file, meta={'base_path': base_path})

        # Follow and scrape all internal links
        for link in response.css('a::attr(href)').getall():
            if link.startswith('/') or link.startswith(self.allowed_domains):
                yield response.follow(link, callback=self.parse)

    def save_file(self, response):
        base_path = response.meta['base_path']
        filename = response.url.split('/')[-1]
        filepath = os.path.join(base_path, filename)
        with open(filepath, 'wb') as file:
            file.write(response.body)
