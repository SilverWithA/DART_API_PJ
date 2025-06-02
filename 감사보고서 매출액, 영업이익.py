
# 1. 감사보고서 목록 불러오기
# from app.model.Info_collecter import API_info_finder
# finder = API_info_finder()
# 2025.02.14 - 2025.05.14
# report_df = finder.공시보고서_접수번호목록_가져오기_no고유번호( '20250214','20250514','F','F001') # 감사보고서
# report_df.to_excel('감사보고서 250214_250514.xlsx')
#
# # 2024.12.13 - 2025.02.13
# report_df2 = finder.공시보고서_접수번호목록_가져오기_no고유번호( '20241213','20250213','F','F001') # 감사보고서
# report_df2.to_excel('감사보고서 20241213_250213.xlsx')
# # 2024.09.12 - 2024.12.12
# report_df3 = finder.공시보고서_접수번호목록_가져오기_no고유번호( '20240912','20241212','F','F001') # 감사보고서
# report_df3.to_excel('감사보고서 240912_241212.xlsx')


from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import datetime

# 1. ChromeOptions 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 헤드리스 모드 활성화
chrome_options.add_argument("--disable-gpu")  # GPU 비활성화 (일부 환경에서 필요)
chrome_options.add_argument("--window-size=1920,3000")
import pandas as pd
import re


#### 2. 결산 보고서인지 확인용 raw 수집
df = pd.read_excel('500대기업 소팅 감사보고서 매출액, 영업이익.xlsx',sheet_name='감사보고서 목록',dtype=str)
df = df[df['미완료'] == "●"]


def 결산_확인메서드():
    for idx, rept_no in enumerate(is_final_df['rcept_no']):
    print(idx,"/",total,"-", round(idx/total*100,1),"%")

    try:

        driver = webdriver.Chrome(options=chrome_options)
        # driver = webdriver.Chrome() # 테스트용 코드
        driver.get(f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rept_no}")

        iframe = driver.find_element(By.ID, "ifrm")
        driver.switch_to.frame(iframe)

        rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')

        tmp_data = [[rept_no]]
        for no, row in enumerate(rows):
            if no >  3:
                break
            else:
                tmp_data[0].append(row.text)

        tmp_df = pd.DataFrame(data=tmp_data, columns=column_names)
        res_df = pd.concat([res_df, tmp_df], axis=0)
        driver.quit()
    except:
        error_lst.append(rept_no)
        driver.quit()
        continue
# res_df.to_excel('결산확인.xlsx', index=False)

#### 3. 매출액 및 영업이익 수집용 raw - 손익계산서 전부 긁어오기
rept_no= '20250403002560'

aest_df = pd.DataFrame(columns=['rcept_no'],data = ['20250403002560','20250410000936','20250411000415'])

# 개황 > 손익계산서 > 개황 순서

error_list = []
unfitted_list = [] # 해당 코드 진행으로 유효한 데이터를 모을 수 없는 접수번호 모음
column_names = ['접수번호', '테이블순번', 'dummy2', 'dummy3', 'dummy4', 'dummy5', 'dummy6', 'dummy7', 'dummy8', 'dummy9'
                            , 'dummy10', 'dummy11', 'dummy12', 'dummy13', 'dummy14', 'dummy15', 'dummy16', 'dummy17'
                            , 'dummy18', 'dummy19','dummy20', 'dummy21', 'dummy22', 'dummy23', 'dummy24']
raw_tables = pd.DataFrame(columns=column_names)
total = len(df)

pattern = r'\bM{0,4}(CM|CD|D?C{0,3})?(XC|XL|L?X{0,3})?(IX|IV|V?I{0,3})\b'
def extract_roman_numerals(text):
    text = (re.sub(pattern,"", text, flags=re.IGNORECASE))
    text = text.replace(" ", "")
    text = text.replace(".", "")
    text = text.replace("(주)", "")
    text = text.replace("주석", "")
    text = text.replace("<", "")
    text = text.replace(">", "")
    text = text.replace("(", "")
    text = text.replace(")", "")
    text = text.replace(",", "")


    # new 아라비어숫자
    text = text.replace("Ⅰ", "")
    text = text.replace("Ⅱ", "")
    text = text.replace("Ⅲ", "")
    text = text.replace("Ⅳ", "")
    text = text.replace("Ⅴ", "")
    text = text.replace("Ⅵ", "")
    text = text.replace("Ⅶ", "")
    text = text.replace("Ⅷ", "")
    text = text.replace("Ⅸ", "")
    text = text.replace("Ⅹ", "")

    text = text.replace("I", "")
    text = text.replace("II", "")
    text = text.replace("III", "")
    text = text.replace("IV", "")

    text = text.replace("V", "")
    text = text.replace("VI", "")
    text = text.replace("VII", "")
    text = text.replace("VIII", "")


    text = text.replace("IX", "")
    text = text.replace("X", "")
    text = text.replace("I", "")
    text = text.replace("l", "")
    text = text.replace("/", "")
    text = text.replace("-", "")

    text = text.replace("와", "")
    text = text.replace(" ", "")



    return text

