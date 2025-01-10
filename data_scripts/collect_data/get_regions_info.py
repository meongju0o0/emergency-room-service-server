import requests
from bs4 import BeautifulSoup
import json

WIKIPEDIA_URL = "https://ko.wikipedia.org/wiki/대한민국의_행정_구역"


def fetch_administrative_regions():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    
    response = requests.get(WIKIPEDIA_URL, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    regions = {}
    
    h3_tags = soup.select('#mw-content-text .mw-parser-output h3')
    for h3_tag in h3_tags:
        sido_name_tag = h3_tag.find("a")
        if not sido_name_tag:
            continue
        sido_name = sido_name_tag.text.strip()
        regions[sido_name] = []
        
        sigungu_list = h3_tag.find_next("ul")
        if sigungu_list:
            sigungu_tags = sigungu_list.find_all("li")
            for sigungu_tag in sigungu_tags:
                sigungu_name = sigungu_tag.text.strip()
                if (sigungu_name.endswith('시') or sigungu_name.endswith('군') or sigungu_name.endswith('구')) and ('\n' not in sigungu_name):
                    regions[sido_name].append(sigungu_name)

    return regions


def save_to_json(data, filename="regions.json"):
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    print("Fetching administrative region data...")
    regions = fetch_administrative_regions()

    save_to_json(regions, "../data_sources/regions_data.json")
    print(f"Data saved to '../data_sources/regions_data.json'")
