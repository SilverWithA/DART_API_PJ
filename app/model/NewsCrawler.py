# 네이버 뉴스 등 크롤링을 위한 모델
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

import pandas as pd
from tqdm import tqdm
tqdm.pandas()

class NewsCrawler():
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # 백그라운드 실행
        self.driver = webdriver.Chrome()

    def 드라이버로_접속하기(self, url):
        self.driver.get(str(url))  # 웹페이지 접속

    def 페이지스크롤(self, news_cnt):
        scroll_cnt = 0
        while True:
            if int(scroll_cnt) == int(news_cnt / 10) - 1:
                break
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            scroll_cnt += 1

    def 전체_기사섹션_divs(self):
        main_divs = self.driver.find_elements(By.CSS_SELECTOR,
                                         "div.sds-comps-vertical-layout.sds-comps-full-layout.dZQQMujvOqnxG1bUQsg6")
        return main_divs

    def 기사시간_수집(self,div):
        time_element = div.find_element(By.CSS_SELECTOR,
                                        "div.sds-comps-profile-info span.sds-comps-profile-info-subtext span.sds-comps-text")
        latest_time = time_element.text.strip()
        return latest_time

    def 언론사_수집(self,div):
        press_element = div.find_element(By.CSS_SELECTOR,
                                         "div.sds-comps-horizontal-layout.sds-comps-inline-layout.sds-comps-profile-info-title span.sds-comps-text span.sds-comps-text")
        press_name = press_element.text.strip()
        return press_name

    def 기사제목_기사링크_수집(self,div):

        article_block = div.find_elements(By.CSS_SELECTOR,
                                          "div.sds-comps-base-layout.sds-comps-full-layout.m6eR7KmFjLYOLhYRyXPh")[0]
        link_tag = article_block.find_element(By.CSS_SELECTOR,
                                              "div.sds-comps-vertical-layout.qzzZ4sfgNQt_Z2zgPnrg a")
        title = link_tag.text.strip()

        link = link_tag.get_attribute("href")

        return title, link

    def df_to_html_변환하기(self,df):
        html_parts = []
        for i, row in df.iterrows():
            number = row['넘버링']
            title = row['기사제목']
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

        return "\n".join(html_parts)





