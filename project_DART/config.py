import os
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

# 절대 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORP_CODE_PATH = os.path.join(BASE_DIR, r'CORPCODE.xml')
CORP_CODE_XML = ET.parse(CORP_CODE_PATH)        # XML 파일 파싱

# 보안 유지 필요한 상수 정의
load_dotenv()
api_key = os.getenv("api_key")


db_user = os.getenv("db_user")
db_pwd = os.getenv("db_pwd")
db_host = os.getenv("db_host")
db_port = os.getenv("db_port")

