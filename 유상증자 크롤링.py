# 유상증자 파일 내 자료 크롤링 테스트
# 마우스를 통해 요소를 찾고 해당 데이터를 저장하는 방식
import pandas as pd
### 마우스크롤링
# (1) 엑셀 내에서 하이퍼링크 추출
# (2) 하이퍼링크 접속하여 유상증자 결정 표 아래 요소 추출
## - 요소 추출시 컬럼명 - 데이터값과 함께 크롤링되도록 정리
## - 표 형식으로 나열된 정보만 크롤링하도록 정의


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ECd
import time

df = pd.read_excel('')

for idx, url in enumerate(df['url']):
    stock_code = df['종목코드'][idx]

    # 1. DART 접속
    driver = webdriver.Chrome()                     # 웹드라이버 실행
    # driver.get(url)                                 # 웹페이지 접속
    driver.get("https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20240729800280")
    time.sleep(2)

    driver.close()


    #

