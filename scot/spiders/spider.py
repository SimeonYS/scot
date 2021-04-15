import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import ScotItem
from itemloaders.processors import TakeFirst
import json

pattern = r'(\xa0)?'
base = 'https://www.scotiabank.com/ca/en/about/news/perspectives/jcr:content/main-par/section_container/section-container-par/generic_filter.economicfilterservlet.{}.all.all.html'

class ScotSpider(scrapy.Spider):
	name = 'scot'
	offset = 0
	start_urls = [base.format(offset)]

	def parse(self, response):
		data = json.loads(response.text)
		for index in range(len(data['jsonArticles'])):
			link = data['jsonArticles'][index]['fragment_url']
			if not "pdf" in link:
				yield response.follow(link, self.parse_post)

		if self.offset < data['total_results']:
			self.offset += 9
			yield response.follow(base.format(self.offset), self.parse)

	def parse_post(self, response):
		date = response.xpath('//span[@class="article-date"]/text()').get()
		date = re.findall(r'\w+\s\d+\s\w+', date)
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="article-container container"]//text()[not (ancestor::div[@class="related-articles col-md-4"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=ScotItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
