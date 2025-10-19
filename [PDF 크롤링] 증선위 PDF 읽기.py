import os
import zipfile
import pandas as pd
import pdfplumber


os.chdir('증선위')           # 위치변경
current_dir = os.getcwd()

# 압출풀기(1회실행 완료)
# for filename in os.listdir(current_dir):
#     if filename.endswith(".zip"):
#         zip_path = os.path.join(current_dir, filename)
#         with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#             # zip 이름을 기준으로 별도 폴더 생성해서 압축 해제
#             folder_name = os.path.splitext(filename)[0]
#             dest_path = os.path.join(current_dir, folder_name)
#             os.makedirs(dest_path, exist_ok=True)
#             zip_ref.extractall(dest_path)

### pdf 읽기
root_folers = os.listdir()    # 모든 파일 읽기
column_names = ['위원회 회차','파일명','dummy1','dummy2']
raw_tables = pd.DataFrame(columns=column_names)

for idx, root_folder in enumerate(root_folers):
    os.chdir(root_folder)   # 증권선물위원회 n차 폴더

    # 아래 있는 폴더를 돌면서 파일명에 '(의결서)'라는 텍스트가 있을 때만 text 추출
    sub_files = os.listdir()
    의결서_files = [item for item in sub_files if "(의결서)" in item]

    for 의결서_file in 의결서_files:
        total_text = []

        with pdfplumber.open(의결서_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                for text in text.splitlines():
                    total_text.append(text)

            for dummy_text in total_text:

                tmp = []
                col_list = [root_folder, 의결서_file]
                col_list.append(dummy_text)

                while len(col_list) < 4:
                    col_list.append("None")
                if len(col_list) > 4:
                    col_list = col_list[:4]

                tmp.append(col_list)
                tmp_df = pd.DataFrame(data=tmp, columns=column_names)
                raw_tables = pd.concat([raw_tables, tmp_df], axis=0)

    os.chdir('..')  # 상위로 돌아가기

raw_tables.to_excel('증선위 2024-2025_250722.xlsx',index=False)




