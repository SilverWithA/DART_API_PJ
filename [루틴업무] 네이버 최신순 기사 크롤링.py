from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import datetime
from selenium.webdriver.chrome.options import Options

# 셀레니움 드라이버 옵션
chrome_options = Options()
chrome_options.add_argument("--headless")  # 헤드리스 모드 활성화

columns = ['NO','기사입력시간','언론사','기사제목','기사링크','네이버기사제목']
news_data = pd.DataFrame(columns=columns)



print("---- 네이버 뉴스 기사 크롤링 프로그램을 시작합니다 ----")

# 네이버 창 열기
driver = webdriver.Chrome()
# 리더스인덱스 검색, 최신순 뉴스 정렬
driver.get(str('https://search.naver.com/search.naver?where=news&query=%EB%A6%AC%EB%8D%94%EC%8A%A4%EC%9D%B8%EB%8D%B1%EC%8A%A4&sm=tab_opt&sort=1&photo=0&field=0&pd=0&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3Aall&is_sug_officeid=0&office_category=0&service_area=0'))


# 페이지 스크롤해서 기사 로딩하기
news_cnt = int(input("최신순으로 수집할 뉴스 기사 개수를 10개 단위로 입력해주세요: "))
scroll_cnt = 1


# 네이버 기사창 스크롤하여 뉴스 불러오기
while True:
    if int(scroll_cnt) == int(news_cnt / 10):
        break
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    scroll_cnt += 1

# 뉴스 데이터가 들어있는 html 영역 선택하기
error_list = []
root_div = driver.find_element(
    By.CSS_SELECTOR,
    f"div.sds-comps-vertical-layout.sds-comps-full-layout.fds-news-item-list-tab"
)

first_inner_div = root_div.find_element(By.TAG_NAME, "div")  # 첫 번째 자식 div
div_class = first_inner_div.get_attribute("class")
div_class = div_class.replace(" ", ".")

news_divs = driver.find_elements(
    By.CSS_SELECTOR,
    f"div.{div_class}"
)

for index, div in enumerate(news_divs):
    print(f' {index} / {news_cnt}:', round(index/news_cnt*100, 1), "%") # 진행 상황 콘솔에 print
    try:

        # 도메인에 출력된 언론사 이름
        press_element = div.find_element(By.CSS_SELECTOR,"span.sds-comps-profile-info-title-text a")
        a_press = press_element.text.strip()

        article_block = div.find_elements(By.CSS_SELECTOR,"div.sds-comps-base-layout.sds-comps-full-layout")[0]

        # 도메인에 첨부돼 있는 기사 링크
        link_tag = article_block.find_element(By.CSS_SELECTOR,"div.sds-comps-vertical-layout a")
        a_link = link_tag.get_attribute("href")
        a_title = link_tag.text.strip() # 도메인 기사 제목

        # (네이버 제휴사만 有) 네이버 기사 사이트 링크
        try:
            __naver_news_element__ = div.find_element(By.CSS_SELECTOR, "span.sds-comps-profile-info-subtext a")
            naver_news_link = __naver_news_element__.get_attribute("href")

            # 네이버 기사로 링크로 접속
            sub_driver = webdriver.Chrome(options=chrome_options)
            sub_driver.get(str(naver_news_link))

            # 네이버 기사 내 기사 제목
            __title_element__ = sub_driver.find_element(By.CSS_SELECTOR, "div.media_end_head_title")
            naver_title = __title_element__.text.strip()

            # 네이버 기사 내 기사 입력시간
            __time_element__ = sub_driver.find_element(By.CSS_SELECTOR, "div.media_end_head_info_datestamp_bunch")
            news_time = __time_element__.find_elements(By.CSS_SELECTOR,
                                                       "span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME")[0]
            news_time = news_time.text.strip()
        except:
            naver_title = None
            news_time = None

        collected_row = pd.Series([index + 1, news_time, a_press, a_title, a_link, naver_title],
                                  index=columns)

        news_data = news_data._append(collected_row, ignore_index=True)

    except Exception as e:
        error_list.append(index)
        print(index, "에서 에러발생",e)
        break
driver.quit()   # 드라이버 닫기
print(news_cnt,"개의 뉴스 데이터를 크롤링 완료했습니다.")
# print(news_cnt, "개의 뉴스 데이터 중 찾고자 하는 뉴스 키워드를 입력을 시작합니다")
# print("제목을 기준으로 필터링하고 싶은 키워드들을 모두 입력해주세요.")
# 특정 키워드 존재하는지 체크


datafilter = news_data['기사제목'].str.contains("온실가스|탄소")
valid_news_data = news_data[datafilter]    # html화 df
invalid_news_data = news_data[~datafilter] # 확인용 df

# 주요 기준으로 우선순위 정렬
# 주요 언론사 리스트
주요_언론사 = ['매일경제','중앙일보','한겨레','SBS','KBS','연합뉴스','경향신문', '국민일보', '동아일보','서울신문', '중앙일보', '한겨레', '한국일보']

# 언론사가 주요 언론사에 포함되면 0, 아니면 1 → 우선순위 부여
valid_news_data.insert(len(valid_news_data.columns), '우선순위', None)
valid_news_data.loc[:,'우선순위'] = valid_news_data['언론사'].apply(lambda x: 0 if x in 주요_언론사 else 1)

# 우선순위 기준으로 정렬하고, 인덱스 재설정
valid_news_data = valid_news_data.sort_values(by=['우선순위','NO']).reset_index(drop=True)

# 필요하면 우선순위 컬럼 제거
valid_news_data = valid_news_data.drop(columns=['우선순위'])

valid_news_data["NO"] = valid_news_data.index + 1
valid_news_data.to_excel('네이버뉴스크롤링.xlsx',index=True)


# 넘버링 재정렬: 특정 언론사 우선으로 올리기(우선순위 정렬) - 추가 필요
to_html  = valid_news_data


print("필터링한 기사의 순서를 정렬 완료하였습니다.")
print("데이터를 html형식으로 변환 시작합니다. 반환이 끝나면 프로그램을 실행했던 파일을 확인해주세요.")
# html 방식으로 변환
to_html['네이버기사제목'] = to_html['네이버기사제목'].fillna(to_html['기사제목'])
html_parts = []
for i, row in to_html.iterrows():
    number = row['NO']
    title = row['네이버기사제목']
    link = row['기사링크']
    press = row['언론사']
    html = f'''
                <p><span style="font-family:'Noto Sans KR';font-size:17px;">
                {number}. 
                <span style="color:rgb(65,65,65);font-style:normal;font-weight:400;letter-spacing:normal;text-align:left;background-color:rgb(255,255,255);font-family:'Noto Sans KR';font-size:17px;">
                <a href="{link}" rel="noreferrer noopener" target="_blank">
                <strong><span style="font-weight:400;">{title}</span></strong>
                </a>
                <strong><span style="font-weight:400;">&nbsp;</span></strong>&lt;{press}&gt;
                </span>&nbsp;
                </span></p>
                <p><span style="font-family:'Noto Sans KR';font-size:17px;">&nbsp;</span></p>
                '''
    html_parts.append(html.strip())
res_html = "\n".join(html_parts)


# from app.controller import NewsController
# newscontroller = NewsController.NewsController()
# news_html = newscontroller.데이터프레임_html형식_변환기(to_html)
with open(f"raw 네이버뉴스 크롤링_{datetime.datetime.now().date()}.txt", "w",encoding="utf-8") as f:
    f.write(res_html)

print("html 형식의 txt 파일이 디렉토리에 저장되었습니다. 프로그램을 종료합니다.")