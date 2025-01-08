from sqlalchemy import create_engine, Table, Column, Index, Integer, String, MetaData
from geoalchemy2 import Geometry
from sqlalchemy.sql import text
import pandas as pd

DATABASE_URL = "postgresql://postgres:apdpfhd3!@localhost:5432/ERSI"


def create_database_engine(database_url):
    """데이터베이스 엔진 생성."""
    return create_engine(database_url)


def define_tables(metadata):
    """테이블 정의."""
    hospital_info_table = Table(
        'hospital_info', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('addr', String),
        Column('cl_cd', String),
        Column('cl_cd_nm', String),
        Column('hosp_url', String),
        Column('mdept_intn_cnt', Integer),
        Column('mdept_resd_cnt', Integer),
        Column('mdept_sdr_cnt', Integer),
        Column('pnurs_cnt', Integer),
        Column('post_no', String),
        Column('tel_no', String),
        Column('yadm_nm', String),
        Column('geom', Geometry('POINT', srid=4326)),
    )
    Index('idx_geom', text("geom"), postgresql_using='gist')
    return hospital_info_table


def recreate_table(engine, metadata, table):
    """기존 테이블 삭제 및 재생성."""
    with engine.begin() as conn:
        if engine.dialect.has_table(conn, table.name):
            print(f"Dropping existing table '{table.name}'...")
            conn.execute(text(f"DROP TABLE IF EXISTS {table.name} CASCADE"))
            conn.commit()
        print(f"Creating table '{table.name}'...")
        metadata.create_all(engine)


def load_and_prepare_data(csv_file_path, encoding="utf-8"):
    """CSV 파일 읽기 및 데이터 준비."""
    df = pd.read_csv(csv_file_path, encoding=encoding)

    # 컬럼 이름 매핑
    df.rename(columns={
        'addr': 'addr',
        'clCd': 'cl_cd',
        'clCdNm': 'cl_cd_nm',
        'hospUrl': 'hosp_url',
        'mdeptIntnCnt': 'mdept_intn_cnt',
        'mdeptResdCnt': 'mdept_resd_cnt',
        'mdeptSdrCnt': 'mdept_sdr_cnt',
        'pnursCnt': 'pnurs_cnt',
        'postNo': 'post_no',
        'telno': 'tel_no',
        'yadmNm': 'yadm_nm',
        'XPos': 'x_pos',
        'YPos': 'y_pos',
    }, inplace=True)

    # NaN 값을 None으로 변환
    df = df.where(pd.notnull(df), None)

    # 정수가 아닌 값을 None으로 변환하는 함수
    def to_valid_integer(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    # 정수형 컬럼에 적용
    int_columns = ['mdept_intn_cnt', 'mdept_resd_cnt', 'mdept_sdr_cnt', 'pnurs_cnt', 'post_no', 'cl_cd']
    for column in int_columns:
        df[column] = df[column].apply(to_valid_integer)

    # POINT 형식의 geom 컬럼 생성
    df['geom'] = df.apply(
        lambda row: f"POINT({row['x_pos']} {row['y_pos']})" if row['x_pos'] and row['y_pos'] else None, axis=1
    )

    return df.to_dict(orient='records')


def insert_data(engine, table, data):
    """데이터 삽입."""
    with engine.connect() as conn:
        for row in data:
            geom = row.pop('geom')
            row.pop('x_pos', None)
            row.pop('y_pos', None)
            conn.execute(
                table.insert().values(**row, geom=text(f"ST_GeomFromText('{geom}', 4326)"))
            )
        conn.commit()
        print(f"Data successfully inserted into the `{table.name}` table.")


if __name__ == "__main__":
    # 설정
    database_url = DATABASE_URL
    csv_file_path = "../data_sources/hospital_data.csv"

    # 데이터베이스 엔진 생성
    engine = create_database_engine(database_url)

    # 메타데이터 및 테이블 정의
    metadata = MetaData()
    hospital_info_table = define_tables(metadata)

    # 테이블 삭제 및 재생성
    recreate_table(engine, metadata, hospital_info_table)

    # 데이터 준비
    data_to_insert = load_and_prepare_data(csv_file_path)

    # 데이터 삽입
    insert_data(engine, hospital_info_table, data_to_insert)
