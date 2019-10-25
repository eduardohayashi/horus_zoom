import time
import json
import MySQLdb
import requests
from lxml import etree
from pythontools.verbose import *
import settings

class Spider(object):

    def __init__(self):
        verbose('Spider start')
        pass


    def request_parse_url(self, url, data=None):

        if not data:
            try:
                verbose('Request', url, level=3)
                response = requests.get(url,
                    headers=settings.requests_headers,
                    proxies=settings.requests_proxy,
                    cookies=settings.requests_cookies,
                    )
                verbose(response.text, level=4)
            except:
                verbose('Request error', url, label='ERROR')
                return
        else:
            try:
                verbose('Request  POST', url, level=3)
                response = requests.post(url,
                    headers=settings.requests_headers,
                    proxies=settings.requests_proxy,
                    cookies=settings.requests_cookies,
                    data=data,
                    )
                verbose(response.text, level=4)
            except:
                verbose('Request error', url, label='ERROR')
                return
            # verbose(etree.tostring( item.xpath("div[3]")[0] , pretty_print=True), level=4)

        try:
            html = etree.HTML(response.text)
        except:
            verbose('Parsing HTML error', url, label='ERROR')
            return

        return html


    def extract_product_list(self, url):

        html = self.request_parse_url(url)
        result = []
        count = 0
        for item in html.xpath("//form[@id='form-catprod']/ul/li"):
            if item.get('class').find('item') != 0:
                continue
            try:
                title = item.xpath("div[contains(@class, 'info-container')]//a/text()")[0]
            except:
                title = item.xpath("div[contains(@class, 'info-container')]/h2/span/text()")[0]

            try:
                link = item.xpath("div[contains(@class, 'info-container')]//a[1]")[0].get('href')
            except:
                link = item.xpath("div[contains(@class, 'info-container')]/h2/span[1]")[0].get('rel')
            url = f'https://www.zoom.com.br/{link}'


            try:
                price = item.xpath("div[contains(@class, 'price-container')]//span[2]/a/text()")[0]
            except:
                price = item.xpath("div[contains(@class, 'price-container')]//span[2]/span[1]/text()")[0]
            if not url:
                continue

            ad = dict(title=title, price=price, url=url)
            result.append(ad)
            count = count + 1
            # result.append(title[0])

        return result


    def get_products(self, slug):

        count = 1
        all_ads = []
        while True:
            url  = f"https://www.zoom.com.br/{slug}?pagenumber={count}"
            verbose(url, level=2, label='INFO')

            ads = self.extract_product_list(url)
            all_ads.extend(ads)
            count = count + 1
            verbose(len(ads))
            break

            if len(ads) != 36:
                break


        return all_ads


    def get_more_ads(self, prod_id):
        stop = False
        page = 1
        all_ads = []
        while stop != True:
            data = {
              '__pAct_': 'getmoreoffers',
              'prodid': prod_id,
              'catId': '7',
              'pagenumber': page,
              'highlightedItemID': '0',
              'resultorder': '7'
            }

            verbose('More Ads', page, prod_id)
            html = self.request_parse_url(
                'https://www.zoom.com.br/product_desk', data)


            try:
                all_ads.extend(html.xpath('//li'))
            except:
                stop = True

            page = page+1

        return all_ads


    def extract_ad_page(self, url, store):

        html = self.request_parse_url(url)

        result = []

        prod_id = html.xpath("//input[@name='prodid']")[0].get('value')
        verbose('Product_ID', prod_id)

        ads = html.xpath("//ul[@class='offers-list']/li")
        moreads = self.get_more_ads(prod_id)
        ads.extend(moreads)

        prices = []
        for item in ads:
            # if item.get('class').find('item') != 0:
            #     continue

            store = item.xpath("div//div[@class='col-store']/a")[0].get('title')
            price = item.xpath("div//span[@class='price__total']/text()")[0]

            info = dict(store=store, price=price)
            verbose(info)
            prices.append(info)

        return dict(id=prod_id, prices=prices)


    def get_ad_page(self, ad, store):

        url  = ad['url']
        verbose(url, level=2, label='INFO')

        return self.extract_ad_page(url, store)
