import scrapy
from acaSpider.items import AcaspiderItem
from scrapy.utils.project import get_project_settings

'''
title = scrapy.Field()
authors = scrapy.Field()
year = scrapy.Field()
typex = scrapy.Field()
subjects = scrapy.Field()
url = scrapy.Field()
abstract = scrapy.Field()
citation = scrapy.Field()
'''


class IEEESpider(scrapy.Spider):
    name = "IEEE_Spider"
    allowed_domains = ["ieeexplore.ieee.org"]
    start_urls = get_project_settings().get('IEEE_URL')
    


    def parse(self, response):
        # Developing in progress
        item = AcaspiderItem()
        subresponse = response.xpath('//xpl-results-list/div[@class="List-results-items"]')
        item['title'] = []
        item['authors'] = []
        item['year'] = []
        item['typex'] = []
        item['subjects'] = []
        item['url'] = []
        item['abstract'] = []
        item['citation'] = []

        # print(len(subresponse))

        # Extracting info
        # Function properly as of 2021.01.21
        for res in subresponse:
            try:
                title = res.xpath('.//xpl-results-item//div[@class="col result-item-align"]/h2/a').xpath('string(.)').extract()[0]
            except Exception as e:
                title = '[Title Unknown]'
            finally:
                item['title'].append(title)

            try:
                authors_raw = res.xpath('.//xpl-results-item//div[@class="col result-item-align"]//p[@class="author"]//a').xpath('string(.)').extract()
                authors = self.merge_authors(authors_raw)
            except Exception as e:
                authors = '[Authors Unknown]'
            finally:
                item['authors'].append(authors)

            try:
                year_raw = res.xpath('.//xpl-results-item//div[@class="col result-item-align"]/div[@class="description"]/div[@class="publisher-info-container"]/span[1]').xpath('string(.)').extract()[0]
                year = self.process4year(year_raw)
            except Exception as e:
                year = '[Publication Year Unknown]'
            finally:
                item['year'].append(year)

            try:
                typex = res.xpath('.//xpl-results-item//div[@class="col result-item-align"]/div[@class="description"]/a').xpath('string(.)').extract()[0]
            except Exception as e:
                typex = '[Origins Unknown]'
            finally:
                item['typex'].append(typex)

            item['subjects'].append(' ')

            try:
                url = 'https://ieeexplore.ieee.org'+res.xpath('.//xpl-results-item/div/div/h2/a/@href').extract()[0]
            except Exception as e:
                url = '[URL Unknown]'
            finally:
                item['url'].append(url)


            try:
                abstract = res.xpath('.//div[@class="js-displayer-content u-mt-1 stats-SearchResults_DocResult_ViewMore hide"]/span/text()').extract()[0]
            except Exception as e:
                abstract = '[Abstract Unknown]'
            finally:
                item['abstract'].append(abstract)

            try:
                citation_raw = res.xpath('.//xpl-results-item//div[@class="col result-item-align"]/div[@class="description"]//a[contains(@href,"tabFilter=papers#citations")]/text()').extract()[0]
                citation = self.process4citation(citation_raw)
            except Exception as e:
                citation = '-1'
            finally:
                item['citation'].append(citation)
        
        yield item

        print(str(len(subresponse))+' results')

        # Next page
        if len(subresponse) > 0:
            current_url = response.request.url
            next_url = ''
            string_start = current_url.find('&pageNumber=')
            string_end = current_url.find('&', string_start+1)
            if string_start == -1:
                next_url = current_url+'&pageNumber=2'
            elif string_end == -1:
                page_number = int(current_url[string_start+12:])
                page_number = page_number+1
                next_url = current_url[:string_start+12]+str(page_number)
            else:
                page_number = int(current_url[string_start+12:string_end])
                page_number = page_number+1
                next_url = current_url[:string_start+12]+str(page_number)+current_url[string_end:]
            
            yield scrapy.Request(next_url, callback=self.parse)






    def merge_authors(self, au_list):
        au_str = ''
        for i in au_list:
            au_str += i + ','
        return au_str.strip(',')

    def process4year(self, year):
        return year[year.find(': ') + 1:].strip()

    def process4citation(self, citation):
        return citation[citation.find(' (')+2:citation.find(')')].strip()