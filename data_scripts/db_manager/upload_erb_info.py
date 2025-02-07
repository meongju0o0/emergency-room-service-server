import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Text, Index
from sqlalchemy.engine import Engine

DATABASE_URL = "postgresql://postgres:password@localhost:5432/ERSI"


def create_database_engine(database_url: str) -> Engine:
    """데이터베이스 엔진 생성"""
    return create_engine(database_url)


def define_tables_from_csv(metadata: MetaData, csv_file_path: str) -> Table:
    """CSV 파일에서 컬럼 이름을 읽어 테이블 정의"""
    df = pd.read_csv(csv_file_path, nrows=0)
    csv_columns = df.columns.tolist()

    columns = [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('uploaded_at', DateTime, index=True),
    ]

    for col in csv_columns:
        columns.append(Column(col, String(255)))

    table = Table('erb_info', metadata, *columns)

    if 'hpid' in csv_columns:
        Index('idx_erb_hpid', table.c.hpid)

    return table


def create_or_update_table(engine: Engine, metadata: MetaData):
    """테이블 생성 또는 업데이트"""
    metadata.create_all(engine, checkfirst=True)


def load_and_prepare_data(csv_file_path: str, encoding="utf-8") -> pd.DataFrame:
    """CSV 파일 로드 및 데이터 준비"""
    df = pd.read_csv(csv_file_path, encoding=encoding, dtype=str)
    df = df.fillna('').astype(str)
    df['uploaded_at'] = datetime.now()
    return df


def insert_data(engine: Engine, table: Table, df: pd.DataFrame):
    """데이터 삽입"""
    dtype = {col.name: Text for col in table.columns if isinstance(col.type, Text)}
    df.to_sql(
        name=table.name,
        con=engine,
        if_exists='append',
        index=False,
        dtype=dtype
    )
    print(f"Data successfully inserted into the `{table.name}` table.")


if __name__ == "__main__":
    engine = create_database_engine(DATABASE_URL)
    metadata = MetaData()
    csv_file_path = "../data_sources/erb_data.csv"

    erb_info_table = define_tables_from_csv(metadata, csv_file_path)

    create_or_update_table(engine, metadata)

    df_prepared = load_and_prepare_data(csv_file_path)
    insert_data(engine, erb_info_table, df_prepared)
