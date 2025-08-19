import os
import json
import pandas as pd
import requests
import time
import numpy as np
from datetime import datetime

import os.path
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

config = configparser.ConfigParser()
config.read('config.ini')

API_KEY = config['API_KEY']
BASE_ID = config['BASE_ID']
TABLE_NAME = config['TABLE_NAME']
                    
url_set_records = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}/upsertRecords"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    """Google Drive API 서비스 객체를 생성하고 반환합니다."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def get_file_id_from_shared_drive(service, drive_id: str, full_path: str):
    """공유 드라이브 내에서 전체 경로를 이용해 파일 ID를 찾습니다."""
    path_parts = [part for part in full_path.split('/') if part]
    if not path_parts:
        print("오류: 파일 경로가 비어있습니다.")
        return None

    parent_id = drive_id  # 검색 시작점을 공유 드라이브의 ID로 설정
    current_item_id = None

    try:
        for part_name in path_parts:
            query = f"'{parent_id}' in parents and name='{part_name}' and trashed=false"
            
            response = service.files().list(
                q=query,
                # ⭐️ 공유 드라이브 검색을 위한 필수 파라미터 ⭐️
                driveId=drive_id,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                corpora='drive',
                fields='files(id, name)'
            ).execute()
            
            files = response.get('files', [])

            if not files:
                print(f"오류: 경로에서 '{part_name}'을(를) 찾을 수 없습니다.")
                return None
            
            current_item_id = files[0]['id']
            parent_id = current_item_id

        return current_item_id

    except HttpError as error:
        print(f"파일 검색 중 API 오류 발생: {error}")
        return None
    
def get_shared_drive_id(service, drive_name):
    """이름으로 공유 드라이브를 찾아 ID를 반환합니다."""
    page_token = None
    while True:
        response = service.drives().list(
            q=f"name = '{drive_name}'",
            fields='nextPageToken, drives(id, name)',
            pageToken=page_token
        ).execute()
        drives = response.get('drives', [])
        if drives:
            return drives[0]['id']
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return Non
                 
def find_folder_id_in_path(service, drive_id, path):
    """공유 드라이브 내에서 경로를 따라 폴더 ID를 찾습니다."""
    path_parts = [part for part in path.split('/') if part]
    current_folder_id = drive_id  # 검색 시작점은 공유 드라이브의 루트

    for folder_name in path_parts:
        page_token = None
        found_in_level = False
        while True:
            response = service.files().list(
                q=f"name = '{folder_name}' and '{current_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'",
                driveId=drive_id,
                corpora='drive',
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='nextPageToken, files(id, name)',
                pageToken=page_token
            ).execute()
            
            files = response.get('files', [])
            if files:
                current_folder_id = files[0]['id']
                found_in_level = True
                break
            
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        
        if not found_in_level:
            print(f"경로 '{path}'에서 '{folder_name}' 폴더를 찾지 못했습니다.")
            return None
            
    return current_folder_id

def upsert_item(record):
#    print(json.dumps(record))
    time.sleep(0.3)
    try:
        
        response = requests.put(url_set_records, headers=headers, data=json.dumps(record))
        print(response)
        print(response.status_code)
        
        hdb_response = response.json()
        print(hdb_response)
    
        records = hdb_response.get('records', [])
        print(records)
              
    
    except requests.exceptions.RequestException as e:
        print(response.status_code)
    except (KeyError, IndexError) as e:
        print(f"❌ JSON 데이터 처리 중 에러 발생: 응답 형식을 확인하세요. ({e})")
    

def process():

    location = "TX"
    date = "072825"
    category = "ASIAN"
    #df = pd.DataFrame(pd.read_excel("ASIAN_CA_PO_Suggest_DEV.xlsx"))
    df = pd.DataFrame(pd.read_excel("ASIAN_TX_PO_Suggest.xlsx"))
    #df = pd.DataFrame(pd.read_excel("ASIAN_GA_PO_Suggest.xlsx"))
    
    df['Item'] = pd.to_numeric(df['Item'], errors='coerce')
    df = df.dropna(subset=['Item'])
    df = df.reset_index(drop=True)
    
    
    
