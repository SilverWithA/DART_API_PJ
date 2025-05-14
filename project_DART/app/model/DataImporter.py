# 데이터베이스에 데이터를 넣기 위한 기능

from sqlalchemy import text

class DataImporter():
    def __init__(self):
        pass

    def 테이블_스키마_생성기(self, engine, tbl_nm, schema_df):
        """미리 스키마가 지정된 df를 기반으로 creart table문을 수행하는 매서드"""


        # CREATE TABLE sql문 생성
        columns_sql = ",\n    ".join([
            f"{row['컬럼명']} {row['컬럼 타입']}" for _, row in schema_df.iterrows()
        ])

        create_table_sql = f'CREATE TABLE {tbl_nm} ({columns_sql})'

        # 생성한 sql문 실행 후 commit
        with engine.connect() as con:
            con.execute(text(create_table_sql))
            con.commit()
        print(f"{tbl_nm} 테이블 스키마 커밋 완료 ---")


    def 테이블_스키마_확인하기(self,engine, tbl_nm):
        with engine.connect() as con:
            sql = f"SHOW COLUMNS FROM {tbl_nm};"
            res = con.execute(text(sql))
        print(res.all())

    def 빈테이블에_데이터추가(self, engine,df, tbl_nm):
        # 미리 스키마에 대해 정의한 df를 import
        df.to_sql(str(tbl_nm), engine, if_exists='append', index=False)
        print(f"{tbl_nm}에 데이터를 추가하였습니다.")
