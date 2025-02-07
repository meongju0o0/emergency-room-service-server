from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Index
from sqlalchemy.sql import text
import pandas as pd
import chardet

DATABASE_URL = "postgresql://postgres:password@localhost:5432/ERSI"


def create_database_engine(database_url):
    """데이터베이스 엔진 생성."""
    return create_engine(database_url)


def define_tables(metadata):
    """테이블 정의."""
    user_disease_table = Table(
        'user_disease', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('user_id', Integer, nullable=False),
        Column('code', String, nullable=False)
    )

    disease_info_table = Table(
        'disease_info', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('code', String, nullable=False),
        Column('korean_name', String),
        Column('english_name', String),
        Column('is_complete_code', String),
        Column('is_using_main_code', String),
        Column('infectious_disease', String),
        Column('gender', String),
    )
    Index('idx_code', disease_info_table.c.code)
    return disease_info_table, user_disease_table


def create_or_clear_table(engine, metadata, tables):
    """테이블 생성 또는 데이터 초기화."""
    with engine.connect() as conn:
        for table in tables:
            if not engine.dialect.has_table(conn, table.name):
                print(f"Creating '{table.name}' table...")
                metadata.create_all(engine)
            else:
                print(f"Clearing existing data in '{table.name}' table...")
                conn.execute(table.delete())
                conn.execute(text(f'TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE;'))
                conn.commit()


def load_and_prepare_data(csv_file_path, encoding="utf-8"):
    """CSV 파일 읽기 및 데이터 준비."""
    df = pd.read_csv(csv_file_path, encoding=encoding)

    # 컬럼 이름 매핑
    df.rename(columns={
        '상병기호': 'code',
        '한글명': 'korean_name',
        '영문명': 'english_name',
        '완전코드구분': 'is_complete_code',
        '주상병사용구분': 'is_using_main_code',
        '법정감염병구분': 'infectious_disease',
        '성별구분': 'gender',
    }, inplace=True)

    df = df[df['code'].notnull()]
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
    csv_file_path = "../data_sources/disease_data.csv"
    metadata = MetaData()

    # 데이터베이스 엔진 생성 및 테이블 정의
    engine = create_database_engine(database_url)
    disease_info_table, user_disease_table = define_tables(metadata)

    # 테이블 생성 또는 초기화
    create_or_clear_table(engine, metadata, [disease_info_table])

    # 데이터 준비
    with open('../data_sources/disease_data.csv', 'rb') as f:
        encode_fmt = chardet.detect(f.read())['encoding'].lower()
    data_to_insert = load_and_prepare_data(csv_file_path, encoding=encode_fmt)

    # 데이터 삽입
    insert_data(engine, disease_info_table, data_to_insert)
