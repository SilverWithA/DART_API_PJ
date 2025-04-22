# 고유번호, 종목코드, 사업보고서 제출 여부 기본 정보를 크롤링하는 모델
import config


class Info_API_Collecter:
    def __init__(self):
        self.corp_code_xml = config.CORP_CODE_XML

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

    def apply_get_corpcode_by_name(self, df, input_col):
        """이름으로 고유번호 찾기 매서드를 전체 df 컬럼에 적용"""
        df['고유번호'] = df[str(input_col)].apply(self.get_corpcode_by_name)

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
