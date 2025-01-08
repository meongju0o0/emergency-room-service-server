import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# API 기본 URL과 파라미터 설정
BASE_URL = 'http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList'
SERVICE_KEY = 'WJZdHnwQayOaAgkoEMZlx2fuBYM1lbBRXnt1XAB2mq3cqm59UBP322b6c1+U9Zq2gzY/UQRQI85D5NAkTR2F6w=='


def fetch_page_data(page_no, num_of_rows=100):
    """단일 페이지 데이터를 가져오는 함수."""
    params = {
        'serviceKey': SERVICE_KEY,
        'type': 'json',
        'numOfRows': num_of_rows,
        'pageNo': page_no
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        items = data.get('body', {}).get('items', [])
        return items
    else:
        print(f"Error fetching page {page_no}: {response.status_code}")
        return []


def fetch_all_drug_data_concurrently(total_pages, num_of_rows=100):
    """멀티스레딩을 이용하여 모든 데이터를 가져오는 함수."""
    all_data = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        # 각 페이지 요청을 스레드로 실행
        future_to_page = {executor.submit(fetch_page_data, page_no, num_of_rows): page_no for page_no in range(1, total_pages + 1)}

        for future in as_completed(future_to_page):
            page_no = future_to_page[future]
            try:
                data = future.result()
                if data:
                    all_data.extend(data)
                print(f"Page {page_no} fetched successfully.")
            except Exception as e:
                print(f"Error fetching page {page_no}: {e}")

    return all_data


def parse_data(all_data):
    """데이터를 DataFrame으로 변환하고 저장 가능한 형태로 가공."""
    df = pd.DataFrame(all_data)

    columns_to_display = [
        'entpName',          # 제조업체명
        'itemName',          # 제품명
        'itemSeq',           # 제품 일련번호
        'efcyQesitm',        # 효능
        'useMethodQesitm',   # 사용법
        'atpnWarnQesitm',    # 주의사항 경고
        'atpnQesitm',        # 주의사항
        'intrcQesitm',       # 상호작용
        'seQesitm',          # 부작용
        'depositMethodQesitm', # 보관 방법
        'openDe',            # 공개 날짜
        'updateDe'           # 수정 날짜
    ]

    df = df[columns_to_display]
    df.fillna('N/A', inplace=True)
    return df


if __name__ == '__main__':
    # 첫 번째 요청으로 전체 페이지 수를 가져옴
    response = requests.get(BASE_URL, params={
        'serviceKey': SERVICE_KEY,
        'type': 'json',
        'numOfRows': 1,
        'pageNo': 1
    })

    if response.status_code == 200:
        total_count = response.json().get('body', {}).get('totalCount', 0)
        total_pages = (total_count // 100) + (1 if total_count % 100 > 0 else 0)

        print(f"Total items: {total_count}, Total pages: {total_pages}")

        # 멀티스레딩으로 모든 데이터 가져오기
        all_data = fetch_all_drug_data_concurrently(total_pages)

        # 데이터 가공 및 저장
        if all_data:
            df = parse_data(all_data)
            df.to_csv('../data_sources/drug_data.csv', index=False, encoding='utf-8-sig')
            print("Data saved to '../data_sources/drug_data.csv'.")
        else:
            print("No data fetched.")
    else:
        print(f"Failed to fetch total count: {response.status_code}")
