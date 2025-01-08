import requests
import pandas as pd
import xml.etree.ElementTree as ET
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed

# API 기본 URL과 파라미터 설정
BASE_URL = 'http://apis.data.go.kr/B551182/hospInfoServicev2/getHospBasisList'
SERVICE_KEY = 'WJZdHnwQayOaAgkoEMZlx2fuBYM1lbBRXnt1XAB2mq3cqm59UBP322b6c1+U9Zq2gzY/UQRQI85D5NAkTR2F6w=='


def parse_xml_to_dict(xml_content):
    """XML 데이터를 파싱하여 딕셔너리 리스트로 변환."""
    root = ET.fromstring(xml_content)
    items = root.find('.//items')
    data_list = []

    if items is not None:
        for item in items:
            data = {}
            for child in item:
                data[child.tag] = child.text
            data_list.append(data)

    return data_list


def fetch_page_data(page_no, num_of_rows=100):
    """단일 페이지 데이터를 가져오는 함수."""
    params = {
        'serviceKey': SERVICE_KEY,
        'numOfRows': num_of_rows,
        'pageNo': page_no
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return parse_xml_to_dict(response.content)
    else:
        print(f"Error fetching page {page_no}: {response.status_code}\n", end='')
        return []


def fetch_data_in_process(page_ranges):
    """프로세스에서 데이터를 비동기로 가져오는 함수."""
    all_data = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_page = {executor.submit(fetch_page_data, page_no): page_no for page_no in page_ranges}
        for future in as_completed(future_to_page):
            page_no = future_to_page[future]
            try:
                data = future.result()
                if data:
                    all_data.extend(data)
                print(f"Page {page_no} fetched successfully by process.\n", end='')
            except Exception as e:
                print(f"Error fetching page {page_no}: {e}\n", end='')
    return all_data


def parse_data(all_data):
    """데이터를 DataFrame으로 변환하고 저장 가능한 형태로 가공."""
    df = pd.DataFrame(all_data)

    # 표시할 컬럼 정의
    columns_to_display = [
        'addr',         # 병원 주소
        'clCd',         # 병원 분류 코드
        'clCdNm',       # 병원 분류 코드명
        'hospUrl',      # 병원 URL
        'mdeptIntnCnt', # 인턴 수
        'mdeptResdCnt', # 레지던트 수
        'mdeptSdrCnt',  # 전문의 수
        'pnursCnt',     # 간호사 수
        'postNo',       # 우편번호
        'telno',        # 전화번호
        'yadmNm',       # 요양기관명
        'XPos',         # 병원 X좌표
        'YPos',         # 병원 Y좌표
    ]

    # 누락된 컬럼을 기본값으로 추가
    for col in columns_to_display:
        if col not in df.columns:
            df[col] = 'N/A'

    # 선택한 컬럼만 표시
    df = df[columns_to_display]

    # NaN 값을 보기 쉽게 변경
    df.fillna('N/A', inplace=True)

    return df


if __name__ == '__main__':
    # 첫 번째 요청으로 전체 페이지 수를 가져옴
    response = requests.get(BASE_URL, params={
        'serviceKey': SERVICE_KEY,
        'numOfRows': 1,
        'pageNo': 1
    })

    if response.status_code == 200:
        total_count = ET.fromstring(response.content).find('.//totalCount').text
        total_count = int(total_count)
        total_pages = (total_count // 100) + (1 if total_count % 100 > 0 else 0)

        print(f"Total items: {total_count}, Total pages: {total_pages}\n", end='')

        # 프로세스당 페이지 분배
        num_processes = cpu_count()
        pages_per_process = total_pages // num_processes
        page_ranges = [
            range(i * pages_per_process + 1, (i + 1) * pages_per_process + 1) for i in range(num_processes)
        ]
        # 나머지 페이지 처리
        if total_pages % num_processes:
            page_ranges[-1] = range(page_ranges[-1].start, total_pages + 1)

        # 멀티프로세싱으로 모든 데이터 가져오기
        with Pool(num_processes) as pool:
            all_results = pool.map(fetch_data_in_process, page_ranges)

        # 데이터 병합
        all_data = [item for sublist in all_results for item in sublist]

        # 데이터 가공 및 저장
        if all_data:
            df = parse_data(all_data)
            df.to_csv('../data_sources/hospital_data.csv', index=False, encoding='utf-8-sig')
            print("Data saved to '../data_sources/hospital_data.csv'.\n", end='')
        else:
            print("No data fetched.\n", end='')
    else:
        print(f"Failed to fetch total count: {response.status_code}\n", end='')
