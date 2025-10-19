
from app.model.Info_collecter import API_info_finder
finder = API_info_finder()
from app.model.Info_collecter import xml_info_finder
xml_finder = xml_info_finder()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

chrome_options = Options()
chrome_options.add_argument("--headless")  # 헤드리스 모드 활성화
chrome_options.add_argument("--disable-gpu")  # GPU 비활성화 (일부 환경에서 필요)
chrome_options.add_argument("--window-size=1920,3000")
import pandas as pd
import time

### 공시보고서 접수번호 목록 불러오기를 위한 고유번호 불러오기 ------------------
stock_list = pd.read_excel('상반기 배당현황 분석.xlsx',sheet_name='상장사 목록',dtype=str)
from app.model.Info_collecter import xml_info_finder
xml_finder = xml_info_finder()

stock_list = finder.get_corpcode_by_stock2(stock_list,'종목코드')
stock_list = stock_list.explode('고유번호',ignore_index=True)
stock_list.to_excel('상반기 배당현황 분석_고유번호추가.xlsx')


### 배당관련 보고서 리스트업 --------------------------------------------
## 조사기간: 2025년 1월 1일 ~ 2025년 8월 31일
## 리스트업할 보고서 상세: 거래소공시 > 수시공시(I001) > 현금ㆍ현물배당결정 보고서
stock_list= pd.read_excel('상반기 배당현황 분석_고유번호추가.xlsx',dtype='str')     #상장사 목록 불러오기
corpcode_list_보통주 = stock_list[stock_list['주식종류'] =="보통주"]              # 보통주 상장사만
corpcode_list = corpcode_list_보통주['고유번호']
수시공시_all = finder.공시보고서_접수번호목록_가져오기_디테일버전(corpcode_list, '20250101', '20250831', "I001")

# 현금ㆍ현물배당결정 보고서만 필터링
datafilter = 수시공시_all['report_nm'].str.contains("현물배당")
valid_report = 수시공시_all[datafilter]
invalid_report = 수시공시_all[~datafilter]

valid_report.to_excel('상장사 250101_250831_현금현물배당보고서.xlsx',index=False)



### 현금배당 보고서 크롤링
# 배당구분, 배당종류, 1주당 배당금(보통주, 우선주), 시가배당율(보통주, 우선주), 배당금총액, 배당기준일
df = pd.read_excel('25년 상반기 배당 현황_v2_20250901.xlsx',sheet_name="배당보고서(상반기)",dtype=str)
def 현금현물배당결정보고서_크롤러(df):


    # a_raw_배당보고서_df 병합을 위한 스키마 미리 지정
    column_names = ['접수번호', '배당구분', '배당종류', '주당배당금_보통주', '주당배당금_우선주', '시가배당율_보통주', '시가배당율_웅선주', '배당금총액', '배당기준일', '비고']
    a_raw_배당보고서_df = pd.DataFrame(columns=column_names)   # 크롤링으로 얻어진  raw 데이터를 담아줄 데이터
    total = len(df['report_nm'])                             # 크롤링 대상 전체 개수
    a_error_list = []                                        # 보고서 내 형식이 다를시 접수번호를 담을 에러 리스트

    # rept_no = "20250306800293"
    # idx=0

    # 배당보고서 접수번호를 순환하며 보고서를 크롤링
    for idx, rept_no in enumerate(df['rcept_no']):

        print(f"{idx} / {total} - (", round(idx / total * 100,1),")%")   # 진행상황 콘솔에 프린트하여 작업 시간 및 현황 파악
        time.sleep(2)

        try:
            driver = webdriver.Chrome(options=chrome_options)   # 백그라운드 실행(크롬 탭 보이지 않음)
            # driver = webdriver.Chrome()                       # 테스트용 코드(크롬 탭 보임) -> 테스트용 코드
            driver.get(f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rept_no}")   # 접수번호를 이용해 공시 보고서 접속

            # iframe 속으로 driver 전환
            iframe = driver.find_element(By.ID, "ifrm")
            driver.switch_to.frame(iframe)

            # html 요소 중 border가 1인 table 요소 모두 선택 -> 배당보고서의 경우 보통 1개지만 정정보고서의 경우 그렇지 않으므로 주의 필요
            table_elements = driver.find_elements(By.XPATH, '//table[@border="1"]')

            # 각 테이블 요소 loop
            for i,table in enumerate(table_elements):

                html = table.get_attribute('outerHTML')             # table 요소를 html로 변환
                soup = BeautifulSoup(html, 'html.parser')    # html을 beautifulsoup 데이터 형식으로 파싱
                rows = soup.find_all('tr')                          # table에 row에 해당하는 tr요소를 모두 불러옴

                raw_row = [None] * 10
                raw_row[0] = rept_no
                pre_column = None
                tmp = []
                cnt = 0


                for row in rows:
                    tds = row.find_all('td') # 실질적인 데이터를 갖고있는 모든 td요소를 불러오기
                    col_list = [col.get_text(strip=True).replace(" ","") for col in tds]    # # tr에 있는 모든 text 불러서 list로 변환

                    try:
                        if len(tds) < 2 or len(tds) > 3:
                            continue

                        if len(tds) == 2 and pre_column is None:
                            cnt += 1
                            if '배당구분' in str(col_list[0]):
                                raw_row[1] = col_list[1]
                            elif '배당종류' in str(col_list[0]):
                                raw_row[2] = col_list[1]
                            elif '배당금총액' in str(col_list[0]):
                                raw_row[7] = col_list[1]
                            elif '배당기준일' in str(col_list[0]):
                                raw_row[8] = col_list[1]

                        elif len(tds) == 3 or '주당배당금' in pre_column or '시가배당율' in pre_column:
                            cnt += 1

                            if '주당배당금' in str(col_list[0]):
                                if '보통' in col_list[1]:
                                    raw_row[3] = col_list[2]
                                    pre_column = '주당배당금'
                            elif '종류' in str(col_list[0]) and '주당배당금' in pre_column:
                                raw_row[4] = col_list[1]
                                pre_column = None

                            elif '배당율' in str(col_list[0]):
                                if '보통' in col_list[1]:
                                    raw_row[5] = col_list[2]
                                    pre_column = '시가배당율'
                            elif '종류' in str(col_list[0]) and '시가배당율' in pre_column:
                                raw_row[6] = col_list[1]
                                pre_column = None

                    except Exception as e:
                        continue
                if cnt > 0:
                    tmp.append(raw_row)


                # tables의 정보를 저장한 tmp 리스트를 df화한 뒤 raw_tables와 row기준으로 병합
                tmp_df = pd.DataFrame(data= tmp, columns=column_names)
                a_raw_배당보고서_df = pd.concat([a_raw_배당보고서_df,tmp_df],axis=0)

            driver.quit()
        except:
            a_error_list.append(rept_no)    # 오류가 발생하여 크롤링이 되지 않은 접수번호 수집
            continue

    return a_raw_배당보고서_df, a_error_list

a_raw_배당보고서_df, a_error_list = 현금현물배당결정보고서_크롤러(df)
a_raw_배당보고서_df.to_excel('현금배당보고서 크롤링 raw.xlsx')

