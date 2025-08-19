import os.path
import io
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# Google Drive API의 권한 범위(scope)를 지정합니다.
# 파일을 읽기만 할 것이므로 .readonly를 사용합니다.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


# -------------------------------------------------------------------
# Google Drive에 있는 실제 XLSX 파일 이름을 입력하세요.
FILE_NAME = "your_file_name.xlsx"  # 👈 여기를 수정하세요.
# -------------------------------------------------------------------


def main():
    """
    Google Drive API를 사용하여 XLSX 파일을 찾아 Pandas DataFrame으로 로드합니다.
    """
    creds = None
    # token.json 파일은 사용자의 액세스 및 새로고침 토큰을 저장합니다.
    # 인증 흐름이 처음 완료될 때 자동으로 생성됩니다.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # 유효한 자격 증명이 없으면 사용자가 로그인하도록 합니다.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # credentials.json 파일을 사용하여 인증 흐름을 시작합니다.
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # 다음 실행을 위해 자격 증명을 저장합니다.
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Google Drive API 서비스 객체를 생성합니다.
        service = build("drive", "v3", credentials=creds)

        # 1. 파일 이름으로 파일 ID 검색
        print(f"'{FILE_NAME}' 파일을 검색 중입니다...")
        response = (
            service.files()
            .list(
                q=f"name='{FILE_NAME}' and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'",
                spaces="drive",
                fields="files(id, name)",
            )
            .execute()
        )
        files = response.get("files", [])

        if not files:
            print(f"오류: '{FILE_NAME}' 파일을 찾을 수 없습니다. 파일 이름을 확인하거나 파일이 휴지통에 없는지 확인하세요.")
            return

        file_id = files[0]["id"]
        file_name = files[0]["name"]
        print(f"파일을 찾았습니다: {file_name} (ID: {file_id})")

        # 2. 파일 ID를 사용하여 파일 내용 다운로드
        request = service.files().get_media(fileId=file_id)
        # io.BytesIO를 사용하여 파일 내용을 메모리에 바이트 스트림으로 저장합니다.
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"다운로드 진행률: {int(status.progress() * 100)}%")

        # 스트림의 시작으로 커서를 이동합니다.
        file_content.seek(0)

        # 3. 메모리에 있는 파일 내용을 Pandas DataFrame으로 읽기
        print("\nPandas DataFrame으로 변환 중...")
        df = pd.read_excel(file_content, engine='openpyxl')

        print("\n✅ 파일 로드 성공!")
        print("DataFrame 상위 5개 행:")
        print(df.head())

    except HttpError as error:
        print(f"API 호출 중 오류가 발생했습니다: {error}")
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()
