import scrapy
from scrapy_examples.items import ActivityReportPdf

class ExtractPdf(scrapy.Spider):
    name = "extract_pdf"

    async def start(self):
        url = "https://heig-vd.ch/a-propos/documents-officiels/"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        files_url = response.css("a.link--download::attr(href)").getall()
        for file_url in files_url:
            item = ActivityReportPdf()
            item["file_urls"] = [file_url]
            yield item