# table 태그 위치로 크롤링
unfitted_bnt = None
for idx, rept_no in enumerate(df['rcept_no']):


    if idx == 600:
        raw_tables['dummy2'] = raw_tables['dummy2'].apply(extract_roman_numerals)
        raw_tables.to_excel('part22.xlsx',index=False)
        raw_tables = pd.DataFrame(columns=column_names)

    try:
        # 웹접속
        driver = webdriver.Chrome(options=chrome_options)
        # driver = webdriver.Chrome()  # 테스트용 코드
        driver.get(f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rept_no}")

        elements = driver.find_elements(By.CLASS_NAME, "jstree-anchor")
        for elem in elements:
            text = elem.text.strip()
            if text == "기업개황자료":
                unfitted_bnt = True

                break

        if unfitted_bnt:
            unfitted_list.append(rept_no)
            print("기업개황임")
            unfitted_bnt = False
            continue

        # 목차 중 '재 무 제 표'라는 텍스트를 포함하는 걸 엔터
        target_section1 = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(normalize-space(text()), '재 무 제 표')]"))
        )
        target_section1[0].send_keys(Keys.ENTER)



        # iframe 전환
        iframe = driver.find_element(By.ID, "ifrm")
        driver.switch_to.frame(iframe)

        # html 에서 모든 table 가져오기
        table_elements = driver.find_elements(By.XPATH, '//table')
        # print("전체 테이블 요소: ",len(table_elements))

        # border = "1" 인 테이블들 찾기
        table_elements_bordered = [table for table in table_elements if table.get_attribute("border") == "1"]
        # print("재무제표 테이블 요소: ",len(table_elements_bordered))

        # 두 번째 border="1" table가 존재하는지 확인
        if len(table_elements_bordered) >= 2:
            second_bordered_table = table_elements_bordered[1]

            # boarder가 1인 두번째 테이블(=손익계산서)의 순서찾기
            all_tables = table_elements
            index_of_target = all_tables.index(second_bordered_table)
            # print("손익계산서 순서: ", index_of_target)


            if index_of_target > 0:
                # 손익계산서 앞에 등장하는 table요소 2개 가져오기
                previous_table1 = all_tables[index_of_target - 1]
                previous_table2 = all_tables[index_of_target - 2]

                # 전전에 위치한 테이블이 제무재표이면 패스
                if previous_table2 not in table_elements_bordered:
                    result_tables = [previous_table1, previous_table2, second_bordered_table]
                else:
                    result_tables = [previous_table1, second_bordered_table]

            else:
                result_tables = [second_bordered_table]  # 앞에 테이블이 없다면 손익계산서만 크롤링

        # 애초에 보더가 1인 두번째 테이블이 없다면 크롤링 실패
        else:
            unfitted_list.append(rept_no)
            break

        # print("-- 테이블 데이터 수집 시작, 테이블 수 = ", len(result_tables))
        # target_tables html 데이터 df로 변환


        for i, table in enumerate(result_tables):
            # print(f"{i}번째 테이블 수집 시작 --- ")
            html = table.get_attribute('outerHTML')

            soup = BeautifulSoup(html, 'html.parser')
            rows = soup.find_all('tr')  # tr요소를 rows로 불러오기

            tmp = []
            for row in rows:
                cols = row.find_all(['td', 'th'])
                col_list = [col.get_text(strip=True) for col in cols]

                col_list.insert(0, i)  # 테이블 순번 추가
                col_list.insert(0, rept_no)  # 접수번호 추가

                if len(col_list) < 25:
                    col_list += [None] * (25 - len(cols) - 2)
                else:
                    col_list = col_list[:25]
                tmp.append(col_list)
            tmp_df = pd.DataFrame(data=tmp, columns=column_names)
            raw_tables = pd.concat([raw_tables, tmp_df], axis=0)
    except Exception as e:
        error_list.append(rept_no)
        print(e)
        break
    finally:
        driver.quit()
        print(idx, "/", total, "-", round(idx / total * 100, 1), "%")
        continue


### 마무리 작업
# 로마자 제거 로직

raw_tables['dummy2'] = raw_tables['dummy2'].apply(extract_roman_numerals)


# 데이터 저장 -- unfitted_list와 error_list도 살펴볼 것
error_df = pd.DataFrame(error_list)
unfitted_df = pd.DataFrame(unfitted_list)

print(unfitted_list)


# 데이터 저장
raw_tables.to_excel("20250527.xlsx",index=False)
error_df.to_excel('error_df_20250526.xlsx',index=False)
unfitted_df.to_excel('unfitted_df_20250526.xlsx',index=False)