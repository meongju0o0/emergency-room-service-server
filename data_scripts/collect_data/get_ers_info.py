import requests
import json
import pandas as pd
import xml.etree.ElementTree as ET


API_KEY = "WJZdHnwQayOaAgkoEMZlx2fuBYM1lbBRXnt1XAB2mq3cqm59UBP322b6c1+U9Zq2gzY/UQRQI85D5NAkTR2F6w=="
BASE_URL = "http://apis.data.go.kr/B552657/ErmctInfoInqireService/getSrsillDissAceptncPosblInfoInqire"


def fetch_emergency_hospital_data(stage1, stage2):
    """응급실 데이터를 요청하는 함수."""
    params = {
        "serviceKey": API_KEY,
        "STAGE1": stage1,
        "STAGE2": stage2,
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


def save_to_csv(data, file_path):
    """데이터를 CSV 파일로 저장"""
    df = pd.DataFrame(data)

    if "region" in df.columns:
        other_columns = [col for col in df.columns if col != "region"]
        df = df[["region"] + other_columns]

    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"Data saved to {file_path}")


if __name__ == "__main__":
    with open("../data_sources/regions_data.json", "r", encoding="utf-8") as json_file:
        regions = json.load(json_file)

    all_data = []

    print("Fetching emergency hospital data...")
    try:
        for stage1, stage2_list in regions.items():
            for stage2 in stage2_list:
                try:
                    print(f"Fetching data for {stage1} - {stage2}...")
                    xml_data = fetch_emergency_hospital_data(stage1, stage2)
                    items = parse_xml_to_dict(xml_data)
                    for item in items:
                        item["region"] = f"{stage1} {stage2}"
                    if items:
                        all_data.extend(items)
                except Exception as e:
                    print(f"Error fetching data for {stage1} - {stage2}: {e}")
    except Exception as e:
        print(f"Error: {e}")

    save_to_csv(all_data, "../data_sources/ers_data.csv")
