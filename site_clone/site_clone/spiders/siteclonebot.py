import scrapy
import os
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))


class SiteclonebotSpider(scrapy.Spider):
    name = "siteclonebot"
    allowed_domains = ["fastapi.tiangolo.com", "cdn.jsdelivr.net"]
    # "fonts.googleapis.com",
    # "cdn.jsdelivr.net"]
    start_urls = ["https://fastapi.tiangolo.com/"]
    site_domain = "fastapi.tiangolo.com/"
    site_name = "fastApi"
    site_path = os.path.join(HERE, site_name)

    def parse(self, response):
        # Create the directory based on the URL
        # Save the HTML content
        filename = 'index.html'
        filepath = os.path.join(self.site_path, filename)
        if response.meta.get('is_internal'):
            filepath = self.get_filepath(response.url)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as file:
            file.write(response.body)

        # Extract and download CSS files
        css_links = response.css('link[rel="stylesheet"]::attr(href)').getall()
        for css_link in css_links:
            css_url = response.urljoin(css_link)
            yield scrapy.Request(css_url, callback=self.save_file)

        # # Extract and download JavaScript files
        js_links = response.css('script[src]::attr(src)').getall()
        for js_link in js_links:
            js_url = response.urljoin(js_link)
            yield scrapy.Request(js_url, callback=self.save_file)

        languages = response.css('a[hreflang]::attr(href)').getall()

        def link_is_language(link):
            for l in languages:
                if l in link and len(l) > 2:
                    return True

        # Follow and scrape all internal links
        for link in response.css('a::attr(href)').getall():
            parsed_link = urlparse(link)
            # print(parsed_link)
            if not parsed_link.scheme or not parsed_link.netloc or (
                    link.startswith('/') or link.startswith(self.allowed_domains[0])):
                # Reconstruct the absolute URL for internal links
                absolute_link = response.urljoin(link)
                if link_is_language(absolute_link):
                    continue
                yield response.follow(absolute_link, callback=self.parse, meta={'is_internal': True})

    def save_file(self, response):
        filepath = self.get_filepath(response.url)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as file:
            file.write(response.body)

    def get_filepath(self, url):
        components = url.split('//')[1].replace(self.site_domain, "").split('/')
        filename = components[-1] if components[-1] else 'index.html'
        filepath = os.path.join(self.site_path, *components[:-1], filename)
        return filepath
