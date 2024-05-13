import scrapy


class CianSpider(scrapy.Spider):
    name = 'cian'
    allowed_domains = ['kazan.cian.ru']
    start_urls = [
        'https://kazan.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=54&region=4777&room1=1'
    ]
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'DOWNLOAD_DELAY': 3,
        'FEED_EXPORT_ENCODING': 'utf-8'
    }

    def parse(self, response):
        page_number = response.url.split('p=')[1].split('&')[0]
        listings = response.xpath('//article[@data-name="CardComponent"]')
        for listing in listings:
            title = listing.xpath('.//span[@data-mark="OfferTitle"]/span/text()').get()
            subtitle = listing.xpath('*//span[@data-mark="OfferSubtitle"]/text()').get()

            data = title.split(', ')

            if subtitle:
                sub_data = subtitle.split(', ')

            if len(data) == 3:
                rooms = data[0][0]
                area = data[1]
                floor = data[2]
            else:
                rooms = sub_data[0][0]
                area = sub_data[1]
                floor = sub_data[2]

            price = listing.xpath('.//span[@data-mark="MainPrice"]/span/text()').get().replace("\xa0", ' ')
            add_id = listing.css('a._93444fe79c--link--VtWj6::attr(href)').get()[32:-1]
            page = page_number
            container = listing.xpath('.//div[@class="_93444fe79c--labels--L8WyJ"]/a/text()').extract()
            address = (", ".join(container))

            yield {
                'title': title,
                'price': price,
                'id': add_id,
                "page": page,
                "rooms": rooms,
                "floor": floor,
                "address": address,
                "area": area
            }

        next_page_url = response.xpath('//a[span[contains(text(), "Дальше")]]/@href').get()
        if next_page_url:
            yield response.follow(next_page_url, callback=self.parse)
        else:
            more_url = response.xpath('//a[span[contains(text(), "Показать ещё")]]/@href').get()
            if more_url:
                yield response.follow(more_url, callback=self.parse)
