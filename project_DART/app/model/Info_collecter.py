# 고유번호, 종목코드, 사업보고서 제출 여부 기본 정보를 크롤링하는 모델
import pandas as pd
from app.view.Info_UI import Info_view
import config
from urllib.request import urlopen
from zipfile import ZipFile
import io
import os
import requests
from sqlalchemy import create_engine
from pandas import isnull


# 최신 기업개황 정보로 업데이트하기 to database
class recent_overview_updater:
    def __init__(self):
        self.api_key = config.api_key
        self.current_dir = os.getcwd()
        self.db_engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(config.db_user, config.db_pwd, config.db_host, config.db_port, 'company_info'))

    def dowmload_recent_cmp_overview(self):
        """DART 내 모든 기업개황정보 업데이트
        CORPCODE.xml 파일로 디렉토리에 저장됨"""

        # 기업개황 zip파일 로컬 디렉토리에 다운로드
        url = f'https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={self.api_key}'


        # 디렉토리 내 CORPNUM.xml로 파일 압축 해제
        with urlopen(url) as zipresp:
            with ZipFile(io.BytesIO(zipresp.read())) as zfile:
                zfile.extractall(self.current_dir)

        print(self.current_dir, "아래 최신 DART 기업개황 CORPNUM.xml 파일을 저장하였습니다. ---")

    def __update_overview_table__(self,tlb_name, df):
        """데이터베이스와 연결하여 테이블을 업데이트"""
        df.to_sql(str(tlb_name), self.db_engine,if_exists='replace',index=False)
        print("기업개황이 담긴 df를 데이터베이스에 업데이트했습니다. ---")

    def convert_overview_to_df(self):
        """xml파일 파일 압축 후 df로 만들기"""

        # 절대 경로로 지정
        file_path = os.path.join(self.current_dir, 'CORPCODE.xml')
        cmp_overview_df = pd.read_xml(file_path, dtype=str)
        print("기업개황 xml을 python df로 변환 완료하였습니다. ---")

        self.__update_overview_table__(cmp_overview_df)

# xml기반 기본정보 찾기
class xml_info_finder:
    def __init__(self):
        self.cmp_overview_df = None       # 이후 정의
        self.corp_code_xml = config.CORP_CODE_XML
        self.view = Info_view()

    # 회사명으로 고유번호 찾기 내부 로직(xml파일 탐색)
    def __get_corpcode_by_name__(self, input_name):
        """회사명 1개에 대하여 대응하는 고유번호가 있는지 검색하여 반환하는 매서드"""
        cnt = 0
        corp_code_list = []

        for country in self.corp_code_xml.iter("list"):
            if country.findtext("corp_name") == input_name:
                cnt += 1
                corp_code_list.append(country.findtext("corp_code"))

        # 회사 이름에 대해 고유번호가 일대다로 대응될때 고유번호를 list 형식으로 모두 반환
        if cnt > 1:
            return corp_code_list

        # 일대일로 대응할때 고유번호 1개를 반환
        elif cnt == 1:
            return corp_code_list[0]

    # 회사명으로 고유번호 찾기
    def apply_get_corpcode_by_name(self, df, input_col):
        """이름으로 고유번호 찾기 매서드를 전체 df 컬럼에 적용"""

        self.view.print_start_UI("고유번호 검색 작업")

        df['고유번호'] = df[str(input_col)].progress_apply(self.__get_corpcode_by_name__)
        df = df.explode('고유번호')  # 리스트형으로 저장된 고유번호 원자화

        self.view.print_end_UI("고유번호 검색 작업")
        return df

    # 종목코드로 고유번호 찾기
    def __get_corpcode_by_stock__(self, input_stock):
        """종목코드로 DART 고유번호를 찾는 매서드"""
        cnt = 0
        corp_code_list = []

        for country in self.corp_code_xml.iter("list"):
            if country.findtext("stock_code") == input_stock:
                cnt += 1
                corp_code_list.append(country.findtext("corp_code"))

        if cnt > 1:

            return corp_code_list

        elif cnt == 1:
            return corp_code_list[0]
    # 종목코드로 고유번호 찾기 컬럼에 적용
    def __get_corpcode_by_stock__(self, df, input_col):
        """종목코드로 고유번호 찾기 매서드를 전체 df 컬럼에 적용"""

        df['고유번호'] = df[str(input_col)].apply(self.__get_corpcode_by_stock__)
        return df


    # 고유번호로 종목코드 찾기
    def __get_stockcode_by_corpcode(self, corp_code):
        for country in self.corp_code_xml.iter("list"):
            if country.findtext("corp_code") == corp_code:
                return country.findtext("stock_code")

    def apply_stockcode_by_corpcode(self, df):

        self.view.print_start_UI("종목코드 검색 작업")
        df['종목코드'] = df['고유번호'].progress_apply(self.__get_stockcode_by_corpcode)
        self.view.print_end_UI("종목코드 검색 작업")

        return df

    # 기본 정보 출력 보기
    def print_Info_by_name(self, input_name):
        for country in self.corp_code_xml.iter("list"):
            if country.findtext("corp_name") == input_name:
                self.view.show_xml_info(country)
    def print_Info_by_stock(self, input_stock):
        for country in self.corp_code_xml.iter("list"):
            if country.findtext("stock_code") == input_stock:
                self.view.show_xml_info(country)
    def print_Info_by_corpcode(self, input_corpcode):
        for country in self.corp_code_xml.iter("list"):
            if country.findtext("corp_code") == input_corpcode:
                self.view.show_xml_info(country)

