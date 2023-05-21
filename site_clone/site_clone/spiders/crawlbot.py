import os

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class SiteclonebotCrawlSpider(CrawlSpider):
    name = "crawlbot"
    allowed_domains = ["fastapi.tiangolo.com",
                       "fonts.googleapis.com",
                       "cdn.jsdelivr.net"]
    start_urls = ["https://fastapi.tiangolo.com/"]
    site_name = "fastApi"

    rules = (
        Rule(LinkExtractor(), callback='parse_page', follow=True),
    )

    def parse_page(self, response):
        # Create the directory based on the URL
        base_path = self.get_base_path(response.url)
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

    def save_file(self, response):
        base_path = response.meta['base_path']
        filepath = self.get_filepath(response.url, base_path)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as file:
            file.write(response.body)

    def get_base_path(self, url):
        components = url.split('//')[1].split('/')
        return os.path.join(*components)

    def get_filepath(self, url, base_path):
        components = url.split('//')[1].split('/')
        filename = components[-1] if components[-1] else 'index.html'
        filepath = os.path.join(base_path, *components[:-1], filename)
        return filepath