#    drop_idx = df[df['Item'] == 'INVADJGROASIAN'].index
#    drop_idx = df[df['Item'] == 'INVADJGROWTN'].index
#    drop_idx = df[df['Item'] == 'INVADJGROCHI'].index
#    if not drop_idx.empty:
#        df = df.drop(drop_idx)
#    
#    df = df.dropna(subset=['Item'])
    
    df['Item'] = df['Item'].astype(int)
    df['Item'] = df['Item'].astype(str)
    df['Location'] = location
    df['Date'] = date
    df['Category'] = category
    
    
    df = df.fillna('')
    #print(df.columns)
    #for col in df.columns:
    #    print(f"Column: {col}, Type: {df[col].dtype}")
        
    #df.columns = df.columns.str.replace(r'\n', ' ', regex=True)
    df.columns = df.columns.astype(str).str.replace(r'\n', ' ', regex=True)
    df.columns = df.columns.astype(str).str.replace(r'\s+', ' ', regex=True)
    df = df.astype(str)
    
    cols_to_drop = df.columns[df.columns.str.contains('210')]
    df = df.drop(columns=cols_to_drop)
    
    record = {}
    record_arr = []
    i = 0
    for index, row in df.iterrows():
        dic = {}
        #dic["primaryKey"] = str(row["Item"])
        dic["primaryKey"] = location + "_" + date + "_" + str(row["Item"])
        dic["fields"] = row.to_dict()
        #print(dic)
        record_arr.append(dic)
        i += 1
        if i > 799:
            print(f"Upserting {len(record_arr)} records...")
            record["records"] = record_arr
            upsert_item(record)
            record_arr = []
            record = {}
            i = 0
    
    print(f"Upserting {len(record_arr)} records...")
    record["records"] = record_arr
    upsert_item(record)
    #record["records"] = [{"primaryKey": "1314101085", "fields": {"Item": "1314101085", "Description": "NATURES GRAIN COOKED WHITE RICE "}}, {"primaryKey": "1314101086", "fields": {"Item": "1314101086", "Description": "NATURES GRAIN COOKED WHITE RICE NEW "}}]
    #record["records"] = [{"primaryKey": "1314101085", "fields": {"Item": "1314101085", "Description": "NATURES GRAIN COOKED WHITE RICE 7.4OZ(210G)/12/1 \uc790\uc5f0\ubbf8 \ud55c\uad6d\uc0b0 \ud770\uc300\ubc25 12PK NEW", "Report Category": 0.0, "\ubbf8\ucde8\uae09\nTOSS\n\uc9c0\uc790\uccb4": 0.0, "B1\n4wks": 1360.5, "B1\n13Wk": 1323.15, "S\n4wks": 1410.75, "S\n13wks": 1157.38, "TR\n4wks": 0.0, "TR\n13wks": 0.0, "B1": "", "7": 938.23, "8": 1384.37, "9": 1513.4, "10": 489.53, "11": 1767.73, "12": 1459.03, "1": 889.0, "2": 398.77, "3": 1437.33, "4": 896.23, "5": 1062.6, "6": 1762.83, "S": "", "7.1": 653.8, "8.1": 1048.83, "9.1": 1165.27, "10.1": 526.4, "11.1": 1147.77, "12.1": 1013.83, "1.1": 799.4, "2.1": 311.97, "3.1": 1030.4, "4.1": 635.13, "5.1": 850.97, "6.1": 1540.0, "Buyer's \nDecision": 1360.5, "Stock \nQty": 6734.0, "Case/Pallet": 0.0, "Stock Pallet Qty": 0.0, "On-order \nQty": 12480.0, "Cur \n Turn Over": 14.1227489893422, "\ud604\uc7ac\uace0 \n Turn Over": 4.94965086365307, "Suggested \nOrder Qty": 0.0, "Actual Order \nGSC Qty": "", "Buyer \nOpinion": "", "\ub3c4\ucc29\uc2dc Turn Over(week)": 14.1227489893422, "Lead Time \n(Week)": 0.0, "\ucd5c\uc18c\uc7ac\uace0\n(Week)": 0.0, "\ubc1c\uc8fc\ub2e8\uc704\n(Week)": 0.0, "Max\uc7ac\uace0\n(Week)": 0.0, "ReOrder Point \n(Week)": 0.0, "buyer": 0.0, "categoryL1": "INSTANT RICE, CUP RICE", "UPC": 84603401489.0, "Free": "", "On Order": "", "CW": 0.0, "C+1W": 0.0, "C+2W": 0.0, "C+3W": 0.0, "C+4W": 0.0, "C+5W": 4920.0, "C+6W": 0.0, "C+7W": 5040.0, "C+8W": 0.0, "C+9W": 0.0, "C+10W": 0.0, "C+11W": 0.0, "C+12W": 2520.0, "C+13W": 0.0, "C+14W": 0.0, "C+15W": 0.0, "C+16W": 0.0, "C+17W": 0.0, "C+18W": 0.0, "C+19W": 0.0, "C+20W": 0.0, "C+21W": 0.0, "C+22W": 0.0, "After 22W": 0.0, "INV\nFCST": "", "CW.1": 5373.5, "C+1W.1": 4013.0, "C+2W.1": 2652.5, "C+3W.1": 1292.0, "C+4W.1": 0.0, "C+5W.1": 3559.5, "C+6W.1": 2199.0, "C+7W.1": 5878.5, "C+8W.1": 4518.0, "C+9W.1": 3157.5, "C+10W.1": 1797.0, "C+11W.1": 436.5, "C+12W.1": 1596.0, "C+13W.1": 235.5, "C+14W.1": 0.0, "C+15W.1": 0.0, "C+16W.1": 0.0, "C+17W.1": 0.0, "C+18W.1": 0.0, "C+19W.1": 0.0, "C+20W.1": 0.0, "C+21W.1": 0.0, "C+22W.1": 0.0, "PO": "", "210678826": 0, "210275906": 0, "210672824": 0, "210680517": 0, "210679779": 0, "210673606": 0, "210671918": 0, "210677169": 0, "210677166": 0, "210677462": 0, "210677163": 0, "210677170": 0, "210275700": 0, "210678101": 0, "210680492": 0, "210680922": 0, "210680923": 0, "210672823": 0, "210678828": 0, "210676604": 0, "210677881": 0, "210677878": 0, "210676603": 0, "210672814": 0, "210672355": 0, "210672072": 0, "210672352": 0, "210677446": 0, "210275701": 0, "210672509": 0, "210680493": 0, "210275702": 0, "210678486": 0, "210674066": 0, "210679537": 0, "210674825": 0, "210679360": 0, "210678829": 0, "210677746": 0, "210678137": 0, "210678139": 0, "210676977": 0, "210676976": 0, "210678134": 0, "210678135": 0, "210670485": 0, "210678107": 0, "210670490": 0, "210672819": 0, "210677153": 0, "210679671": 0, "210676607": 0, "210678509": 0, "210679361": 0, "210679538": 0, "210677182": 0, "210680004": 0, "210679177": 0, "210678115": 0, "210677691": 0, "210677454": 0, "210677675": 0, "210677703": 0, "210678385": 0, "210677088": 0, "210680821": 0, "210673106": 0, "210673088": 0, "210673101": 0, "210673096": 0, "210673099": 0, "210673104": 0, "210673107": 0, "210673089": 0, "210673103": 4920, "210673105": 0, "210677702": 0, "210680320": 0, "210680323": 0, "210680335": 0, "210680336": 0, "210266277": 0, "210680516": 0, "210680513": 0, "210679720": 0, "210680338": 0, "210677448": 0, "210680337": 0, "210680340": 0, "210680322": 0, "210266274": 0, "210680707": 0, "210679539": 0, "210677912": 0, "210679540": 0, "210678116": 0, "210677455": 0, "210674861": 0, "210679724": 0, "210677452": 0, "210675948": 0, "210675852": 0, "210675846": 0, "210675853": 0, "210675856": 0, "210675857": 0, "210675851": 0, "210675947": 0, "210675850": 0, "210675949": 0, "210675858": 0, "210675845": 0, "210675860": 0, "210675855": 0, "210675854": 5040, "210677458": 0, "210268493": 0, "210268490": 0, "210268495": 0, "210268496": 0, "210268494": 0, "210268497": 0, "210678158": 0, "210679756": 0, "210679754": 0, "210679753": 0, "210679757": 0, "210679749": 0, "210680296": 0, "210680318": 0, "210680300": 0, "210680319": 0, "210680317": 0, "210680294": 0, "210680312": 0, "210680292": 0, "210680316": 0, "210680315": 0, "210680314": 0, "210680303": 0, "210680307": 0, "210680306": 0, "210680308": 2520, "210273840": 0}}]
    

