import pathlib
from bs4 import BeautifulSoup
from requests_html import HTMLSession


def data_from_url(_url):
    session = HTMLSession()
    cat = session.get(_url)
    cat.html.render()

    title, models = parse_html(cat.text)

    return title, models


def parse_html(_html):
    cat_soup = BeautifulSoup(_html, 'html.parser')
    title = cat_soup.find('title').contents[0]
    kk = cat_soup.find_all('table')
    kh = kk[0].find('thead')
    kb = kk[0].find('tbody')

    models = [m.find('strong').contents for m in kh.find_all('th')]

    cols = kb.find_all('tr')
    for col in cols:
        spec = [val.find('div').contents[0] for val in col.find_all('td') if val.find('div').contents ]
        for m, s in zip(models, spec):
            m.append(s)

    return title, models


def save_csv(path: pathlib.Path, models):

    with open(path / "models.csv", 'w') as file:
        for m in models:
            file.write("{},{},{},{},{},{},{},KUKA\n".format(
                m.model,
                m.model,
                m.reach,
                m.payload,
                m.weight,
                m.footprint[0],
                m.footprint[1])
                )
