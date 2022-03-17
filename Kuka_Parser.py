import pathlib
from io import BytesIO
import random
import pdfplumber
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import re


def data_from_url(_url):
    session = HTMLSession()
    cat = session.get(_url)
    cat.html.render()

    title, models = parse_html(cat.text)

    with open("KUKA_Lib/DL/{}.html".format(title), 'w') as f:
        f.write(cat.text)

    save_csv(title, models)

    return models


def get_pdf(_url, name):
    session = HTMLSession()
    cat = session.get(_url).content
    mem_pdf = BytesIO(cat)

    with open("DL/{}.pdf".format(name), 'wb') as file:
        file.write(cat)

    return mem_pdf


def parse_html(_html):
    cat_soup = BeautifulSoup(_html, 'html.parser')
    title = cat_soup.find('title').contents[0]
    kk = cat_soup.find_all('table')
    kh = kk[0].find('thead')
    kb = kk[0].find('tbody')

    models = [m.find('strong').contents for m in kh.find_all('th')]
    # print(models)

    cols = kb.find_all('tr')
    for col in cols:
        spec = [val.find('div').contents for val in col.find_all('td')]
        models = [m + s for m, s in zip(models, spec)]

    models[0] += ['Weight', 'Footprint', 'Max Payload']

    print()
    print(models[0])

    for m in models[1:]:
        print()
        print(m)
        datasheet = m[-2].get('href')
        print(datasheet)
        try:
            dsheet = get_pdf(datasheet, m[0])
            model, w, fp, mp = parse_kuka_datasheet(dsheet)
            m += [w, fp[0], fp[1], mp]
            print(m)
        except:
            m += [10, 10, 10, 0]
    return title, models


def parse_kuka_datasheet(mem_pdf):
    with pdfplumber.open(mem_pdf) as temp:
        _page = temp.pages[0]
        ds = _page.extract_text().strip()
        model = ds.splitlines()[0]
        w = re.search(r"Weight approx. (\d+) kg", ds, flags=re.M | re.S | re.IGNORECASE)
        f = re.search(r"Footprint (\d+) mm x (\d+) mm", ds, flags=re.M | re.S | re.IGNORECASE)
        m = re.search(r"Maximum payload (\d+\.?\d*) kg", ds, flags=re.M | re.S | re.IGNORECASE)

        return model, w.groups()[0], f.groups(), m.groups()[0]


def save_csv(title, models):
    with open("{}.csv".format(title), 'w') as file:
        for m in models[1:]:
            file.write("{},{},{},{},{},{},{},KUKA\n".format(
                *re.search(r"(KR \d*) (\w.*)", m[0]).groups(),
                float(re.search(r"(\d+\.?\d*)\xa0.*", m[2]).group(1)) / 1000,
                float(re.search(r"(\d+\.?\d*)\xa0.*", m[1]).group(1)),
                float(m[-4]),
                float(m[-3]),
                float(m[-2])))


def data_from_file(_p: pathlib.Path):
    with open(_p, 'rb') as f:
        save_csv(*parse_html(f))
