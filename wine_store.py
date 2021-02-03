import requests
from bs4 import BeautifulSoup
import pandas as pd
from decimal import Decimal
from googletrans import Translator


wine_name = input('Please, enter a name of wine:\n')
formated_wine_name = wine_name.replace(' ', '+')
print(f'Searching {wine_name}. Wait, please...')
base_url = 'https://www.vinosribera.com'
base_url_detail = 'https://www.vinosribera.com/epages/ec5114.sf/sece0a131be3b/'
search_url = f'https://www.vinosribera.com/epages/ec5114.sf/es_ES/?ViewAction=FacetedSearchProducts&SearchString={formated_wine_name}'
translator = Translator()

data = {
    'Handle': [],
    'Title': [],
    'Body (HTML)': [],
    'Vendor': [],
    'Type': [],
    'Tags': [],
    'Published': [],
    'Option1 Name': [],
    'Option1 Value': [],
    'Option2 Name': [],
    'Option2 Value': [],
    'Option3 Name': [],
    'Option3 Value': [],
    'Variant SKU': [],
    'Variant Grams': [],
    'Variant Inventory Tracker': [],
    'Variant Inventory Qty': [],
    # 'Variant Inventory Policy': [],
    # 'Variant Fulfillment Service': [],
    'Variant Price': [],
    'Variant Compare At Price': [],
    'Variant Requires Shipping': [],
    'Variant Taxable': [],
    'Variant Barcode': [],
    'Image Src': [],
    'Image Position': [],
    'Image Alt Text': [],
    'Gift Card': [],
    'SEO Title': [],
    'SEO Description': [],
    'Variant Image': [],
    # 'Variant Weight Unit': [],
    'Variant Tax Code': [],
    'Cost per item': [],
}


name = ''
bodega = ''
category = ''
description = ''
sku = ''
bigImage = ''

GBP = 0.857679


def currency_converter(eur_amount):
    eur_amount = price_in_decimal(eur_amount)
    eur_no_spanish_iva = eur_amount - (eur_amount * Decimal(0.21))
    poundAmount = round(eur_no_spanish_iva * Decimal(GBP), 2)
    return poundAmount + profit(poundAmount)


def percentage(a, b):
    return round(a / b * 100, 2)


def price_in_decimal(price):
    price_decimal = Decimal(price.replace(',', '.'))
    return price_decimal


def profit(poundAmount):
    return poundAmount * Decimal(0.15)


def export_table_and_print(data):

    table = pd.DataFrame(data, columns=[
        'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Type', 'Tags', 'Published', 'Option1 Name', 'Option1 Value',
        'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU', 'Variant Grams',
        'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping', 'Variant Taxable', 'Variant Barcode',
        'Image Src', 'Image Position', 'Image Alt Text', 'Gift Card', 'SEO Title', 'SEO Description', 'Variant Image', 'Variant Tax Code', 'Cost per item'])
    table.index = table.index + 1
    clean_wine_name = wine_name.lower().replace(' ', '_')
    table.to_csv(f'{clean_wine_name}.csv', sep=',',
                 encoding='utf-8', index=False)
    print(table)


def get_wine_attributes(wi):

    name = wi.find('div', class_='ListItemProductTopFloatArea').find('a').text
    innnerTable = wi.find('table', class_='cke-table')

    if innnerTable != None and len(innnerTable.find_all('th')) > 1:

        bodega = innnerTable.find_all(
            'th')[0].text if len(innnerTable.find_all('th')) > 1 else 'N'
        image = wi.find('img', class_='ProductSmallImage')['src']

        print(image)

        url = wi.find('div', class_='ListItemProductTopFloatArea').find(
            'a')['href']
        type_wine = innnerTable.find_all('th')[1].text if len(
            innnerTable.find_all('th')) > 1 else 'N'
        quantity = innnerTable.find_all('th')[2].text
        year = innnerTable.find_all('th')[3].text
        temperature = innnerTable.find_all('th')[4].text
        price = currency_converter(wi.find('span', itemprop='price').text)
        currency = wi.find('span', itemprop='priceCurrency').text

        page2 = requests.get(base_url_detail+url)
        descriptionTemp = []

        if page2.status_code == requests.codes.ok:
            soup2 = BeautifulSoup(page2.text, 'lxml')
            wine_detail = soup2.find('div', itemprop="mainEntity")

            description = wine_detail.find(
                'div', class_="description").find_all('p')

            for des in description:
                if des.getText().strip() != '':
                    descriptionTemp.append(des.getText().strip())

            for tag in wine_detail.find_all('meta'):
                if tag.get("itemprop", None) == "sku":
                    sku = tag.get("content", None)
                    # data['SKU'].append(sku if sku else '')

                if tag.get("itemprop", None) == "category":
                    category = tag.get("content", None)
                    # data['Category'].append(category if category else '')

            bigImage = ''

            # print(wine_detail.find('div', id="ProductImages").find(
            # 'img', itemprop='image'))

            try:
                bigImage = wine_detail.find('div', id="ProductImages").find(
                    'img', itemprop='image')['data-src-ml']
            except:
                print('Exception')
            else:
                print('No Exception')

            # print('bigImage')
            # print(bigImage)
            # data['BigImage'].append(bigImage if bigImage else '')

        description = ''.join(descriptionTemp)

        type_result = compare_string(
            name.lower(), bodega.lower(), category.lower(), description.lower())

        if type_result != '' and bigImage != '' and description != '':

            print('Before ', description)

            description = translator.translate(
                description, src='es', dest='en').text

            print('After ', description)

            data['Handle'].append(sku+name if name else '')
            data['Title'].append(name if name else '')
            data['Body (HTML)'].append(description if description else '')
            data['Vendor'].append('Ribera del Duero Wines')
            data['Type'].append(type_result if type_result else '')
            data['Tags'].append(type_wine if type_wine else '')
            data['Published'].append('TRUE')
            data['Option1 Name'].append('')
            data['Option1 Value'].append('')
            data['Option2 Name'].append('')
            data['Option2 Value'].append('')
            data['Option3 Name'].append('')
            data['Option3 Value'].append('')
            data['Variant SKU'].append(sku if sku else '')
            data['Variant Grams'].append('')
            data['Variant Inventory Tracker'].append('')
            data['Variant Inventory Qty'].append('')
            # data['Variant Inventory Policy'].append('')
            # data['Variant Fulfillment Service'].append('')
            data['Variant Price'].append(price if price else '')
            data['Variant Compare At Price'].append('')
            data['Variant Requires Shipping'].append('')
            data['Variant Taxable'].append('')
            data['Variant Barcode'].append('')
            data['Image Src'].append(base_url+bigImage if bigImage else '')
            data['Image Position'].append('')
            data['Image Alt Text'].append('')
            data['Gift Card'].append('')
            data['SEO Title'].append('')
            data['SEO Description'].append(description if description else '')
            data['Variant Image'].append(base_url+image if image else '')
            # data['Variant Weight Unit'].append('0')
            data['Variant Tax Code'].append('')
            data['Cost per item'].append('')


