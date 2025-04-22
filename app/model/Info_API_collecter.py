# 고유번호, 종목코드, 사업보고서 제출 여부 기본 정보를 크롤링하는 모델
import pandas as pd
import requests

import config


class Info_API_Collecter:
    def __init__(self):
        self.corp_code_xml = config.CORP_CODE_XML
        self.api_key = config.api_key


    # 기본정보로 고유번호 단순 매핑
    def get_corpcode_by_name(self, input_name):
        """회사명으로 고유번호 찾는 매서드"""
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

    def print_stockcode_by_name(self, input_name):
        for country in self.corp_code_xml.iter("list"):
            if country.findtext("corp_name") == input_name:
                return country.findtext("stock_code")

    def apply_get_corpcode_by_name(self, df, input_col):
        """이름으로 고유번호 찾기 매서드를 전체 df 컬럼에 적용"""
        df['고유번호'] = df[str(input_col)].apply(self.get_corpcode_by_name)
        return df

    def get_corpcode_by_stock(self, input_stock):
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

    def apply_get_corpcode_by_stock(self, df, input_col):
        """이름으로 고유번호 찾기 매서드를 전체 df 컬럼에 적용"""
        df['고유번호'] = df[str(input_col)].apply(self.get_corpcode_by_stock)
        return df


    # 고유번호 유효성 검증
    def get_jurir_no(self, corp_code):
        """고유번호로 DART 내 법인등록번호를 불러오는 매서드"""

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

    def apply_get_jurir_no(self,df):
        df['검증용 법인코드'] = df['고유번호'].apply(self.get_corpcode_by_stock)
        return df

    def is_equal_jurir_no(self, df):
        """기존 법인등록번호와 불러온 법인등록번호가 일치하는지 확인하는 매서드"""
        # 공백제거
        # "-"값제거


    # 특정보고서 제출여부 확인
    def get_raw_report_list(self, corpcode_list,start_date,end_date, pblntf_ty, pblntf_detail_ty):
        """고유번호를 기반으로 특정공시보고서 리스트를 반환하는 매서드"""
        url = "https://opendart.fss.or.kr/api/list.json"

        res_df = pd.DataFrame(columns=['corp_code', 'corp_name', 'stock_code'
            , 'corp_cls', 'report_nm', 'rcept_no'
            , 'flr_nm', 'rcept_dt', 'rm'])

        for corp_code in corpcode_list:
            if not corp_code or corp_code is None:
                continue

            params = {"crtfc_key":self.api_key,
                      "corp_code":str(corp_code).replace(" " , ""),
                      "bgn_de": start_date,
                      "end_de": end_date,
                      "last_reprt_at":'Y',
                      "pblntf_ty": pblntf_ty,
                      "pblntf_detail_ty": pblntf_detail_ty,
                      "page_count":'100'}

            try:
                response = requests.get(url, params=params)
                data = response.json()

                if data['message'] == '조회된 데이타가 없습니다.':
                    continue

                if data['list']:
                    tmp_df = pd.DataFrame(data['list'])
                    res_df = pd.concat([res_df, tmp_df])

            except Exception as e:
                print("고유번호 ", corp_code,"에서 에러가 발생하였습니다", e)

        print("공시보고서 리스트를 모두 불러왔습니다 --- ")
        return res_df

    def get_unique_column_values(self,df, col_name):
        """df 컬럼의 고유값만 남겨 리스트에 담아 반환하는 매서드"""
        return list(df[str(col_name)].unique()) # reported_list

    def is_reported(self, input_corpcode, reported_list):
        """해당 고유번호에 대응하는 회사가 특정보고서를 보고하는지 여부를 반환하는 매서드"""
        if input_corpcode in reported_list:
            return "●"
        else:
            return "x"



