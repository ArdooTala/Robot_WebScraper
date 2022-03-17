import pathlib
from io import BytesIO
import random
import pdfplumber
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import re


class KukaParser:
    def __init__(self, cat, model, pdf=None):
        # self.url = _url

        self.manufacturer = 'KUKA'
        self.category = cat
        self.model = model
        self.payload = 0
        self.weight = 0
        self.footprint = (0, 0)
        self.payload_max = 0
        self.reach = 0
        self.construction = None
        self.mount = []

        self.html_data = None

        self.datasheet_url = None
        self._datasheetdata = None
        self.datasheet = None
        if pdf:
            self.datasheet = pdf

    def download_pdf(self):
        if not self.datasheet_url:
            return
        print("Downloading > {}".format(self.datasheet_url))
        session = HTMLSession()
        cat = session.get(self.datasheet_url).content

        self.datasheet = BytesIO(cat)
        self._datasheetdata = cat

    def parse_kuka_datasheet(self):
        try:
            with pdfplumber.open(self.datasheet) as temp:
                _page = temp.pages[0]
                ds = _page.extract_text().strip()
                model = ds.splitlines()[0]
                w = re.search(r"Weight approx. (\d+) kg", ds, flags=re.M | re.S | re.IGNORECASE)
                f = re.search(r"Footprint (\d+) mm x (\d+) mm", ds, flags=re.M | re.S | re.IGNORECASE)
                m = re.search(r"Maximum payload (\d+\.?\d*) kg", ds, flags=re.M | re.S | re.IGNORECASE)

                self.model = model
                self.weight = float(w.groups()[0])
                self.footprint = f.groups()
                self.footprint = (float(self.footprint[0]), float(self.footprint[1]))
                self.payload_max = float(m.groups()[0])
        except:
            print("Could not read pdf file . . .")
            return None
        return model, w.groups()[0], f.groups(), m.groups()[0]

    def save_to_disk(self, path: pathlib.Path):
        if not path.exists():
            path.mkdir(exist_ok=True, parents=True)

        with open(path / "{}.pdf".format(self.model), 'wb') as file:
            file.write(self._datasheetdata)

        # with open(path / "{}.html".format(self.model), 'w') as f:
        #     f.write(self.html_data)

    def __repr__(self):
        desc = '''
        KUKA [{}]
        {}
            > payload:  {}
            >   reach:  {}
            >  weight:  {}
        \n\n'''.format(
            self.category,
            self.model,
            self.payload,
            self.reach,
            self.weight)
        return desc
