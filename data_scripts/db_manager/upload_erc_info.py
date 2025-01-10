import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Index
from geoalchemy2 import Geometry
from sqlalchemy.engine import Engine
from sqlalchemy.sql import text

DATABASE_URL = "postgresql://postgres:apdpfhd3!@localhost:5432/ERSI"


def create_database_engine(database_url: str) -> Engine:
    """데이터베이스 엔진 생성"""
    return create_engine(database_url)


def define_tables_from_csv(metadata: MetaData, csv_file_path: str) -> Table:
    """CSV 파일에서 컬럼 이름을 읽어 테이블 정의"""
    df = pd.read_csv(csv_file_path, nrows=0)
    csv_columns = df.columns.tolist()

    columns = [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('geom', Geometry('POINT', srid=4326), index=True)
    ]

    for col in csv_columns:
        if col not in ['wgs84Lat', 'wgs84Lon']:
            columns.append(Column(col, Text if col in ['dgidIdName', 'dutyMapimg', 'dutyInf'] else String(255)))

    table = Table('erc_info', metadata, *columns)

    if 'hpid' in csv_columns:
        Index('idx_erc_hpid', table.c.hpid)

    return table


def reset_table(engine: Engine, table_name: str):
    """기존 테이블이 존재하면 모든 데이터를 삭제하고 id를 1로 초기화"""
    with engine.connect() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"))
        print(f"Table `{table_name}` has been reset.")


def create_or_update_table(engine: Engine, metadata: MetaData):
    """테이블 생성 또는 업데이트"""
    metadata.create_all(engine, checkfirst=True)


def load_and_prepare_data(csv_file_path: str, encoding="utf-8") -> pd.DataFrame:
    """CSV 파일 로드 및 데이터 준비"""
    df = pd.read_csv(csv_file_path, encoding=encoding, dtype=str)

    df['geom'] = df.apply(
        lambda row: f"SRID=4326;POINT({row['wgs84Lon']} {row['wgs84Lat']})" 
        if row['wgs84Lon'] and row['wgs84Lat'] else None, 
        axis=1
    )

    df = df.drop(columns=['wgs84Lat', 'wgs84Lon'])
    df = df.fillna('').astype(str)
    return df


def insert_data(engine: Engine, table: Table, df: pd.DataFrame):
    """데이터 삽입"""
    dtype = {col.name: Text for col in table.columns if isinstance(col.type, Text)}
    dtype['geom'] = Geometry('POINT', srid=4326)
    
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
    csv_file_path = "../data_sources/erc_data.csv"
    table_name = "erc_info"

    erc_info_table = define_tables_from_csv(metadata, csv_file_path)

    create_or_update_table(engine, metadata)

    reset_table(engine, table_name)

    df_prepared = load_and_prepare_data(csv_file_path)
    insert_data(engine, erc_info_table, df_prepared)
