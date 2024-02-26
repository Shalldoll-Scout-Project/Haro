import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, element

import re

import logging
from tqdm import tqdm
from pprint import pprint
import json

import os
from dotenv import load_dotenv

load_dotenv()

FOLDER_PATH = os.environ.get('FOLDER_PATH', '.')
HEADLESS_MODE = os.environ.get('HEADLESS_MODE', '1') != '0'
PAGE_DEFAULT_TIMEOUT_IN_SEC = int(os.environ.get('PAGE_DEFAULT_TIMEOUT_IN_SEC', '60'))


def get_page_url(page_number: int) -> str:
    # filters set to Category=Gundam, Manufacturer=Bandai, ItemType=[HG, MG, PG, RG]
    return f"https://www.hlj.com/search/?GenreCode2=Gundam&Page={page_number}&Maker2=Bandai&MacroType2=High+Grade+Kits&MacroType2=High-Grade+Kits&MacroType2=Master+Grade+Kits&MacroType2=Master-Grade+Kits&MacroType2=Perfect+Grade+Kits&MacroType2=Perfect-Grade+Kits&MacroType2=Real+Grade+Kits&MacroType2=Real-Grade+Kits"


def extract_product_urls(soup: BeautifulSoup) -> list:
    product_grid = soup.select_one('#test > div')
    children = product_grid.find_all('div', recursive=False)
    logging.info(f'Found {len(children)} products on the page!')

    product_urls=[]
    for i, child in enumerate(children):
        a_tag = child.find('a')
        url = a_tag['href']
        product_urls.append(url)
    
    return product_urls


def extract_product_info(soup: BeautifulSoup, product_link: str) -> dict:
    product_info={}

    product_info['link'] = product_link

    product_info_div = soup.find('div', class_='product-info')
    product_info['stock_status'] = product_info_div.find('p').text.strip()
    product_info['name'] = product_info_div.find('h2', class_='page-title').text.strip()
    # for price, we need to strip away all chars except digits & '.', then convert into float
    price_str = product_info_div.select_one('p.price.product-margin').text.strip()
    price_str = ''.join(filter(lambda x: x.isdigit() or x == '.', price_str))
    product_info['price'] = float(price_str)
    
    product_desc_div = soup.find('div', class_='product-description')
    product_info['description'] = product_desc_div.text.strip()

    product_details_div = soup.find('div', class_='product-details')
    ul_element = product_details_div.find('ul')
    for detail in ul_element.find_all('li'):
        detail_text = detail.text.strip()
        key, val = [st.strip() for st in detail_text.split(':', 1)]
        key = key.lower().replace(' ', '_')

        # handle the special case of size/weight...
        if key == 'item_size/weight':
            size, weight = [st.strip() for st in val.split('/', 1)]
            
            numbers = re.findall(r'\d+\.\d+|\d+', size)
            size = [float(num) for num in numbers]

            weight = float(weight[:-1])

            product_info['size'] = size
            product_info['weight'] = weight

            continue

        product_info[key] = val

    return product_info


# TODO: rename this
async def run():
    async with async_playwright() as playwright:
        # TODO: rotating user agents for webdriver
        browser = await playwright.chromium.launch(headless=HEADLESS_MODE)
        context = await browser.new_context()
        page = await context.new_page()
        page.set_default_timeout(PAGE_DEFAULT_TIMEOUT_IN_SEC * 1000)


        # navigate to hlj site
        page_url = get_page_url(page_number=1)
        await page.goto(page_url)
        await page.wait_for_selector('#test > div')     # wait for the page content to load
        logging.info('Successfully navigated to page!')


        # determine page count
        pages = await page.query_selector_all('xpath=//html/body/div/div[2]/div[2]/div[2]/div[1]/span/ul/li')
        if len(pages) > 0:
            page_count = int(await pages[-2].text_content())
        else:
            logging.info("no pages found...")
            page_count = 1
        logging.info(f'Page count determined to be {page_count}')


        # change currency to Japanese Yen
        currency_switcher_button = await page.query_selector('button.switcher-currency__button')
        await currency_switcher_button.click()
        await currency_switcher_button.click()    # ?: why do i need to click twice??????
        await page.get_by_placeholder("Search currency").click()
        await page.get_by_placeholder("Search currency").fill("JPY")
        await page.get_by_role("link", name="Japanese Yen (JPY)").click()
        await asyncio.sleep(0.5)
        await page.wait_for_selector('#test > div')     # wait for the page content to load
        logging.info('Successfully switched currency to JPY!')

        
        # get all product urls on page
        product_urls = []
        for page_number in range(1, page_count+1):
            if page_number != 1:
                page_url = get_page_url(page_number=page_number)
                await page.goto(page_url)
                await page.wait_for_selector('#test > div')     # wait for the page content to load
                logging.info(f'Successfully navigated to page #{page_number}!')
            
            # save page source locally
            page_content = await page.content()
            soup = BeautifulSoup(page_content, "html.parser")
            logging.info(f'Saved page source for page #{page_number}')

            # extract info from the page
            logging.info(f'Extracting product urls from page #{page_number}...')
            product_urls_from_page = extract_product_urls(soup)
            product_urls += product_urls_from_page
        logging.info(f'Successfully extracted {len(product_urls)} product urls!')


        # extract product info from each url
        products = []
        for product_url in tqdm(product_urls):
            try:
                await page.goto(f"https://www.hlj.com{product_url}")
                await page.wait_for_selector('div.product-details')     # wait for the page content to load
                logging.info(f'Successfully navigated to product page for {product_url}')
                
                # save page source locally
                page_content = await page.content()
                soup = BeautifulSoup(page_content, "html.parser")


                logging.info(f"Attempting to extract product info for {product_url}")
                product_info = extract_product_info(soup, product_url)
                logging.info(f"Successfully extracted product info for {product_info['name']}")
                
                products.append(product_info)

                # TODO: unindent this later lol
                # write product info into a file
                with open(f'{FOLDER_PATH}/hlj_products_info.json', 'w') as file_obj:
                    file_obj.write(json.dumps(products, indent=4))
            except Exception as e:
                logging.error(f"Something went wrong while trying to extract product info for {product_url}")
                logging.error(e)
                with open(f'{FOLDER_PATH}/failed_attempts.txt', 'a') as file_obj:
                    file_obj.write(f'{product_url}\n')


async def main():
    # logging config
    logging.basicConfig(
        level = logging.INFO, 
        filename=f'{FOLDER_PATH}/hlj_web_scraper.log', 
        filemode='a', 
        format='%(asctime)s | %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    logging.info('Started running!')

    await run()

if __name__=='__main__':
    asyncio.run(main())