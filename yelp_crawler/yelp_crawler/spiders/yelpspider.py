import scrapy
from urllib.parse import quote


class YelpSelectors:
    class CSSSelectors:
        DIV_WITH_ALL_BUSINESSES = "div.businessName__09f24__EYSZE.css-1jq1ouh a.css-19v1rkv"
        NEXT_PAGE_LINK = "a.next-link.navigation-button__09f24__m9qRz.css-ahgoya::attr(href)"
        NUMBER_OF_REVIEWS_TEXT = "div.rating-text__09f24__VDRkR.css-ea1vb8 p::text"
        BUSINESS_NAME = "h1.css-1se8maq::text"
        BUSINESS_RATING = "div.arrange-unit__09f24__rqHTg.arrange-unit-fill__09f24__CUubG.css-v3nuob span.css-1p9ibgf::text"

    class XPathSelectors:
        BUSINESS_WEBSITE = "//div[@class='arrange-unit__09f24__rqHTg arrange-unit-fill__09f24__CUubG css-1qn0b6x']/p[text()='Business website']/following-sibling::p/a/text()"
        LIST_OF_REVIEWS = "//li[@class=' css-1q2nwpv']/div[@class=' css-1qn0b6x']"
        RELATIVE_REVIEWER_NAME = ".//div[@class='user-passport-info css-1qn0b6x']/span[@class='fs-block css-ux5mu6']/a/text()"
        RELATIVE_REVIEWER_LOCATION = ".//div[@class='user-passport-info css-1qn0b6x']/div[@class=' css-kzxnxo']/div[@class=' css-1qn0b6x']/span[@class=' css-qgunke']/text()"
        RELATIVE_REVIEW_DATE = ".//div[@class=' css-10n911v']//span[@class=' css-chan6m']/text()"


class YelpspiderSpider(scrapy.Spider):
    name = "yelpspider"
    MAIN_PAGE = "yelp.com"
    allowed_domains = [MAIN_PAGE]
    custom_settings = {
        "FEEDS": {
            "businesses_data.json": {"format": "json", "overwrite": True}
        }
    }

    MAX_NUMBER_OF_REVIEWS_TO_PARSE = 5

    def start_requests(self):
        category_name = getattr(self, "category_name", None)
        location = getattr(self, "location", None)

        if not category_name or not location:
            raise Exception("You need to specify both category_name and location atrributes. "
                            "Example: scrapy crawl yelpspider -a category_name='Contractors' -a location='San Francisco, CA'")
        
        url = "https://www." + self.MAIN_PAGE + f"/search?find_desc={quote(category_name)}&find_loc={quote(location)}"
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        businesses = response.css(YelpSelectors.CSSSelectors.DIV_WITH_ALL_BUSINESSES)

        for business in businesses:
            business_url = business.attrib["href"]
            yield response.follow(business_url, callback=self.parse_business)
        
        next_page = response.css(YelpSelectors.CSSSelectors.NEXT_PAGE_LINK).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_business(self, response):
        number_of_reviews_text = response.css(YelpSelectors.CSSSelectors.NUMBER_OF_REVIEWS_TEXT).get()
        number_of_reviews = int(number_of_reviews_text.split(" ")[0]) if number_of_reviews_text else 0

        yield {"business_name": response.css(YelpSelectors.CSSSelectors.BUSINESS_NAME).get(),
               "business_rating": response.css(YelpSelectors.CSSSelectors.BUSINESS_RATING).get("No rating"),
               "number_of_reviews": number_of_reviews,
                "business_yelp_url": response.url,
                "business_website": response.xpath(YelpSelectors.XPathSelectors.BUSINESS_WEBSITE).get("No website"),
               "reviews": self.parse_reviews(response.xpath(YelpSelectors.XPathSelectors.LIST_OF_REVIEWS))
               }
    
    def parse_reviews(self, review_divs):
        reviews = []

        for review_div in review_divs:
            review_data = {
                "reviewer_name": review_div.xpath(YelpSelectors.XPathSelectors.RELATIVE_REVIEWER_NAME).get(),
                "reviewer_location": review_div.xpath(YelpSelectors.XPathSelectors.RELATIVE_REVIEWER_LOCATION).get(),
                "review_date": review_div.xpath(YelpSelectors.XPathSelectors.RELATIVE_REVIEW_DATE).get()
            }
            reviews.append(review_data)

        return reviews
