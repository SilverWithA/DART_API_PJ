import os
import xml.etree.ElementTree as ET

# 절대 결로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORP_CODE_PATH = os.path.join(BASE_DIR, r'corp_num\\CORPCODE.xml')
CORP_CODE_XML = ET.parse(CORP_CODE_PATH)        # XML 파일 파싱