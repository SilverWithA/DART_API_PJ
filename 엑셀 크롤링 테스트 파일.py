# ⚠️ 문제점(1): 수기로 직접 순차실행하는 것이 아니라 함수로 만들었을 때 에러발생 + time.sleep()
# ⚠️ 문제점(2): 임원 현황 전체선택 + 복사하기 부분에서 브라우저 화면 클릭 작동이 각 문서마다 오락가락함
# ---------------------------------------------------


## 공시보고서 내 임원현황 데이터 raw를 긁어오는 테스트 코드임

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
# import openpyxl           # 엑셀 백그라운드 실행
import win32com.client      # 엑셀 파일 경합할시 오류발생
import os

import pandas as pd
df = pd.read_excel('삼성 계열사.xlsx',sheet_name='2024 삼성 계열사 목록',
                   dtype={'종목코드':str})


for idx, corp_name in enumerate(df['회사명']):
    stock_code = df['종목코드'][idx]

    # 1. DART 접속
    driver = webdriver.Chrome()                     # 웹드라이버 실행
    driver.get("https://dart.fss.or.kr/main.do")    # 웹페이지 접속
    time.sleep(2)
    # 1. 검색창에 키워드 입력
    search_box = driver.find_element(By.ID, "textCrpNm2")  # 검색창 ID에 맞게 수정
    search_box.send_keys(stock_code)

    # 2. 토글(검색 조건) 선택
    # 정기공시 탭열기
    regular_report_btn = driver.find_element(By.ID, "li_01")  # 실제 ID나 XPath 수정
    regular_report_btn.click()
    # 정기공시 중 사업보고서 토글 클릭
    annual_report_btn = driver.find_element(By.ID, "publicTypeDetail_A001")  # 실제 ID나 XPath 수정
    annual_report_btn.click()
    # Enter 키 입력하여 검색 실행
    search_box.send_keys(Keys.ENTER)
    time.sleep(1)
    # 3. 조사기간 토글 클릭
    period_10y_btn = driver.find_element(By.ID, "date7")  # 실제 ID나 XPath 수정
    period_10y_btn.click()
    # 검색어 재입력후 Enter작업으로 처리
    search_box1 = driver.find_element(By.ID, "textCrpNm")  # 검색창 ID에 맞게 수정
    search_box1.clear()
    search_box1.send_keys(stock_code)
    ActionChains(driver).send_keys(Keys.RETURN).perform()
    time.sleep(1)
    # 4. 원본 공시보고서 열기
    # 공시보고서 항목 찾기
    report_sections = WebDriverWait(driver, 2).until(
        EC.presence_of_all_elements_located((By.XPATH, "//a[contains(normalize-space(text()), '사업보고서')]"))
    )



    file_name = f'raw {corp_name} 임원 현황.xlsx'
    excel_file_path = rf'C:\Users\HP\OneDrive\바탕 화면\crawling test\임원 현황 raw\{file_name}'


    # 공시보고서 항목 클릭
    for section in report_sections:
        section.click()

        # 현재 열린 창 목록 확인
        window_handles = driver.window_handles
        # 새롭게 열린 팝업 창으로 전환 (기존 창은 window_handles[0])
        driver.switch_to.window(window_handles[-1])
        sheet_name = str(driver.title.replace('/', '_'))
        # 임원에 관한 사항 열기
        director_section = WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(normalize-space(text()), '임원 및 직원')]"))
        )
        director_section[0].click()



        # ActionChains 생성
        actions = ActionChains(driver)

        actions.move_to_element(director_section[0]).perform()  # 요소 위로 이동

        # 현재 창 크기
        window_width = driver.execute_script("return window.innerWidth")
        window_height = driver.execute_script("return window.innerHeight")

        max_x = window_width - 1
        max_y = window_height - 1

        x = min(300, max_x)  # 300이 화면 너비를 초과하지 않도록 조정
        y = min(200, max_y)  # 200이 화면 높이를 초과하지 않도록 조정

        actions.move_by_offset(100, -100).click().perform()
        actions.move_by_offset(100, -100).click().perform()
        time.sleep(1)
        actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()    # 전체선택
        time.sleep(1)
        actions.key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()    # 복사하기

        try:
            # 엑셀 열기
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = False  # 엑셀을 눈에 보이게 실행 (테스트용)

            # 파일이 존재하는지 확인
            if os.path.exists(file_name):
                # 파일이 존재하면 열기
                wb = excel.Workbooks.Open(excel_file_path)
            else:
                # 파일이 없으면 새로 만들기
                wb = excel.Workbooks.Add()  # 새 워크북 생성
                wb.SaveAs(excel_file_path)

            # 시트 생성
            ws = wb.Worksheets.Add()

            # 시트 이름 변경
            try:
                ws.Name = str(driver.title).replace('/', '_')
            except:
                # 느림
                print("해당 이름을 가진 데이터가 존재합니다.")
                ws.Name = "new_" + str(driver.title).replace('/', '_')


            ws.Range("A1").Select()  # 복붙
            ws.PasteSpecial()  # 클립보드에서 HTML 서식 포함
        except:
            pass

        wb.Save()
        driver.close()
        # 원래 창으로 다시 전환
        driver.switch_to.window(window_handles[0])

    wb.Close()
    driver.quit() # 드라이버 닫기
    print(corp_name, "사의 임원 현황 크롤링 작업이 완료되었습니다.")

