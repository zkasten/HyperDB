from datetime import datetime

# 현재 날짜와 시간 가져오기
today = datetime.now()

# 'ddmmyy' 형식으로 변환
formatted_date = today.strftime("%m%d%y")

print(formatted_date)
# 예시 출력: 310725

