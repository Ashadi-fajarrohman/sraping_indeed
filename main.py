import requests
from bs4 import BeautifulSoup
import os
import json
import pandas as pd

url = 'https://www.indeed.com/jobs?'
site = 'https://www.indeed.com'
params = {'q': 'python entry level', 'l': 'New York State', 'vjk': 'da727c0cddda240e'}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/100.0.4896.88 Safari/537.36'}

res = requests.get(url, params=params, headers=headers)


def get_total_pages(query, location):
    params = {
        'q': query,
        'l': location,
        'vjk': 'da727c0cddda240e'
    }
    res = requests.get(url, params=params, headers=headers)

    # buat library baru
    try:
        os.mkdir('temp')
    except FileExistsError:
        pass

    # buat file baru untuk mengecek raw html
    with open('temp/res.html', 'w+') as outfile:
        outfile.write(res.text)
        outfile.close()

    # Scraping
    total_pages = []
    soup = BeautifulSoup(res.text, 'html.parser')
    pagination = soup.find('ul', 'pagination-list')
    pages = pagination.find_all('li')
    for page in pages:
        total_pages.append(page.text)

    total = int(max(total_pages))
    return total


def get_all_items(query, location, start, page):
    params = {
        'q': query,
        'l': location,
        'start': start,
        'vjk': 'da727c0cddda240e'
    }
    res = requests.get(url, params=params, headers=headers)

    with open('temp/res.html', 'w+') as outfile:
        outfile.write(res.text)
    outfile.close()

    soup = BeautifulSoup(res.text, 'html.parser')
    content = soup.find_all('table', 'jobCard_mainContent big6_visualChanges')

    job_list = []
    for item in content:
        title = item.find('h2', 'jobTitle').text
        company = item.find('span', 'companyName')
        company_name = company.text
        try:
            company_link = site + company.find('a')['href']
        except:
            company_link = 'Link is not available'

        # sortig data
        data_dict = {
            'title': title,
            'company name': company_name,
            'link': company_link
        }
        # ubah menjadi list
        job_list.append(data_dict)

    # buat library json
    try:
        os.mkdir('json_result')
    except FileExistsError:
        pass
    with open(f'json_result/{query}_in_{location}_page_{page}.json', 'w+') as json_data:
        json.dump(job_list, json_data)
    print('json created')
    return job_list


# create csv or exxel
def create_doc(dataFrame, filename):
    try:
        os.mkdir('data_result')
    except FileExistsError:
        pass

    df = pd.DataFrame(dataFrame)
    df.to_csv(f'data_result/{filename}.csv', index=False)
    df.to_excel(f'data_results{filename}.xlsx', index=False)

    print(f'File {filename}.csv and {filename}.xlsx sucessfuly')


def run():
    query = input('Enter your query :')
    location = input('Enter your location :')

    total = get_total_pages(query, location)
    counter = 0
    final_result = []
    for page in range(total):
        page += 1
        counter += 10
        final_result += get_all_items(query, location, counter, page)

    # formating data
    try:
        os.mkdir('reports')
    except FileExistsError:
        pass
    with open('reports/{}.json'.format(query), 'w+') as final_data:
        json.dump(final_result, final_data)
    print('json created')

    create_doc(final_result, query)


if __name__ == '__main__':
    run()
