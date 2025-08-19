import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# API 권한 범위(scope)를 지정합니다.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def main():
    """
    페이지네이션을 처리하여 사용자가 접근할 수 있는 모든 공유 드라이브 목록을 출력합니다.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("drive", "v3", credentials=creds)

        print("모든 공유 드라이브 목록을 가져오는 중입니다 (페이지네이션 처리 중)...")
        
        all_drives = []
        page_token = None

        # nextPageToken이 없을 때까지 루프를 계속 실행합니다.
        while True:
            # Drives V3 API를 호출하여 공유 드라이브 목록을 가져옵니다.
            # pageToken 파라미터를 요청에 포함시킵니다.
            response = service.drives().list(
                pageToken=page_token,
                pageSize=100  # 한 번에 가져올 개수 (최대 100)
            ).execute()

            drives = response.get("drives", [])
            all_drives.extend(drives)

            # 응답에서 다음 페이지 토큰을 가져옵니다.
            page_token = response.get("nextPageToken", None)
            
            # 다음 페이지 토큰이 없으면 루프를 종료합니다.
            if page_token is None:
                break

        if not all_drives:
            print("접근할 수 있는 공유 드라이브를 찾을 수 없습니다.")
        else:
            print(f"\n--- 📂 총 {len(all_drives)}개의 공유 드라이브를 찾았습니다 ---")
            for drive in all_drives:
                print(f"  - 이름: {drive['name']}, ID: {drive['id']}")
            print("-----------------------------------------")


    except HttpError as error:
        print(f"API 호출 중 오류가 발생했습니다: {error}")
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()