def compare_string(name, bodega, category, description):

    comparator = 'rosado'
    comparator2 = 'rose'
    comparator3 = 'tinto'
    comparator6 = 'rojo'
    comparator4 = 'box'
    comparator5 = 'disponible por cajas'
    comparator7 = 'roble'

    print('start++++++++++++++++++')

    if name == '' and bodega == '' and category == '' and description == '':
        return ''

    if name.find(comparator) != -1 or bodega.find(comparator) != -1 or category.find(comparator) != -1 or description.find(comparator) != -1 or name.find(comparator2) != -1 or bodega.find(comparator2) != -1 or category.find(comparator2) != -1 or description.find(comparator2) != -1:
        if name.find(comparator4) != -1 or bodega.find(comparator4) != -1 or category.find(comparator4) != -1 or description.find(comparator4) != -1 or name.find(comparator5) != -1 or bodega.find(comparator5) != -1 or category.find(comparator5) != -1 or description.find(comparator5) != -1:
            return 'ROSE-BOX'
        else:
            return 'ROSE'
    elif name.find(comparator3) != -1 or bodega.find(comparator3) != -1 or category.find(comparator3) != -1 or description.find(comparator3) != -1 or name.find(comparator6) != -1 or bodega.find(comparator6) != -1 or category.find(comparator6) != -1 or description.find(comparator6) != -1:
        if name.find(comparator4) != -1 or bodega.find(comparator4) != -1 or category.find(comparator4) != -1 or description.find(comparator4) != -1 or name.find(comparator5) != -1 or bodega.find(comparator5) != -1 or category.find(comparator5) != -1 or description.find(comparator5) != -1:
            #print('red_box', name, bodega, category, description)
            return 'RED-BOX'
        else:
            #print('red', name, bodega, category, description)
            return 'RED'
    else:
        if name.find(comparator4) != -1 or bodega.find(comparator4) != -1 or category.find(comparator4) != -1 or description.find(comparator4) != -1 or name.find(comparator5) != -1 or bodega.find(comparator5) != -1 or category.find(comparator5) != -1 or description.find(comparator5) != -1:
            if name.find(comparator7) != -1 or bodega.find(comparator7) != -1 or category.find(comparator7) != -1 or description.find(comparator7) != -1:
                return 'RED-BOX'
            else:
                return 'WHITE-BOX'
        elif name.find(comparator7) != -1 or bodega.find(comparator7) != -1 or category.find(comparator7) != -1 or description.find(comparator7) != -1:
            return 'RED'
        else:
            return 'WHITE'
    return ''


def parse_page(url):

    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++')

    page = requests.get(url)

    if page.status_code == requests.codes.ok:
        soup = BeautifulSoup(page.text, 'lxml')

        list_all_wine = soup.findAll('div', class_='ListItemProduct')

        for wi in list_all_wine:
            get_wine_attributes(wi)

        next_page_text = soup.find(
            'ul', class_="PagerSizeContainer").findAll('li')[-1].text
        print('ppppppppppppppppppppppppppppppppppppppppppppppppp')
        # print(soup)

        if next_page_text == '>':
            next_page_partial = soup.find('ul', class_="PagerSizeContainer").findAll(
                'li')[-1].find('a', rel='next')['href']

            print('=====================================next_page_partial')
            print(next_page_partial)

            next_page_url = 'https://www.vinosribera.com/epages/ec5114.sf/es_ES/' + next_page_partial
            parse_page(next_page_url)
        # No more 'Next' pages, finish the script
        else:
            export_table_and_print(data)


parse_page(search_url)
