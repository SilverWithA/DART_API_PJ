# 데이터베이스 조작에 관한 컨트롤
import pandas as pd
from utils.common_helper import db_utils as ut, db_utils
from app.model.DataImporter import DataImporter

class DatabaseController:
    def __init__(self):
        self.engine = None
        self.db_importer = DataImporter()

    def 보도자료_최종데이터_저장하기(self,tbl_nm, file_nm, data_sheet, schema_sheet):

        self.engine = ut.connect_mysql_db('reported_data')

        # 스키마 데이터 불러오기
        schema_df = pd.read_excel(f'{file_nm}.xlsx', sheet_name=schema_sheet, dtype=str)

        # 테이블 스키마 생성
        try:
            self.db_importer.테이블_스키마_생성기(self.engine,tbl_nm,schema_df)
        except Exception as e:
            pass

        # 스키마 생성 확인
        self.db_importer.테이블_스키마_확인하기(self.engine,tbl_nm)

        # 추가할 데이터 불러오기
        df = pd.read_excel(f'{file_nm}.xlsx',sheet_name=data_sheet, dtype=str)

        # 데이터 추가
        self.db_importer.빈테이블에_데이터추가(self.engine, df, tbl_nm)

        # 추가된 데이터 테스트 확인
        ut.테이블_테스트_조회(self.engine,tbl_nm)

