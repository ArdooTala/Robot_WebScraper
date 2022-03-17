import unicodedata
import ABB_Parser
import Kuka_Scraper
from kukaparser import KukaParser
import pathlib
from bs4 import BeautifulSoup


if __name__ == '__main__':
    # ABB_Parser.kir('ABB_Lib/ABB Library - Articulated Robots.html')
    # ABB_Parser.parse_all('DL')
    links = [
        "https://www.kuka.com/en-ca/products/robotics-systems/industrial-robots/kr-4-agilus",
        "https://www.kuka.com/en-ca/products/robotics-systems/industrial-robots/kr-agilus",
        "https://www.kuka.com/en-ca/products/robotics-systems/industrial-robots/kr-cybertech-nano",
        "https://www.kuka.com/en-ca/products/robotics-systems/industrial-robots/kr-cybertech",
        "https://www.kuka.com/en-ca/products/robotics-systems/industrial-robots/kr-iontec",
        "https://www.kuka.com/en-ca/products/robotics-systems/industrial-robots/kr-quantec",
        "https://www.kuka.com/en-ca/products/robotics-systems/industrial-robots/kr-quantec-nano",
        "https://www.kuka.com/en-ca/products/robotics-systems/industrial-robots/kr-quantec-press",
        "https://www.kuka.com/en-ca/products/robotics-systems/industrial-robots/kr-360-fortec",
        "https://www.kuka.com/en-ca/products/robotics-systems/industrial-robots/kr-500-fortec",
        "https://www.kuka.com/en-ca/products/robotics-systems/industrial-robots/kr-600-fortec"
    ]

    save_path = pathlib.Path('../KUKA_Lib')

    for link in links:
        category, models = Kuka_Scraper.data_from_url(link)

        robots = []
        print(link)
        print("HTML data".center(100, '='))
        print(models[0])
        for model in models[1:]:
            print('-'*100)
            print(model)
            rob = KukaParser(category, model[0])
            rob.payload = unicodedata.normalize("NFKD", model[1])
            rob.reach = unicodedata.normalize("NFKD", model[2])
            rob.construction = model[3]
            rob.mount = model[5].split(',')
            rob.datasheet_url = model[-2].get('href')

            rob.download_pdf()
            rob.parse_kuka_datasheet()

            robots.append(rob)

            print(rob)
            rob.save_to_disk(save_path / rob.category / rob.model)

        Kuka_Scraper.save_csv(save_path / category, robots)

    exit(0)
    print("This should not happen")

    path = pathlib.Path("../")
    with open("KUKA.csv", 'w') as kuk:
        for f in path.glob("KR*.csv"):
            with open(f, 'r') as k:
                kuk.write(k.read())
