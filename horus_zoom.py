import time
import json
import docker
import requests
import concurrent.futures
from spider.spider import Spider
from datahub.mysql import Mysql
from datahub.redis import Redis
from pythontools.argparse import *
from pythontools.verbose import *
import settings


def reload_tor():
    try:
        client = docker.from_env()
        for container in client.containers.list():
            if container.attrs['Name'] == '/tor_socks_proxy':
                container.restart()
    except:
        pass

def print_ip():
    sources = [
        "http://whatismyip.akamai.com",
        "http://ifconfig.me",
        "http://ipecho.net/plain",
        "http://ipinfo.io/ip",
        "http://ifconfig.co",
    ]
    for source in sources:
        try:
            ip = requests.get(source, headers=settings.requests_headers,
                proxies=settings.requests_proxy).text
            verbose(ip, level=2)
            break
        except:
            verbose("Não foi possivel buscar o IP", source, label='WARN')


def worker2(product, store):
    verbose(product, store, level=1, label='INFO')

    ad = spider.get_ad_page(product, store)
    verbose(ad, level=4, label='INFO')

    product['id'] = ad['id']
    product['prices'] = ad['prices']

    pool.insert_ad(ad['id'], store, product)


def worker(store):
    verbose("Requesting Ads", level=1, label='INFO')
    products = spider.get_products(store)
    verbose("get_products", products, level=4, label='INFO')

    all_ads = []
    pular=1
    for prod in products:
        if prod['url'].find('lead?oid') != -1:
            all_ads.append(prod)
            continue

        if pular > 0:
            pular = pular -1
            continue
        # serial mode
        worker2(prod, store)
        exit()





    # with concurrent.futures.ThreadPoolExecutor(max_workers=settings.max_workers) as executor:
    #     future_mbl = {executor.submit(worker2, job, store): job for job in ads}
    #
    #     for future in concurrent.futures.as_completed(future_mbl):
    #         mbl = future_mbl[future]
    #         try:
    #             data = future.result()
    #         except Exception as exc:
    #             verbose('%r generated an exception: %s' % (url, exc), label='ERROR')


def main():
    # stop = False
    # try:
    #     if settings.filter_ads:
    #         stop = True
    #         verbose('FILTERING Ad', settings.filter_ads, level=1)
    #
    #         # serial mode
    #         # worker2(settings.filter_ads, 'UNKNOWN')
    #
    #         verbose(stop)
    # except:
    #     pass
    #
    # try:
    #     if settings.filter_store:
    #         stop = True
    #         verbose('FILTERING STORE', settings.filter_store, level=1)
    #         worker(settings.filter_store)
    #         stores = [settings.filter_store]
    # except:
    #     pass
    #
    # if stop == True:
    #     verbose('STOP', stop)
    #     return
    #
    # stores = database.get_stores()
    # verbose(stores, level=2)

    stores = ['celular/smartphone']

    # serial mode
    worker(stores[0])

    exit()
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=settings.max_workers) as executor:
        future_spider = {executor.submit(worker, job): job for job in stores}



spider = Spider()
database = Mysql()
pool = Redis()

while True:
    try:
        print_ip()
        main()
    except Exception as exc:
        verbose('%r generated an exception: %s' % (url, exc), label='ERROR')
    # break
