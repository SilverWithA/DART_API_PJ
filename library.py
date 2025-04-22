#### 단축키 관련
# 주석처리 : ctrl + /
# 부분 실행 : alt + shift + E
# 다중 커서: Shift + alt + 드래그(마우스)

#####################################################
# 해당 문서에서는 기본 라이브러리 및 글로벌 변수 및 변수 업데이트 매서드만 정의합니다

# --------------------------------------------------------
# dart api 이용을 위한 기본 라이브러리 세팅

import pandas as pd
import requests
import xml.etree.ElementTree as ET
from zipfile import ZipFile
import io
from urllib.request import urlopen
# import csv
import json
import copy
import os

import warnings
warnings.simplefilter("ignore")

# --------------------------------------------------------
# dart api 키
api_key = '2ae5aede864cda8f26e03f216d7662056b0944d2'

# DART 내 기업개황 정보 xml 파일(글로벌에 정의해두고 사용할 것)



# dart 내 기업 개황 정보 업데이트 매서드
def update_corp_code():
    """DART 내 모든 기업개황정보 업데이트
    CORPCODE.xml 파일로 디렉토리에 저장됨"""

    # 고유번호 호출을 위한 url
    url =f'https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={api_key}'

    # dart 내 모든 회사 고유번호 xml 파일로 저장
    with urlopen(url) as zipresp:
        with ZipFile(io.BytesIO(zipresp.read())) as zfile:
            zfile.extractall('corp_num')

    # xml to df
    corp_code_df = pd.read_xml('corp_num/CORPCODE.xml',dtype=str)
    corp_code_df.to_excel('CORPCODE.xlsx',index=False)



########################################################


