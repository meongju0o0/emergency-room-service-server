import requests
import pandas as pd
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = "WJZdHnwQayOaAgkoEMZlx2fuBYM1lbBRXnt1XAB2mq3cqm59UBP322b6c1+U9Zq2gzY/UQRQI85D5NAkTR2F6w=="
BASE_URL = "http://apis.data.go.kr/B552657/ErmctInfoInqireService/getEgytBassInfoInqire"


def fetch_emergency_hospital_data(page_no, num_of_rows):
    """응급실 데이터를 요청하는 함수."""
    params = {
        "serviceKey": API_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.content


def parse_xml_to_dict(xml_data):
    """XML 데이터를 파싱하여 딕셔너리로 변환."""
    root = ET.fromstring(xml_data)
    items = []

    for item in root.findall(".//item"):
        record = {}
        for child in item:
            record[child.tag] = child.text
        items.append(record)

    return items


def get_total_count(xml_data):
    """총 데이터 개수를 가져오는 함수."""
    root = ET.fromstring(xml_data)
    total_count = root.find(".//totalCount")
    return int(total_count.text) if total_count is not None else 0


def save_to_csv(data, file_path):
    """데이터를 CSV 파일로 저장"""
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"Data saved to {file_path}\n", end='')


def fetch_page_data(page_no, total_pages, num_of_rows):
    """특정 페이지 데이터를 가져오는 함수."""
    try:
        print(f"Fetching page {page_no} / {total_pages}...\n", end='')
        xml_data = fetch_emergency_hospital_data(page_no, num_of_rows)
        return parse_xml_to_dict(xml_data)
    except Exception as e:
        print(f"Error fetching page {page_no}: {e}\n", end='')
        return []


if __name__ == "__main__":
    print("Fetching emergency hospital detailed data...\n", end='')
    all_data = []
    num_of_rows = 100

    try:
        first_page_data = fetch_emergency_hospital_data(1, num_of_rows)
        total_count = get_total_count(first_page_data)
        total_pages = (total_count // num_of_rows) + (1 if total_count % num_of_rows > 0 else 0)

        print(f"Total records: {total_count}, Total pages: {total_pages}\n", end='')

        items = parse_xml_to_dict(first_page_data)
        all_data.extend(items)

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(fetch_page_data, page, total_pages, num_of_rows) for page in range(2, total_pages + 1)]

            for future in as_completed(futures):
                result = future.result()
                if result:
                    all_data.extend(result)

        save_to_csv(all_data, "../data_sources/erh_data.csv")
    except Exception as e:
        print(f"Error: {e}")
