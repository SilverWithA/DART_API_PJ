
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
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# 1. ChromeOptions 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 헤드리스 모드 활성화
chrome_options.add_argument("--disable-gpu")  # GPU 비활성화 (일부 환경에서 필요)
chrome_options.add_argument("--window-size=1920,3000")
import pandas as pd



#### 2. 결산 보고서인지 확인용 raw 수집
df = pd.read_excel('500대기업 소팅 감사보고서 매출액, 영업이익.xlsx',sheet_name='감사보고서 목록',dtype=str)
# is_final_df = df[df['결산여부']=='0']
#
# error_lst = []
#
# column_names = ['rcept_no','tr0','tr1','tr2','tr3']
# res_df = pd.DataFrame(columns=column_names)
# total = len(is_final_df)
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
rept_no= '20250508000219'


# 연결 아닌 녀석들 먼저 수집
df = df[df['연결여부'] != "1"]
df = df.iloc[:4000]
error_list = []

column_names = ['접수번호', '회사명', '테이블순번', 'dummy3', 'dummy4', 'dummy5', 'dummy6', 'dummy7', 'dummy8', 'dummy9'
                            , 'dummy10', 'dummy11', 'dummy12', 'dummy13', 'dummy14', 'dummy15', 'dummy16', 'dummy17'
                            , 'dummy18', 'dummy19','dummy20', 'dummy21', 'dummy22', 'dummy23', 'dummy24']

raw_tables = pd.DataFrame(columns=column_names)


total = len(df)

for idx, rept_no in enumerate(df['rcept_no']):
    print(idx,"/",total,"-", round(idx/total*100,1),"%")

    try:

        driver = webdriver.Chrome(options=chrome_options)
        # driver = webdriver.Chrome() # 테스트용 코드
        driver.get(f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rept_no}")

        # 손 익 계 산 서
        target_section = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(normalize-space(text()), '손 익 계 산 서')]"))
        )
        target_section[0].click()

        iframe = driver.find_element(By.ID, "ifrm")
        driver.switch_to.frame(iframe)

        table_elements = driver.find_elements(By.XPATH, '//table')
        for i,table in enumerate(table_elements):
            html = table.get_attribute('outerHTML')

            soup = BeautifulSoup(html, 'html.parser')

            rows = soup.find_all('tr')

            tmp = []
            for row in rows:
                cols = row.find_all(['td', 'th'])
                col_list = [col.get_text(strip=True) for col in cols]
                col_list.insert(0, i)
                col_list.insert(0, rept_no)

                if len(col_list) < 25:
                    col_list += [None] * (25 - len(cols)-2)
                else:
                    col_list = col_list[:25]
                tmp.append(col_list)
            tmp_df = pd.DataFrame(data= tmp, columns=column_names)
            raw_tables = pd.concat([raw_tables,tmp_df],axis=0)

    except:
        error_list.append(rept_no)
        driver.quit()
        continue
raw_tables.to_excel('raw 감사보고서 part1.xlsx', index=False)