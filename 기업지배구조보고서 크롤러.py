import pandas as pd
import xlrd
import openpyxl


# 엑셀 병합하기

for i in range(1,7):

    if i == 1:
        df = pd.read_excel('상세검색.xls', sheet_name=0, engine="xlrd")
    try:
        df1= pd.read_excel(f'상세검색 ({i}).xls', sheet_name=0, engine="xlrd")
        df = pd.concat([df, df1], axis=0, ignore_index=True)

    except:
        print(i,"에서 에러발생")
        break

df.to_excel('기업위원회_4개년.xlsx',index=False)

## 1. 기업지배구조보고서 풀러오기
from app.model.Info_collecter import API_info_finder
finder = API_info_finder()


# 거래소공시(I) > 수시공시(I001)로 검색
report_df = finder.공시보고서_접수번호목록_가져오기_no고유번호( '20200402','20200701','I','I003')
report_df.to_excel('거래소공시  raw 240529_240630.xlsx',index=False)


#### 웹크롤링
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# ChromeOptions 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 헤드리스 모드 활성화
chrome_options.add_argument("--disable-gpu")  # GPU 비활성화 (일부 환경에서 필요)
chrome_options.add_argument("--window-size=1920,3000")
import pandas as pd


## (1) 기업지배구조보고서 목록 불러오기
report_df = pd.read_excel('500대 기업_기업지배구조보고서_20250605_v4.xlsx',sheet_name='2023 보고서 목록',dtype=str)

## (2) 웹크롤링으로 데이터 불러오기
rept_no= '20250604800426'   # 테스트용 접수번호

error_list = []     # 에러가 발생한 접수번호
column_names = ['접수번호', '테이블순번', '테이블이름', 'dummy3', 'dummy4', 'dummy5', 'dummy6', 'dummy7', 'dummy8', 'dummy9', 'dummy10']
raw_tables = pd.DataFrame(columns=column_names)
total = len(report_df)

# 웹크롤링 루프
for idx, rept_no in enumerate(report_df['rcept_no']):

    # # 중간 저장
    # if idx == 200:
    #     raw_tables.to_excel('기업지배구조_중간저장.xlsx',index=False)
    #     raw_tables = pd.DataFrame(columns=column_names)


    time.sleep(2)

    try:
        # 웹접속
        driver = webdriver.Chrome(options=chrome_options)
        # driver = webdriver.Chrome()  # 테스트용 코드
        driver.get(f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rept_no}")

        # iframe 전환
        iframe = driver.find_element(By.ID, "ifrm")
        driver.switch_to.frame(iframe)

        # table-name p 태그들을 전부 찾기
        table_titles = driver.find_elements(By.CSS_SELECTOR, "p.table-name")
        for i, p_tag in enumerate(table_titles):
            title_text = p_tag.text

            try:

                # 2. 태이블이름에 해당하는 table.fact-table 요소 찾기 - 단점 table name없이 공시된 정보를 놓치게 됨
                table = p_tag.find_element(By.XPATH, "following-sibling::*[1]//table[@class='fact-table']")

                html = table.get_attribute('outerHTML')
                soup = BeautifulSoup(html, 'html.parser')
                rows = soup.find_all('tr')  # tr요소를 rows로 불러오기

                tmp = []
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    col_list = [col.get_text(strip=True) for col in cols]

                    col_list.insert(0, title_text)  # 테이블 이름 추가
                    col_list.insert(0, i)  # 테이블 순번 추가
                    col_list.insert(0, rept_no)  # 접수번호 추가

                    if len(col_list) < 11:
                        col_list += [None] * (11 - len(cols) - 3)
                    else:
                        col_list = col_list[:11]
                    tmp.append(col_list)

                # raw_table 데이터에 병합
                tmp_df = pd.DataFrame(data=tmp, columns=column_names)
                raw_tables = pd.concat([raw_tables, tmp_df], axis=0)
            except:
                print("해당 제목 아래에 테이블이 없음:", title_text)

    except:
        error_list.append(rept_no)
        continue

    finally:
        driver.quit()
        print(idx, "/", total, "-", round(idx / total * 100, 1), "%")
        continue


raw_tables.to_excel('raw 기업지배구조 크롤링(2023결산)_.xlsx',index=False)
