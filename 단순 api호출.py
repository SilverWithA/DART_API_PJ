import pandas as pd
import requests



df = pd.read_excel('krx 상장사 고유번호3.xlsx', dtype={"고유번호":str, "종목코드":str})


# 유상증자 결정 api
def 유상증자_콜렉팅(df, cnt = 0):
    url = "https://opendart.fss.or.kr/api/piicDecsn.json"


    res_df = pd.DataFrame(columns=['rcept_no', 'corp_cls', 'corp_code', 'corp_name', 'nstk_ostk_cnt',
           'nstk_estk_cnt', 'fv_ps', 'bfic_tisstk_ostk', 'bfic_tisstk_estk',
           'fdpp_fclt', 'fdpp_bsninh', 'fdpp_op', 'fdpp_dtrp', 'fdpp_ocsa',
           'fdpp_etc', 'ic_mthn', 'ssl_at', 'ssl_bgd', 'ssl_edd'])

    print(" --- 유상증자 결정 정보를 불러오는 중...")

    # corp_code = "00126380"
    cnt = 0
    for index, corp_code in enumerate(df['고유번호']):
        cnt += 1
        if corp_code is None:
            print(df['종목명'][index], "는 고유번호로 유상증자 정보를 찾을 수 없습니다.")
            continue
        try:
            params = {"crtfc_key": api_key,
                  "corp_code": corp_code,
                  "bgn_de":'20200407',
                  "end_de":"20220406"}


            res = requests.get(url, params=params)
            data = res.json()

            if data['message'] == '조회된 데이타가 없습니다.':
                continue

            if data['list']:
                tmp = pd.DataFrame(data['list'])
                res_df = pd.concat([res_df, tmp], ignore_index=True)

            cnt += 1
        except Exception as e:
            print(e, end=' ')
            print(df['종목명'][index], "의 유상증자 결정 호출중 에러가 발생했습니다.")

    print("총 ", cnt,"개 사의 유상증자 결정 정보를 모았습니다.")
    return res_df

res_df = 유상증자_콜렉팅(df)
res_df.to_excel('2개년 유상증자결정 콜렉팅_20250408.xlsx')



# corp_code = "01351080"
def 유무상증자_콜렉팅(df, cnt = 0):
    url = "https://opendart.fss.or.kr/api/pifricDecsn.json"

    res_df = pd.DataFrame(columns=['rcept_no', 'corp_cls', 'corp_code', 'corp_name', 'piic_nstk_ostk_cnt',
       'piic_nstk_estk_cnt', 'piic_fv_ps', 'piic_bfic_tisstk_ostk',
       'piic_bfic_tisstk_estk', 'piic_fdpp_fclt', 'piic_fdpp_bsninh',
       'piic_fdpp_op', 'piic_fdpp_dtrp', 'piic_fdpp_ocsa', 'piic_fdpp_etc',
       'piic_ic_mthn', 'fric_nstk_ostk_cnt', 'fric_nstk_estk_cnt',
       'fric_fv_ps', 'fric_bfic_tisstk_ostk', 'fric_bfic_tisstk_estk',
       'fric_nstk_asstd', 'fric_nstk_ascnt_ps_ostk', 'fric_nstk_ascnt_ps_estk',
       'fric_nstk_dividrk', 'fric_nstk_dlprd', 'fric_nstk_lstprd', 'fric_bddd',
       'fric_od_a_at_t', 'fric_od_a_at_b', 'fric_adt_a_atn', 'ssl_at',
       'ssl_bgd', 'ssl_edd'])

    print(" --- 유무상증자 결정 정보를 불러오는 중...")
    for index, corp_code in enumerate(df['고유번호']):

        if corp_code is None:
            print(df['종목명'][index], "는 고유번호로 유상증자 정보를 찾을 수 없습니다.")
            continue
        try:
            params = {"crtfc_key": api_key,
                  "corp_code": corp_code,
                  "bgn_de":'20200407',
                  "end_de":"20220406"}


            res = requests.get(url, params=params)
            data = res.json()

            if data['message'] == '조회된 데이타가 없습니다.':
                continue

            if data['list']:
                tmp = pd.DataFrame(data['list'])
                res_df = pd.concat([res_df, tmp], ignore_index=True)

            cnt += 1
        except Exception as e:
            print(e, end=' ')
            print(df['종목명'][index], "의 유상증자 결정 호출중 에러가 발생했습니다.")

    print("총 ", cnt,"개 사의 유무상증자 결정 정보를 모았습니다.")
    return res_df


유무상_df = 유무상증자_콜렉팅(df)
유무상_df.to_excel('2개년 유무상증자 콜렉팅.xlsx')