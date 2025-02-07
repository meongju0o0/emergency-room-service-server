from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Index, Date
from sqlalchemy.sql import text
import pandas as pd
from datetime import datetime

DATABASE_URL = "postgresql://postgres:password@localhost:5432/ERSI"


def create_database_engine(database_url):
    """데이터베이스 엔진 생성."""
    return create_engine(database_url)


def define_tables(metadata):
    """테이블 정의."""
    user_drug_table = Table(
        'user_drug', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('user_id', Integer, nullable=False),
        Column('item_seq', String, nullable=False)
    )

    drug_info_table = Table(
        'drug_info', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('entp_name', String),
        Column('item_name', String),
        Column('item_seq', String, nullable=False, unique=True),
        Column('efcy_qesitm', String),
        Column('use_method_qesitm', String),
        Column('atpn_warn_qesitm', String),
        Column('atpn_qesitm', String),
        Column('intrc_qesitm', String),
        Column('se_qesitm', String),
        Column('deposit_method_qesitm', String),
        Column('open_de', Date),
        Column('update_de', Date),
    )
    Index('idx_item_seq', drug_info_table.c.item_seq)
    return drug_info_table, user_drug_table


def create_or_clear_table(engine, metadata, tables):
    """테이블 생성 또는 데이터 초기화."""
    with engine.connect() as conn:
        for table in tables:
            if not engine.dialect.has_table(conn, table.name):
                print(f"Creating '{table.name}' table...")
                metadata.create_all(engine)
            else:
                print(f"Clearing existing data in '{table.name}' table...")
                conn.execute(text(f'TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE;'))
                conn.execute(table.delete())
                conn.commit()


def convert_to_date(date_str):
    """문자열을 datetime.date로 변환."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def load_and_prepare_data(csv_file_path, encoding="utf-8"):
    """CSV 파일 읽기 및 데이터 준비."""
    df = pd.read_csv(csv_file_path, encoding=encoding)
    
    # 컬럼 이름 매핑
    df.rename(columns={
        'entpName': 'entp_name',
        'itemName': 'item_name',
        'itemSeq': 'item_seq',
        'efcyQesitm': 'efcy_qesitm',
        'useMethodQesitm': 'use_method_qesitm',
        'atpnWarnQesitm': 'atpn_warn_qesitm',
        'atpnQesitm': 'atpn_qesitm',
        'intrcQesitm': 'intrc_qesitm',
        'seQesitm': 'se_qesitm',
        'depositMethodQesitm': 'deposit_method_qesitm',
        'openDe': 'open_de',
        'updateDe': 'update_de'
    }, inplace=True)

    # item_seq가 없는 데이터 제거
    df = df[df['item_seq'].notnull()]

    # open_de와 update_de를 datetime.date로 변환
    df['open_de'] = df['open_de'].apply(convert_to_date)
    df['update_de'] = df['update_de'].apply(convert_to_date)

    # NaN 값을 None으로 변환
    df = df.where(pd.notnull(df), None)

    return df.to_dict(orient='records')


def insert_data(engine, table, data):
    """데이터 삽입."""
    with engine.connect() as conn:
        conn.execute(table.insert(), data)
        conn.commit()
        print(f"Data successfully inserted into the `{table.name}` table.")


if __name__ == "__main__":
    # 설정
    database_url = DATABASE_URL
    csv_file_path = "../data_sources/drug_data.csv"
    metadata = MetaData()

    # 데이터베이스 엔진 생성 및 테이블 정의
    engine = create_database_engine(database_url)
    drug_info_table, user_drug_table = define_tables(metadata)

    # 테이블 생성 또는 초기화
    create_or_clear_table(engine, metadata, [drug_info_table])

    # 데이터 준비
    data_to_insert = load_and_prepare_data(csv_file_path)

    # 데이터 삽입
    insert_data(engine, drug_info_table, data_to_insert)
