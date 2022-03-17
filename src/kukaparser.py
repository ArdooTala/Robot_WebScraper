import pathlib
from io import BytesIO
import random
import pdfplumber
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import re


class KukaParser:
    def __init__(self, _url, pdf=None):
        self.url = _url

        self.manufacturer = 'KUKA'
        self.category = 'Generic'
        self.model = 'Unknown'
        self.weight = 0
        self.footprint = (0, 0)
        self.payload = 0
        self.payload_max = 0
        self.reach = 0
        self.construction = None
        self.mount = None

        self.html_data = None

        self.datasheet_url = None
        self._datasheetdata = None
        self.datasheet = None
        if pdf:
            self.datasheet = pdf

    def retrieve_html(self):
        session = HTMLSession()
        cat = session.get(self.url)
        cat.html.render()
        self.html_data = cat.text

    def download_pdf(self):
        if not self.datasheet_url:
            return
        session = HTMLSession()
        cat = session.get(self.datasheet_url).content

        self.datasheet = BytesIO(cat)
        self._datasheetdata = cat

    def parse_kuka_datasheet(self):
        with pdfplumber.open(self.datasheet) as temp:
            _page = temp.pages[0]
            ds = _page.extract_text().strip()
            model = ds.splitlines()[0]
            w = re.search(r"Weight approx. (\d+) kg", ds, flags=re.M | re.S | re.IGNORECASE)
            f = re.search(r"Footprint (\d+) mm x (\d+) mm", ds, flags=re.M | re.S | re.IGNORECASE)
            m = re.search(r"Maximum payload (\d+\.?\d*) kg", ds, flags=re.M | re.S | re.IGNORECASE)

            return model, w.groups()[0], f.groups(), m.groups()[0]

    def save_to_disk(self):
        with open("DL/{}.pdf".format(self.model), 'wb') as file:
            file.write(self.datasheet)

        with open("KUKA_Lib/DL/{}.html".format(self.model), 'w') as f:
            f.write(self.html_data)

    def parse_html(self, _html):
        cat_soup = BeautifulSoup(_html, 'html.parser')
        title = cat_soup.find('title').contents[0]
        kk = cat_soup.find_all('table')
        kh = kk[0].find('thead')
        kb = kk[0].find('tbody')

        models = [m.find('strong').contents for m in kh.find_all('th')]

        # cols = kb.find_all('tr')
        for col in kb.find_all('tr'):
            spec = [val.find('div').contents for val in col.find_all('td')]
            models = [m + s for m, s in zip(models, spec)]

        models[0] += ['Weight', 'Footprint', 'Max Payload']

        return title, models

    def save_csv(self, title, models):
        with open("{}.csv".format(title), 'w') as file:
            for m in models[1:]:
                file.write("{},{},{},{},{},{},{},KUKA\n".format(
                    *re.search(r"(KR \d*) (\w.*)", m[0]).groups(),
                    float(re.search(r"(\d+\.?\d*)\xa0.*", m[2]).group(1)) / 1000,
                    float(re.search(r"(\d+\.?\d*)\xa0.*", m[1]).group(1)),
                    float(m[-4]),
                    float(m[-3]),
                    float(m[-2])))
