import pandas as pd
from app.model import Info_collecter
from app.view import Info_UI


class Company_info_finder():
    def __init__(self):
        self.xml_updater = Info_collecter.recent_overview_updater()
        self.xml_model = Info_collecter.xml_info_finder()
        self.api_model = Info_collecter.API_info_finder()
        self.view = Info_UI.Info_view()

    def 회사명_데이터_불러오기(self, file_name, sheet_name):

        # 원본 데이터 불러오기
        raw_df = pd.read_excel(f'{str(file_name)}.xlsx', sheet_name=str(sheet_name),dtype=str)
        return raw_df

    def 회사명으로_고유번호_불러오기(self, df):

        print("df의 모든 컬럼명은 다음과 같습니다. -----------------------")
        print(df.columns)
        input_col = input("* 다음 컬럼 중 검색에 사용할 회사명 컬럼을 선택해주세요(다트기준 회사명 추천): ")

        res_df = self.xml_model.apply_get_corpcode_by_name(df,input_col)

        print("총 ", len(res_df['고유번호']), "개의 회사의 고유번호를 매핑 완료! --------")
        print(" - 고유번호 중복 회사: ", len(res_df[res_df[str('고유번호')].apply(lambda x: isinstance(x, list))]), "개")
        print(" - 사명으로 매핑 실패한 회사: ", len(res_df[res_df[str('고유번호')].isna()]), "개")

        return res_df

    def 법인등록번호로_고유번호_유효성검증(self, df):


        compare_col = '검증용 법인코드'
        # 검증용 법인코드 불러오기
        jurir_df = self.api_model.apply_jurir_no(df = df, output_col=compare_col)

        # 불러온 법인코드와 기존 법인코드 비교
        jurir_df = self.api_model.check_corpcode_vaild(df, '법인등록번호', compare_col)

        return jurir_df

    def 고유번호로_종목코드_불러오기(self, df):

        res_df = self.xml_model.apply_stockcode_by_corpcode(df)
        # print("총 ", len(res_df['고유번호']), "개의 고유번호로 종목코드 ", len(res_df['종목코드']),"개 매핑 완료!")
        return res_df

    def 사업보고서제출여부_확인(self,df):


        self.view.print_start_UI("사업보고서 제출여부 확인")

        # 고유번호 없는 회사는 검색하지 않음
        not_null_df = df[~df['고유번호'].isnull()]

        # 고유번호에 대해 사업보고서 조회
        report_list = self.api_model.공시보고서_접수번호목록_가져오기(list(not_null_df['고유번호']),'20250101','20250508','A','A001')

        # 사업보고서 제출하는 회사 고유번호 리스트
        reported_corpcode = self.api_model.get_unique_column_values(report_list, 'corp_code')

        # 사업보고서 제출 여부 확인
        df['사업보고서 제출여부'] = df['고유번호'].isin(reported_corpcode)

        self.view.print_end_UI("사업보고서 제출여부 확인")
        return df


    def tmp_데이터베이스_업로더(self,df):
        self.xml_updater.__update_overview_table__('group2025_info',df)