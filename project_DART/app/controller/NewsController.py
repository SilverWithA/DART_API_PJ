import pandas as pd
from app.model import NewsCrawler
from app.view import Info_UI


class NewsController:
    def __init__(self):
        self.news_crawler = NewsCrawler.NewsCrawler()
        self.df = pd.DataFrame(columns=['넘버링','시간','언론사','기사제목','기사링크'])
        self.view = Info_UI.Info_view()

    def 네이버_최신기사_수집(self):
        # 수집할 최신 뉴스 개수 입력
        news_cnt = int(input("수집하고자 하는 뉴스의 개수 입력(10단위): "))

        self.view.print_start_UI(f"{news_cnt}개의 뉴스 크롤링 작업")

        # 웹접속
        self.news_crawler.드라이버로_접속하기('https://search.naver.com/search.naver?where=news&query=%EB%A6%AC%EB%8D%94%EC%8A%A4%EC%9D%B8%EB%8D%B1%EC%8A%A4&sm=tab_opt&sort=1&photo=0&field=0&pd=0&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3Aall&is_sug_officeid=0&office_category=0&service_area=0')

        # 수집할 뉴스 개수에 맞게 페이지 스크롤
        self.news_crawler.페이지스크롤(news_cnt)

        # 전체 페이지 요소 불러오기
        main_divs = self.news_crawler.전체_기사섹션_divs()

        # 정보 수집 시작
        for index, div in enumerate(main_divs):
            try:
                latest_time = self.news_crawler.기사시간_수집(div)
            except Exception as e:
                print(f"{index}번째 기사의 기사시간 수집 에러 발생: ",e)

            try:
                press_name = self.news_crawler.언론사_수집(div)
            except Exception as e:
                print(f"{index}번째 기사의 언론사 수집 에러 발생: ", e)

            try:
                title, link = self.news_crawler.기사제목_기사링크_수집(div)
            except Exception as e:
                print(f"{index}번째 기사의 기사제목 및 기사링크 수집 에러 발생: ", e)

            collected_row = pd.Series([index + 1, latest_time, press_name, title, link],
                                index=['넘버링', '시간', '언론사', '기사제목', '기사링크'])

            self.df = self.df._append(collected_row,ignore_index=True)
        self.view.print_end_UI(f"{news_cnt}개의 뉴스 크롤링 작업")
        return self.df

    def 데이터프레임_html형식_변환기(self,df):
        # html로 변환하여 내보내기
        self.view.print_start_UI("html 변환 작업")
        converted_html = self.news_crawler.df_to_html_변환하기(df)
        self.view.print_end_UI("html 변환 작업")
        return converted_html


