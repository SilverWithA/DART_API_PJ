# main에서 사용할 템플릿
# 각 컨트롤러의 기본적인 사용 예시임

import pandas as pd

from app.controller import DartInfoController
from app.controller import NewsController


class 기업기본정보_수집기():
    def __init__(self):
        self.cmp_info_finder = DartInfoController.Company_info_finder()

    def 순차적_기본정보_수집하기(self,file_name,sheet_name):

        # 회사명 원본 데이터 불러오기 from 디렉토리(xlsx파일)
        raw_df = self.cmp_info_finder.회사명_데이터_불러오기(file_name, sheet_name)

        # 회사명으로 고유번호 불러오기
        corp_df = self.cmp_info_finder.회사명으로_고유번호_불러오기(raw_df)

        # 고유번호 유효성 검증: 법인등록번호로 검증
        vaildated_corp_df = self.cmp_info_finder.법인등록번호로_고유번호_유효성검증(corp_df)

        # 종목코드 불러오기
        stock_df = self.cmp_info_finder.고유번호로_종목코드_불러오기(vaildated_corp_df)

        # 사업보고서 제출 여부 확인
        reported_df = self.cmp_info_finder.사업보고서제출여부_확인(stock_df)

        # 데이터 저장
        reported_df.to_excel('사업보고서 제출여부 확인 완료.xlsx', index=False)

    def 이름으로_개별기본정보_확인하기(self):

        while True:
            cmp_name = input("다트기준 회사명 입력: ")
            self.cmp_info_finder.xml_model.print_Info_by_name(cmp_name)

def 네이버_보도자료_아카이브():
    """네이버 뉴스란에 올라온 최근 보도자료 관련 보도들을 수집"""
    newscontroller = NewsController.NewsController()

    # 네이버 창열기
    news_df = newscontroller.네이버_최신기사_수집()

    news_df.to_excel('raw_크롤링뉴스.xlsx', index=False)

    # 보도자료 관련된 내용만 추린 후(로컬 엑셀에서 작업) 불러오기
    news_df = pd.read_excel('raw_크롤링뉴스.xlsx')

    news_html = newscontroller.데이터프레임_html형식_변환기(news_df)

    with open("뉴스 크롤링 html.txt","w") as f:
        f.write(news_html)

def 작업완료_엑셀파일_db_업로드():
    from app.controller import DatabaseController
    db_controller = DatabaseController.DatabaseController()
    db_controller.보도자료_최종데이터_저장하기('ReducedCap_250513', 'raw_주총공고 준비금 감액', 'raw_주총공고 준비금 감액', 'meta')



