To run the spider navigate to `yelp_crawler` folder:

```
cd yelp_crawler
```

And run the following command:
```
scrapy crawl yelpspider -a category_name='<chosen category>' -a location='<chosen location>'
```

Example:
```
scrapy crawl yelpspider -a category_name='Contractors' -a location='New York, NY'
```

Results will be saved into `yelp_crawler/businesses_data.json` file.