# API기반 기본정보 찾기
class API_info_finder:
    def __init__(self):
        self.api_key = config.api_key
        self.view = Info_view()

    # 고유번호로 법인등록번호 조회
    def __get_jurir_no__(self, corp_code):
        """고유번호로 DART 내 법인등록번호를 불러오는 매서드"""
        if corp_code is None or isnull(corp_code):
            return None


        try:
            url = "https://opendart.fss.or.kr/api/company.json"
            params = {"crtfc_key":self.api_key,
                      "corp_code":str(corp_code)}

            response = requests.get(url, params=params)
            data = response.json()

            if data['jurir_no']:
                return data['jurir_no']
        except Exception as e:
            print("법인등록번호를 불러오는 작업에서 에러발생: ", e)

    # 검증용 법인등록번호 컬럼 생성
    def apply_jurir_no(self,df, output_col):

        self.view.print_start_UI("검증용 법인코드 검색 작업")
        df[str(output_col)] = df['고유번호'].progress_apply(self.__get_jurir_no__)
        self.view.print_end_UI("검증용 법인코드 검색 작업")
        return df

    # 기존 법인코드와 검증용 법인코드가 일치하는지 확인하는 컬럼 생성
    def check_corpcode_vaild(self, df, origin_col, compare_col):

        self.view.print_start_UI("법인코드로 고유번호 유효 검증 작업")

        # 공백제거 및 "-" 등 제거
        df[str(origin_col)] = df[str(origin_col)].str.replace("-", "").str.strip()
        df[str(compare_col)] = df[str(compare_col)].str.replace("-", "").str.strip()

        df['고유번호 유효'] = df[str(origin_col)] == df[str(compare_col)]
        self.view.print_end_UI("법인코드로 고유번호 유효 검증 작업")
        return df



    # 특정 공시보고서 제출 목록 불러오기
    def get_raw_report_list(self, corpcode_list, start_date, end_date, pblntf_ty, pblntf_detail_ty):
        """고유번호를 기반으로 특정공시보고서 리스트를 반환하는 매서드"""

        end_bnt = False  # 예상치못한 오류에 대해 break 후 저장할 수 있게하는 버튼

        url = "https://opendart.fss.or.kr/api/list.json"

        res_df = pd.DataFrame(columns=['corp_code', 'corp_name', 'stock_code'
            , 'corp_cls', 'report_nm', 'rcept_no'
            , 'flr_nm', 'rcept_dt', 'rm'])

        length = len(corpcode_list)

        for index, corp_code in enumerate(corpcode_list):
            if end_bnt:
                break

            print(index, "/", length)

            if not corp_code or corp_code is None or isnull(corp_code):
                continue

            page_no = 0
            while True:
                page_no += 1

                params = {"crtfc_key":self.api_key,
                      "corp_code":str(corp_code).replace(" " , ""),
                      "bgn_de": str(start_date),
                      "end_de": str(end_date),
                      "last_reprt_at":'Y',
                      "pblntf_ty": str(pblntf_ty),
                      "pblntf_detail_ty": str(pblntf_detail_ty),  # https://dart-fss.readthedocs.io/en/latest/dart_types.html
                      "page_no": str(page_no),
                      "page_count":'100'}

                try:
                    response = requests.get(url, params=params)
                    data = response.json()

                    if data['message'] == '조회된 데이타가 없습니다.':
                        break
                    elif str(data['page_no']) != str(page_no):
                        break
                    elif data['message'] == "사용한도를 초과하였습니다.":
                        end_bnt = True
                        break

                    elif data['list']:
                        tmp_df = pd.DataFrame(data['list'])
                        res_df = pd.concat([res_df, tmp_df])

                except Exception as e:
                    print("고유번호 ", corp_code,"에서 에러가 발생하였습니다", e)

        return res_df


    def get_unique_column_values(self,df, col_name):
        """df 컬럼의 고유값만 남겨 리스트에 담아 반환하는 매서드"""
        return list(df[str(col_name)].unique()) # reported_list



