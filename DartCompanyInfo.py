import xml.etree.ElementTree as ET
import pandas as pd
import requests
from library import api_key


class Company_info_finder():
    """특정 회사의 기본 정보(고유번호, 종목코드, 사업보고서 제출 여부)를 찾는 클래스"""

    def __init__(self):
        self.root = ET.parse('CORPCODE.xml').getroot()
        self.api_key = api_key
        self.krx_df = pd.read_excel('KRX_20250415_상장 데이터.xlsx', sheet_name="전종목 기본정보", dtype={"단축코드": str}) # 데이터베이스와 연결하여 불러오기

    # 이름으로 고유번호 찾기
    def __fill_corp_code_by_name__(self, find_name):
        """회사명으로 고유번호 찾는 매서드
            * find_name = 고유번호를 찾고자하는 회사명"""

        # 하나의 사명으로 고유번호가 여러개인 경우까지 처리
        cnt = 0
        corp_code_list = []

        for country in self.root.iter("list"):
            if country.findtext("corp_name") == find_name:
                cnt += 1
                corp_code_list.append(country.findtext("corp_code"))

        if cnt > 1:

            return corp_code_list

        elif cnt == 1:
            return corp_code_list[0]

    def __fill_corp_code_by_stock__(self, find_stock):
        """종목코드로 고유번호 찾는 매서드
            * find_stcok = 고유번호를 찾고자하는 회사의 종목코드"""

        cnt = 0
        corp_code_list = []

        for country in self.root.iter("list"):
            if country.findtext("stock_code") == find_stock:
                cnt += 1
                corp_code_list.append(country.findtext("corp_code"))

        if cnt > 1:

            return corp_code_list

        elif cnt == 1:
            return corp_code_list[0]

    def __check_jur_no__(self):
        pass

    def __check_is_group_report__(self):
        pass

    def is_corp_code_vaild(self,corp_code):
        """고유번호 유효성 검증 로직 추가"""

        if corp_code is None or isnull(corp_code):
            return "X"

        url = 'https://opendart.fss.or.kr/api/list.json'

        params = {"crtfc_key": api_key,
                      "corp_code": corp_code,
                      "bgn_de": '20241231',
                      "end_de": '20250415',
                      "pblntf_ty": "J",
                      "pblntf_detail_ty": 'J004',  # 대규모 기업집단 현황
                      "page_no": '1',
                      "page_count": '100'
                      }
        try:
            res = requests.get(url, params=params)  # API 호출
            data = res.json()  # 불러온 json to dictionary 변환

            if data['message'] == '조회된 데이타가 없습니다.':
                return "X"
            elif data['list']:
                return "●"
        except Exception as e:
            print(corp_code, "에서 에러가 발생했습니다." ,e)

    def create_corp_code_col(self, df, input_col_name, output_col_name, by):
        print()
        print(" --------------", input_col_name,"을 이용하여 dart내 고유번호를 찾기 시작! ----------------- ")
        print(" --", output_col_name, "불러오는 중 ...")

        if by == "name":

            df[str(output_col_name)] = df[str(input_col_name)].apply(self.__fill_corp_code_by_name__)

        elif by == "stock":
            df[str(output_col_name)] = df[str(input_col_name)].apply(self.__fill_corp_code_by_stock__)

        print()
        print("총 ",len(df[output_col_name]),"개의 회사의 고유번호를 매핑 완료! --------")
        print(" - 고유번호 중복 회사: ", len(df[df[str(output_col_name)].apply(lambda x: isinstance(x, list))]), "개")
        print(" - 사명으로 매핑 실패한 회사: ",len(df[df[str(output_col_name)].isna()]),"개")

        df = df.explode(output_col_name)        # 중복 고유번호를 원자화
        print("-----------------------------------")
        #
        # print("고유번호 유효성 검사 시작 ---")
        # vaild_col_name = str(output_col_name) + "_유효"
        # df[str(vaild_col_name)] = df[str(output_col_name)].apply(self.is_corp_code_vaild)

        # 유효한 것만 남기는 로직 필요



        return df


    # 고유번호로 종복코드 찾기
    def __fill_stock_code_root(self, corp_code):

        for country in self.root.iter("list"):
            if country.findtext("corp_code") == corp_code:
                return country.findtext("stock_code")

    # KRX 데이터로 빠진 종목 코드 보충하는 매서드
    def __supplement_stock_code_KRX(self, corp_name):
        """KRX 전종목 기본정보를 기준으로 종목코드를 추가 및 보충하는 매서드"""

        for index, krx_name in enumerate(self.krx_df['한글 종목약명']):
            if krx_name == corp_name:
                return self.krx_df['단축코드'][index]

    def create_stock_code(self, df, input_col_name, sup_input_col_name, output_col_name):
        print()
        print(" --------------", input_col_name,"을 이용하여 dart내 고유번호를 찾기 시작! ----------------- ")
        print(" --", output_col_name, "불러오는 중 ...")


        df[str(output_col_name)] = df[str(input_col_name)].apply(self.__fill_stock_code_root)


        # 보충 추가


        sup_col_name = str(output_col_name) + "_krx보충"
        df[str(sup_col_name)] = df[str(sup_input_col_name)].apply(self.__supplement_stock_code_KRX)

        print()
        print("총 ",len(df[output_col_name]),"개의 회사의 종목코드 매핑 완료! --------")
        print(" - 중복 데이터 수: ", len(df[df[str(output_col_name)].apply(lambda x: isinstance(x, list))]), "개")
        print(" - 불러오기 실패한 데이터 수: ",len(df[df[str(output_col_name)].isna()]),"개")
        return df



    # 고유번호로 사업보고서 제출 여부 확인
    def __collect_raw_anuual_report_list__(self, df):
        """기업 고유번호를 기반으로 사업보고서 제출 여부를 확인하는 매서드
        사용한 API 설명 페이지: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001"""

        start_date = str(input("start_date를 입력해주세요(입력예시: YYYYMMDD): "))
        end_date = str(input("end_date를 입력해주세요(입력예시: YYYYMMDD): "))


        url = 'https://opendart.fss.or.kr/api/list.json'

        # 빈 df 생성(API로 불러와지는 데이터에 맞게 미리 정의 필요)
        res_df = pd.DataFrame(columns=['corp_code', 'corp_name', 'stock_code'
            , 'corp_cls', 'report_nm', 'rcept_no'
            , 'flr_nm', 'rcept_dt', 'rm'])

        for index, corp_code in enumerate(df['고유번호']):
            if corp_code is None:
                continue

            params = {"crtfc_key": api_key,
                      "corp_code": str(corp_code).replace(" ", ""),
                      "bgn_de": start_date,
                      "end_de": end_date,
                      "pblntf_detail_ty": 'A001',
                      # 사업보고서만 조회 # https://dart-fss.readthedocs.io/en/latest/dart_types.html
                      "page_no": '1',
                      "page_count": '100'
                      }

            res = requests.get(url, params=params)  # API 호출
            data = res.json()  # 불러온 json to dictionary 변환

            if data['message'] == '조회된 데이타가 없습니다.':  # 데이타 ㅎ
                continue
            try:
                new_data = pd.DataFrame(data["list"])  # dictionary to df 변환
                res_df = pd.concat([res_df, new_data], ignore_index=True)
            except Exception as e:
                print("에러 발생: ", e, "에러 발생 구역의 고유번호: ", corp_code)

            # print(res_df)

        print("조사기간동안 제출된 사업보고서 목록을 불러왔습니다.----------------")


    def __is_annual_report__(self, corp_codes):
        if corp_codes in report_list:
            return "●"
        else:
            return "x"





