import os
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORP_CODE_PATH = os.path.join(BASE_DIR, r'corp_num\\CORPCODE.xml')

# XML 파일 파싱
CORP_CODE_XML = ET.parse(CORP_CODE_PATH)