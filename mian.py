# 📌 외부 모듈 불러오기
import pandas as pd
import requests
import json
import copy
import os
from dotenv import load_dotenv


##  xml 파일 로드 및 불러올때 사용
import xml.etree.ElementTree as ET
from zipfile import ZipFile
import io
from urllib.request import urlopen

import warnings
warnings.simplefilter("ignore")

# 📌 controller 불러오기
from app.controller.DartInfoController import  Company_info_finder


def main():
    load_dotenv()
    api_key = os.getenv("api_key")
    controller = Company_info_finder()

# 어플리케이션 초기화 및 메인 윈도우 실행
if __name__ == "__main__":
    main()

