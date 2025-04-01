import xml.etree.ElementTree as ET
import pandas as pd
import requests
from library import api_key


class Company_info_finder():
    """특정 회사의 기본 정보(고유번호, 종목코드, 사업보고서 제출 여부)를 찾는 클래스"""

    def __init__(self):
        self.root = ET.parse('CORPCODE.xml').getroot()
        self.api_key = api_key

    # 회사명으로 고유번호를 찾는 매서드
    def __fill_corp_code__(self, find_name):
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

    def __fill_jurir_no_by_corp_code__(self, corp_code):
        """고유번호를 통해 법인등록번호 조회하여 고유번호가 유효한지 확인하는 매서드"""
        if corp_code is None or corp_code == "-":
            return

        url = "https://opendart.fss.or.kr/api/company.json"

        params = {
            "crtfc_key": self.api_key,
            "corp_code": corp_code,
        }

        res = requests.get(url, params=params)
        data = res.json()

        try:
            if data['jurir_no']:
                return str(data['jurir_no'])
            else:
                return "-"
        except:
            print(corp_code, "로 법인등록번호를 조회할 수 없습니다. 추가확인이 필요합니다.")

    def __is_vaild_corp_code__(self, df):

        df['법인등록번호2'] = df['고유번호'].apply(self.__fill_jurir_no_by_corp_code__)
        df['고유번호 유효'] = df.apply(lambda row: str(row['법인등록번호']).replace(" ","").replace("-","")
                                             == str(row['법인등록번호2']).replace(" ","").replace("-",""), axis=1)

        return df



    def create_corp_code_col(self, df, input_col_name, output_col_name):
        print()
        print(" --------------", input_col_name,"을 이용하여 dart내 고유번호를 찾기 시작! ----------------- ")
        print(" --", output_col_name, "불러오는 중 ...")

        df[output_col_name] = df[input_col_name].apply(self.__fill_corp_code__) # 사명으로 고유번호 찾기

        print()
        print("총 ",len(df[output_col_name]),"개의 회사의 고유번호를 매핑 완료! --------")
        print(" - 고유번호 중복 회사: ", len(df[df[output_col_name].apply(lambda x: isinstance(x, list))]), "개")
        print(" - 사명으로 매핑 실패한 회사: ",len(df[df[output_col_name].isna()]),"개")

        df = df.explode(output_col_name)        # 중복 고유번호를 원자화


        print(" - 고유번호 유효성 검증 작업중...")
        df = self.__is_vaild_corp_code__(df)
        print(" --- 고유번호 유효성 검증 완료 --- ")
        return df

    # 고유코드로 종목 코드 찾는 매서드
    def fill_stock_code_Dart(corp_code):
            """Dart API를 통해 Dart 내 종목코드 찾는 매서드"""

            # 종목코드를 불러와 저장해줄 컬럼 사전 정의 필요
            # API 호출 url 정의
            url = f'https://opendart.fss.or.kr/api/company.json'

            if not corp_code:
                return None

            params = {
                "crtfc_key": str(api_key),  # 호출을 위한 API키
                "corp_code": str(corp_code) # 고유번호
            }

            try:
                # API호출
                res = requests.get(url, params= params)
                data = res.json()   #json 형식으로 파싱

                # 호출이 정상적으로 불러와졌을 때만 종목코드 추가 및 수정
                if data['message'] != '정상':
                    return

                # Dart 데이터베이스 내 종목코드가 정의된 것이 없다면 패스
                if len(data['stock_code']) == 0:
                    return None
                else:
                    return data['stock_code']

            except Exception as e:
                print(corp_code, "에서 에러발생!")

    # KRX 데이터로 빠진 종목 코드 보충하는 매서드
    def supplement_stock_code(df,krx_df, df_corp_code, krx_corp_name):
        """KRX 전종목 기본정보를 기준으로 종목코드를 추가 및 보충하는 매서드
        df: 보충하고자하는  데이터프레임
        krx_df: KRX 전종목 기본정보 데이터프레임
        df_corp_code = df내 고유번호가 정의된 컬럼명(str)
        krx_corp_name = df내 krx기준 회사명 컬럼명(str)
        * 실행 전 krx_df내 컬럼 명을 확인할 것, 매서드 수정이 필요할 수 있음"""

        for i, company_name in enumerate(df[krx_corp_name]):
            for idx, krx_name in enumerate(krx_df['한글 종목약명']):
                if krx_name == company_name:
                    df[str(df_corp_code)][i] = krx_df['단축코드'][idx]
                    continue

    # 매핑이 되지 않은 빈 row를 확인하는 매서드
    def find_none_mapping_rows(df, check_col_name, corp_name):
        """위 매서드 사용 후 매핑되지 않은 빈 컬럼 확인시 사용할 수 있는 매서드
            check_col_name: 매핑여부를 확인할 컬럼 이름
            corp_name: 회사명이 정의된 컬럼 이름"""

        missing_corpcode_list = []
        for index, data in enumerate(df[str(check_col_name)]):

            # 매핑이 되지 않은 경우
            if data is None or len(data) == 0:
                missing_corpcode_list.append(df[str(corp_name)][index])

        print("전체 계열사 개수: ", len(df[str(corp_name)]))
        print("매핑 안된 계열사 수: ",len(missing_corpcode_list))
        print("매핑 안된 계열사: ", missing_corpcode_list)


