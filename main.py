import ABB_Parser
import Kuka_Parser
from src.kukaparser import KukaParser
import pathlib


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
        "https://www.kuka.com/en-ca/products/robotics-systems/industrial-robots/kr-600-fortec",
        "https://www.kuka.com/en-ca/products/robotics-systems/industrial-robots/kr-1000-titan"
    ]

    for link in links:
        print(link)
        Kuka_Parser.data_from_url(link)

        exit(0)

    path = pathlib.Path("./")
    with open("KUKA.csv", 'w') as kuk:
        for f in path.glob("KR*.csv"):
            with open(f, 'r') as k:
                kuk.write(k.read())
