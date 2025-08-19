import pandas as pd
import requests
import time
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

API_KEY = config['API_KEY']
BASE_ID = config['BASE_ID']
TABLE_NAME = config['TABLE_NAME']

url_get_records = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}/getRecords"
url_del_records = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}/deleteRecords"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def del_request(pkey_lst):
    print(f"Delete Target cnt: {len(pkey_lst)}")
#    print(pkey_lst)

    dic = {}
    dic['primaryKeysForDelete'] = pkey_lst

    try:
        time.sleep(0.3)
        response = requests.post(url_del_records, headers=headers, json=dic)
        response.raise_for_status()
        airtable_response = response.json()
        records_data = airtable_response.get('records', [])
 
    except requests.exceptions.RequestException as e:
        print(response)
    except (KeyError, IndexError) as e:
        print(f"❌ JSON 데이터 처리 중 에러 발생: 응답 형식을 확인하세요. ({e})")

def del_item(item_nms):
    i = 0
    pkey_lst = []
    for item in item_nms:
        pkey_lst.append(item)
        if len(pkey_lst) >= 50000:
            del_request(pkey_lst)
            pkey_lst = []

    del_request(pkey_lst)
    print(len(pkey_lst))
    #print(pkey_lst)
    print("----------------------length----------------------")
    print(len(pkey_lst))




def get_item_nm():
    
    dic={}
    arr=[]
    arr.append('Item')
    dic['fields'] = []
    print(arr)
    print(dic)
    
    result = []

    try:
        # POST 요청을 보냅니다.
        # 본문(payload)을 비워두면 모든 필드를 가져옵니다.
        response = requests.post(url_get_records, headers=headers, json=dic)
        
        #print(response)
        print(response.status_code)

        # HTTP 요청이 성공했는지 확인 (에러 시 예외 발생)
        response.raise_for_status()
    
        # JSON 응답을 파이썬 딕셔너리로 변환
        hdb_response = response.json()
        #print(hdb_response)
        
        # 실제 데이터는 'records' 키 안에 들어있습니다.
        records_data = hdb_response.get('records', [])
        for i in records_data:
            #print(i['primaryKey'])
            result.append(i['primaryKey'])
    
        # # 각 레코드의 'fields' 딕셔너리만 추출하여 리스트로 만듭니다.
        # data_for_df = [record['fields'] for record in records_data]
    
        # # 추출한 데이터로 Pandas DataFrame 생성
        # df = pd.DataFrame(data_for_df)
    
        # # 결과 확인
        # print("✅ 데이터프레임 생성 성공!")
        # print(df.head())
    
    except requests.exceptions.RequestException as e:
        print(response)
#        print(f"❌ API 요청 중 에러 발생: {e}")
    except (KeyError, IndexError) as e:
        print(f"❌ JSON 데이터 처리 중 에러 발생: 응답 형식을 확인하세요. ({e})")

    #print(result)
    print(f"Item cnt: {len(result)}")

    return result

def main():
    
    while True:
        item_nms = get_item_nm()
        if len(item_nms) == 0:
            print("모든 항목이 삭제되었습니다.")
            break

        del_item(item_nms)


if __name__ == "__main__":
    main()
