from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

driver = webdriver.Chrome()
driver.get(str('https://search.naver.com/search.naver?where=news&query=%EB%A6%AC%EB%8D%94%EC%8A%A4%EC%9D%B8%EB%8D%B1%EC%8A%A4&sm=tab_opt&sort=1&photo=0&field=0&pd=0&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3Aall&is_sug_officeid=0&office_category=0&service_area=0'))

news_cnt = int(input("크롤링할 기사개수를 입력(10개 단위): "))

df = pd.DataFrame(columns=['넘버링','언론사','기사제목','기사링크'])


# 페이지 스크롤해서 기사 로딩하기
scroll_cnt = 0
while True:
    if int(scroll_cnt) == int(news_cnt / 10):
        break
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    scroll_cnt += 1


# main div 클래스가 수시로 바뀌므로 크롤링시마다 바꿔줘야하는 문제
error_list = []

root_div = driver.find_element(
    By.CSS_SELECTOR,
    f"div.sds-comps-vertical-layout.sds-comps-full-layout.fds-news-item-list-tab"
)

first_inner_div = root_div.find_element(By.TAG_NAME, "div")  # 첫 번째 자식 div
div_class = first_inner_div.get_attribute("class")
div_class = div_class.replace(" ", ".")
# sds-comps-vertical-layout sds-comps-full-layout fds-news-item-list-tab

news_divs = driver.find_elements(
    By.CSS_SELECTOR,
    f"div.{div_class}"
)

div= news_divs[0]
for index, div in enumerate(news_divs):
    try:


        press_element = div.find_element(By.CSS_SELECTOR,"span.sds-comps-profile-info-title-text a")
        a_press = press_element.text.strip()

        article_block = div.find_elements(By.CSS_SELECTOR,"div.sds-comps-base-layout.sds-comps-full-layout")[0]

        link_tag = article_block.find_element(By.CSS_SELECTOR,"div.sds-comps-vertical-layout a")
        a_link = link_tag.get_attribute("href")
        a_title = link_tag.text.strip()


        # print(latest_time,press_name,title,link)

        collected_row = pd.Series([index + 1, a_press, a_title, a_link],
                                  index=['넘버링', '언론사', '기사제목', '기사링크'])

        df = df._append(collected_row, ignore_index=True)

    except Exception as e:
        error_list.append(index)
        print(index, "에서 에러발생",e)
        break

driver.quit()

df.to_excel('raw 네이버뉴스 크롤링.xlsx',index=False)

news_df = pd.read_excel('raw 네이버뉴스 크롤링.xlsx',sheet_name=0,dtype=str)

from app.controller import NewsController
newscontroller = NewsController.NewsController()
news_html = newscontroller.데이터프레임_html형식_변환기(news_df)

with open("뉴스 크롤링 html_20250611.txt", "w",encoding="utf-8") as f:
    f.write(news_html)