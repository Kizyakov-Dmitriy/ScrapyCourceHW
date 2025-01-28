import scrapy


class OrgSpider(scrapy.Spider):
    name = "org"
    allowed_domains = ["merchantpoint.ru"]
    start_urls = ["https://merchantpoint.ru/brands"]
    max_pages = 200

    def parse(self, response):
        hrefs = response.xpath('//td/a/@href').getall()
        for href in hrefs:
            yield scrapy.Request(url=self.start_urls[0].replace('/brands', '') + href, callback=self.parse_org)
        if self.max_pages > 0:
            self.max_pages -= 1
            next_page = response.xpath("//a[@class = 'page-link' and contains(text(), 'Вперед')]/@href").get()
            yield scrapy.Request(url=next_page)


    def parse_org(self, response):
        org_data = {
            'org_description': response.xpath("//div[@class = 'form-group mb-2']/p[2]/text()").get(),
            'org_name': response.xpath('//h1/text()').get()
        }

        hrefs = response.xpath("//div[@id = 'terminals']//a[contains(@href, 'merchant')]/@href").getall()
        for href in hrefs:
            yield scrapy.Request(
                url=self.start_urls[0].replace('/brands', '') + href,
                callback=self.parse_merchant,
                cb_kwargs={'org_data': org_data}
            )

    def parse_merchant(self, response, org_data):
        merchant_data = {
            'merchant_name': response.xpath("//b[text() = 'MerchantName']/parent::p/text()").get(),
            'mcc': response.xpath("//b[text() = 'MCC код']/parent::p/a/text()").get(),
            'address': response.xpath("//b[text() = 'Адрес торговой точки']/parent::p/text()").get(),
            'geo_coordinates': response.xpath("//b[text() = 'Геокоординаты: ']/parent::p/text()").get(),
        }

        merchant_data.update(org_data)

        return merchant_data