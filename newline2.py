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

# 1. 데이터프레임 전체에서 '\n'을 찾아 빈 문자열 ''로 변경 (이 부분은 올바릅니다)
df_all.replace(r'\n', '', regex=True, inplace=True)

# 2. 모든 컬럼명을 문자열로 바꾼 뒤, '\n'을 공백 ' '으로 변경 (수정된 부분)
df_all.columns = df_all.columns.astype(str).str.replace(r'\n', ' ', regex=True)


print("\n--- 수정 후 ---")
print(df_all)
