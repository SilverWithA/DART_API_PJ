import library
# import '회사명으로 고유번호 및 종목코드 채우기'.py

df = pd.read_excel('2024년 기준 500대 기업.xlsx',sheet_name='2024_500대 기업')


# 매서드 적용
# 보충을 사용하는 이유: 사명이 바뀐 경우 반영
df['고유번호'] = df['다트기준 회사명'].apply(find_corp_num)


# 2025.03.11 추가
# 고유번호가 중복인 경우 리스트형으로 각 셀에 리스트형으로 저장되어있음
# (이때 확장하고자하는 셀은 '리스트'형으로 정의되어야 함)
df = df.explode('고유번호').reset_index(drop=True) # 리스트 값을 행으로 확장

# 빠진 항목 확인하기
def check_none_corp_code():
    missing_corpcode_list = []
    for index, unique_code in enumerate(df['고유번호']):
        if unique_code is None:
            missing_corpcode_list.append(df['회사명'][index])
    print(len(missing_corpcode_list))
    print(missing_corpcode_list)


df.to_excel('2024년 기준 500대 기업(고유번호 및 종목코드 포함).xlsx', index=False)


