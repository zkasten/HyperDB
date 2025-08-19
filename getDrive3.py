import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# API 권한 범위(scope)를 지정합니다. .readonly로도 충분합니다.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def main():
    """
    사용자가 접근할 수 있는 모든 공유 드라이브의 목록을 출력합니다.
    """
    creds = None
    # token.json 파일은 사용자의 액세스 토큰과 리프레시 토큰을 저장합니다.
    # 인증 흐름이 처음 완료될 때 자동으로 생성됩니다.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # 유효한 자격 증명이 없으면 사용자가 로그인하도록 합니다.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # 다음 실행을 위해 자격 증명을 저장합니다.
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Google Drive API 서비스 객체를 생성합니다.
        service = build("drive", "v3", credentials=creds)

        print("공유 드라이브 목록을 가져오는 중입니다...")
        
        # Drives V3 API를 직접 호출하여 공유 드라이브 목록을 가져옵니다.
        response = service.drives().list().execute()
        drives = response.get("drives", [])

        if not drives:
            print("접근할 수 있는 공유 드라이브를 찾을 수 없습니다.")
            return

        print("\n--- 📂 접근 가능한 공유 드라이브 ---")
        for drive in drives:
            # 각 공유 드라이브의 이름과 ID를 출력합니다.
            print(f"  - 이름: {drive['name']}, ID: {drive['id']}")
        print("---------------------------------")


    except HttpError as error:
        print(f"API 호출 중 오류가 발생했습니다: {error}")
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()