def main():
    today = datetime.now()
    FORMATTED_DATE = today.strftime("%m%d%y")
#    FORMATTED_DATE = "081825"
    SHARED_DRIVE_NAME = config['SHARED_DRIVE_NAME']
    FOLDER_PATH_IN_DRIVE = config['FOLDER_PATH_IN_DRIVE']
    FOLDER_PATH_IN_DRIVE_SEAFOOD = config['FOLDER_PATH_IN_DRIVE_SEAFOOD']
    target_info = {}
    target_info['type'] = ['ASIAN', 'CHINESE', 'WESTERN']
    target_info['region'] = ['NJ', 'CA', 'GA', 'IL', 'MD', 'TX']
    
    drive_service = get_drive_service()
    drive_id = get_shared_drive_id(drive_service, SHARED_DRIVE_NAME)
    print(f"- Info: Drive Name : {SHARED_DRIVE_NAME}")
    print(f"- Info: Drive ID : {drive_id}")
    print(f"- Info: DATE : {FORMATTED_DATE}")
    
    files = []
    files.append(f"{FOLDER_PATH_IN_DRIVE_SEAFOOD}/{FORMATTED_DATE}/SF_PO_Suggest.xlsx")
    for type in target_info['type']:
        for region in target_info['region']:
            files.append(f"{FOLDER_PATH_IN_DRIVE}/{FORMATTED_DATE}/{type}/{type}_{region}_PO_Suggest.xlsx")
    
    file_ids = {}
    if drive_id:
        for file in files:
            file_id = get_file_id_from_shared_drive(drive_service, drive_id, file)
            if file_id:
                file_ids[file] = file_id
                print(f"- Info: File ID for {file}: {file_id}")
            else:
                print(f"- ERR: File not found: {file}")
    else:
        print(f"- ERR: '{SHARED_DRIVE_NAME}' Cannot find the drive.")
        return
        
    tmp_id = "1pIixS6FTf5umsccucULuey6YfcC3ZkKj"
    
    for file_name, file_id in file_ids.items():
        
        print(f"- Info: File Name: {file_name}")
        print(f"- Info: File ID: {file_id}")
        tmp_arr = file_name.split('/')
        name_arr = tmp_arr[-1].split('_')
        print(name_arr[0], name_arr[1], name_arr[2])
        
        request = drive_service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(tmp_arr[4])
            print(f"다운로드 진행률: {int(status.progress() * 100)}%")

        file_content.seek(0)
        df = pd.DataFrame(pd.read_excel(file_content, engine='openpyxl'))
        df = df.fillna('')
        df['Item'] = pd.to_numeric(df['Item'], errors='coerce')
        df = df.dropna(subset=['Item'])
        df = df.reset_index(drop=True)
        df['Item'] = df['Item'].astype(int)
        df.columns = df.columns.astype(str).str.replace(r'\n', ' ', regex=True)
        df.columns = df.columns.astype(str).str.replace(r'\s+', ' ', regex=True)
        df = df.astype(str)

        cols_to_drop = df.columns[df.columns.str.contains('210')]
        df = df.drop(columns=cols_to_drop)
        
        #df['Item'] = df['Item'].astype(int)
        #df['Item'] = df['Item'].astype(str)

        df['Date'] = FORMATTED_DATE 
        if name_arr[0] == 'SF':
            df['Category'] = 'SEAFOOD'
            #df.rename(columns={'Lead Time': 'Lead Time (Week)'}, inplace=True)
            df.rename(columns={'Max 재고 (Week)': 'Max재고 (Week)', '발주 단위 (Week)': '발주단위 (Week)', '최소 재고 (Week)': '최소재고 (Week)', 'Lead Time': 'Lead Time (Week)', '도착시 Turn Over': '도착시 Turn Over(week)'}, inplace=True)
        else:
            df['Category'] = name_arr[0]
            df['Location'] = name_arr[1]
            
        record = {}
        record_arr = []
        i = 0
        for index, row in df.iterrows():
            dic = {}
            #dic["primaryKey"] = str(row["Item"])
            dic["primaryKey"] = name_arr[1] + "_" + FORMATTED_DATE + "_" + str(row["Item"])
            dic["fields"] = row.to_dict()
            # Test
            #print(dic)
            record_arr.append(dic)
            #break
            i += 1
            if i > 799:
                print(f"Upserting {len(record_arr)} records...")
                record["records"] = record_arr
                upsert_item(record)
                record_arr = []
                record = {}
                i = 0
        
        print(f"Upserting {len(record_arr)} records...")
        record["records"] = record_arr
        upsert_item(record)

                                                      



if __name__ == "__main__":
    main() 
