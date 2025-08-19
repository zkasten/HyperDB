import pandas as pd

# 여러 열에 '\n'이 포함된 샘플 데이터프레임
data = {
    '제품\n명': ['삼성\n노트북', 'LG\n모니터'],
    1: ['삼성\n노트북', 'LG\n모니터'],
    '특\n징': ['2025년\n최신형', '고화질\n디스플레이']
}
df_all = pd.DataFrame(data)


print("--- 원본 ---")
print(df_all)

# 데이터프레임 전체에서 '\n'을 찾아 빈 문자열 ''로 변경
df_all.replace(r'\n', '', regex=True, inplace=True)

df_all.columns = df_all.columns.str.replace('\n', ' ', regex=False)

print("\n--- 뉴라인 제거 후 ---")
print(df_all)
