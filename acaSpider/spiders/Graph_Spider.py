import scrapy
from acaSpider.items import AcaspiderItem
from scrapy.utils.project import get_project_settings
from urllib.parse import urlparse
from scrapy.http import HtmlResponse

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
        print(json.dumps(dict_item))

        yield item



    def get_IEEE_item(self, response):
        # extract a json object that contains most information
        script_list = response.xpath('//body/div[@id="LayoutWrapper"]/div/div/div/script').getall()
        target_str = ''
        for script_item in script_list:
            start_idx = script_item.find('xplGlobal.document.metadata')
            if start_idx != -1:
                target_str = script_item[start_idx:]
                break
        json_list = regex.findall(r'\{(?:[^{}]|(?R))*\}',target_str)
        # print(json_list)
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
        for item in reference_container_path:
            reference_item = dict()

            item_str = item.get()
            item_html = HtmlResponse(url='reference_item', body=item_str, encoding='utf-8')
            reference_info_str = item_html.xpath('//div/xpl-reference-item-migr/div/div/span[2]').xpath('string(.)').get()

            reference_title = regex.findall(r'\"(.+?)\"', reference_info_str)
            if len(reference_title) > 0:
                reference_title = reference_title[0]
            else:
                reference_title = '[Reference TITLE Unknown]'
            reference_item['reference_title'] = reference_title

            # REFERENCE URL DICT
            reference_url_dict = dict()
            # REFERENCE URL, possibly contained in info string
            if reference_info_str.find('[online]')>=0:
                _url = regex.findall(r'(?:(?:http|ftp|https)\:\/\/)?(?:[\w_-]+(?:(?:\.[\w_-]+)+))(?:[\w.@?^=\%&:/~+#-]*[\w@?^=\%&/~+#-])?', reference_info_str)
                # print('_url:', _url)
                if len(_url) > 0:
                    _url = _url[0]
                else:
                    _url = None
                reference_url_dict['original_webpage'] = _url

            # REFERENCE URL, class = 'stats-reference-link-crossRef' / 'stats-reference-link-googleScholar'
            _url = item_html.xpath('//div/xpl-reference-item-migr/div/div/div[@class="ref-links-container stats-reference-links-container"]//a[@class="stats-reference-link-crossRef"]/@href').get()
            reference_url_dict['cross_ref'] = _url
            _url = item_html.xpath('//div/xpl-reference-item-migr/div/div/div[@class="ref-links-container stats-reference-links-container"]//a[@class="stats-reference-link-googleScholar"]/@href').get()
            reference_url_dict['google_scholar'] = _url

            reference_url_dict = {k:v for k,v in reference_url_dict.items() if v is not None}
            reference_item['reference_url_dict'] = reference_url_dict

            reference_url = '[Reference URL Unknown]'
            # reference_url is the primary url in reference_url_dict
            key_priority = ['original_webpage', 'cross_ref', 'google_scholar']

            for key_str in key_priority:
                reference_url = reference_url_dict.get(key_str, '[Reference URL Unknown]')
                if reference_url != '[Reference URL Unknown]':
                    break
            reference_item['reference_url'] = reference_url
            reference_list.append(reference_item)

        dict_item['reference_list'] = reference_list

        return dict_item
        
        


