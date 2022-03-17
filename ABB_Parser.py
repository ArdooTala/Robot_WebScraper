import random
import pathlib
import warnings
from io import BytesIO
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import re
import pdfplumber


def kir(_p):
    with open(_p, 'rb') as f:
        cat_soup = BeautifulSoup(f, 'html.parser')
        kk = cat_soup.find_all('a')
        for k in kk:
            if i_tag := k.find('i'):
                if 'file' in i_tag.contents[0]:
                    print(_url := k.get('href'))
                    session = HTMLSession()
                    cat = session.get(_url).content
                    mem_pdf = BytesIO(cat)
                    with pdfplumber.open(mem_pdf) as temp:
                        _page = temp.pages[0]
                        cover = _page.extract_text()
                        m = re.search(r"ROBOTICS\w*\n(IRB \d{3,4})", cover)
                        if m:
                            model = m.groups()[0]
                            print(model)
                        else:
                            model = "Unknown" + str(random.randint(0, 100))

                        with open("DL/{}.pdf".format(model), 'wb') as file:
                            file.write(cat)


def extract_info(pdf):
    with pdfplumber.open(pdf) as temp:
        _page = temp.pages[1]
        h1_page = _page.crop((_page.bbox[0], _page.bbox[1], _page.bbox[2] / 2 + 50, _page.bbox[3] - 100), relative=True)
        data = h1_page.extract_text()

        h2_page = _page.crop((_page.bbox[2] / 2 + 50, _page.bbox[1], _page.bbox[2], _page.bbox[3] - 100), relative=True)
        data += h2_page.extract_text()

        return data


def read_specs(sec):
    data_dic = {}

    res = re.findall(r"(IRB \d{3,4})-?(\S*)?\s*(\d*\.?\d*)\s*(\d*)", sec)
    for m, t, r, p in res:
        if r and float(r) > 10:
            r = float(r) / 1000
        data_dic.setdefault((m, t), {"Spec": (r, p)})
        print("IRB {} [{}] >> {}".format(m, t, (r, p)))

    return data_dic


def read_technical(sec):
    phys_data = re.search(r"(^Physical.*)(?=^Environment)", sec, flags=re.M | re.S).group(0)

    base_dim = None
    base_data = re.search(r"(Robot base)\s+(\d+.?\d*)\s?x\s?(\d+.?\d*)\s?mm.*(?=^Robot weight)", phys_data,
                          flags=re.M | re.S | re.IGNORECASE)
    if base_data:
        base_dim = base_data.groups()
        print("{}: {} x {} mm".format(base_dim[0], base_dim[1], base_dim[2]))

    weight_data = re.search(r"(weight.*)", phys_data, flags=re.M | re.S | re.IGNORECASE)
    if not weight_data:
        return None, base_dim
    weights = re.findall(r"(?:(IRB \d{3,4})-?(\S*)?)?\s*(\d+\.?\d*)\s?kg", weight_data.group(0), flags=re.M)
    if not weights:
        return None, base_dim
    for w in weights:
        print(w)
    return weights, base_dim


def extract_vals(data):
    secs = re.split(r"—\n", data, flags=re.M)
    data_dic = {}

    for sec in secs:
        if not sec:
            continue
        if not (tit := re.search(r"\w+", sec)):
            continue
        sec_tit = tit.group(0)
        print(sec_tit.center(100, '='))

        if "Specification" in tit.group(0):
            print(sec)
            print("-"*100)
            data_dic = read_specs(sec)

            print("\t>> ", data_dic)

        if "Technical" in tit.group(0):
            print(sec)
            print("-" * 100)
            weights, base_dims = read_technical(sec)
            if weights:
                for t in weights:
                    if not t[0]:
                        for m in data_dic.keys():
                            data_dic[m]['weight'] = t[2]
                        break
                    data_dic[(t[0], t[1])]['weight'] = t[2]

            if base_dims:
                for m in data_dic.keys():
                    data_dic[m]['base'] = base_dims[1:]

            print("\t>> ", data_dic)

    print(data_dic)
    return data_dic


def parse_all(_p):
    all_data = {}
    path = pathlib.Path(_p)
    with open("ABB.csv", 'w') as csv_file:
        csv_file.write("Model,Type,Reach,Payload,Weight,Base_X,Base_Y\n")
        for file in path.glob("IRB *.pdf"):
            print(str(file).center(100, '='))
            data = extract_vals(extract_info(file))
            if not data:
                continue

            all_data.update(data)
            for d in data.items():
                print(d[0])
                print(d[1])
                csv_file.write(
                    "{},{},{},{},{},{},{}\n".format(*d[0],
                                              *d[1].get('Spec', ('', '')),
                                              d[1].get('weight', ''),
                                              *d[1].get('base', ('', ''))))
