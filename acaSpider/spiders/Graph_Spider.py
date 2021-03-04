import scrapy
from acaSpider.items import AcaspiderItem
from scrapy.utils.project import get_project_settings
from urllib.parse import urlparse

import regex
import json

'''
title = scrapy.Field()
authors = scrapy.Field()
year = scrapy.Field()
origin = scrapy.Field()
subjects = scrapy.Field()
url = scrapy.Field()
abstract = scrapy.Field()
citation = scrapy.Field()
'''


class GraphSpider(scrapy.Spider):

    '''
    Crawling from webpage of one paper
    '''

    name = 'Graph_Spider'
    dict_of_domains = {\
        'ieeexplore.ieee.org': 'IEEE'\
    }
    allowed_domains = dict_of_domains.keys()

    start_urls = get_project_settings().get('GRAPH_START_URL')
    


    def parse(self, response):
        item = AcaspiderItem()
        item['title'] = []
        item['authors'] = []
        item['year'] = []
        item['origin'] = []
        item['subjects'] = []
        item['url'] = []
        item['abstract'] = []
        item['citation'] = []

        # Get domain of current webpage
        webpage_domain = self.dict_of_domains.get(urlparse(response.url).netloc, 'UnknownDomain')

        print('Domain of current webpage:',webpage_domain)

        if webpage_domain == 'IEEE':
            dict_item = self.get_IEEE_item(response)
        else:
            pass
        '''
        for k,v in dict_item.items():
            item[k].append(v)
            print(k,v)
        '''
        yield item



    def get_IEEE_item(self, response):
        # extract a json object that contains most information
        script_list = response.xpath('//body/div[@id="LayoutWrapper"]/div/div/div/script').extract()
        target_str = ''
        for script_item in script_list:
            start_idx = script_item.find('xplGlobal.document.metadata')
            if start_idx != -1:
                target_str = script_item[start_idx:]
                break
        pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')
        json_list = pattern.findall(target_str)
        json_item = json_list[0]
        json_to_dict = json.loads(json_item)

        dict_item = dict()
        subresponse = response.xpath('//body//xpl-root//xpl-document-details')

        # TITLE, key = 'formulaStrippedArticleTitle' / 'title' / 'displayDocTitle'
        title = json_to_dict.get('formulaStrippedArticleTitle', '[Title Unknown]')
        dict_item['title'] = title

        # AUTHORS
        authors_raw = json_to_dict.get('authors', [dict()])
        authors = []
        for item in authors_raw:
            _temp_name = item.get('name')
            if _temp_name != None:
                authors.append(_temp_name)
        dict_item['authors'] = authors
        
        # YEAR, key = 'publicationYear' / 'copyrightYear'
        year_p = json_to_dict.get('publicationYear')
        year_c = json_to_dict.get('copyrightYear')
        year = '[Year Unknown]'
        if year_p != None:
            year = year_p
        elif year_c != None:
            year = year_c
        dict_item['year'] = year

        # ORIGIN, key = 'publicationTitle' / 'displayPublicationTitle'
        origin = json_to_dict.get('displayPublicationTitle', '[Origin Unknown]')
        dict_item['origin'] = origin

        # SUBJECTS


        # URL
        url = response.url
        dict_item['url'] = url

        # ABSTRACT, key = 'abstract'
        abstract = json_to_dict.get('abstract', '[Abstract Unknown]')
        dict_item['abstract'] = abstract

        # CITATION, key = 'citationCount'
        citation = json_to_dict.get('citationCount', '-1')
        dict_item['citation'] = citation

        # CITATION LIST

        # REFERENCE LIST
        reference_container_path = subresponse.xpath('//xpl-reference-panel/section/div[@class="document-ft-section-container"]/div/div[@class="reference-container"]')

        reference_list = []
        for idx in xrange(len(reference_container_path)):
            pass
            # print(reference_container_path)
            


            reference_item = dict()

            reference_list.append(reference_item)



        return dict_item
        
        



    def merge_authors(self, au_list):
        au_str = ''
        for i in au_list:
            au_str += i + ','
        return au_str.strip(',')

    def process4year(self, year):
        return year[year.find(': ') + 1:].strip()

    def process4citation(self, citation):
        return citation[citation.find(' (')+2:citation.find(')')].strip()