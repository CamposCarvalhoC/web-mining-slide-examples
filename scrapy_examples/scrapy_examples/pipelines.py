# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline
import hashlib

class RenameFilePipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        url_hash = hashlib.shake_256(request.url.encode()).hexdigest(5)
        perspective = request.url.split("/")[-2]
        filename = f"{url_hash}_{perspective}.pdf"

        return filename