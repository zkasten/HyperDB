import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# The scope must allow at least read-only access to Drive files.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def main():
    """Lists folders from the user's "Shared with me" section."""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("drive", "v3", credentials=creds)
        all_folders = []
        page_token = None

        print("Fetching list of shared folders...")

        # Loop to handle pagination
        while True:
            # This query finds items that are shared with the user and are folders.
            response = service.files().list(
                q="sharedWithMe and mimeType='application/vnd.google-apps.folder'",
                spaces='drive',
                fields='nextPageToken, files(id, name, owners)',
                pageToken=page_token
            ).execute()

            folders = response.get('files', [])
            all_folders.extend(folders)

            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        if not all_folders:
            print("No shared folders found.")
        else:
            print("\n--- Shared Folders Found ---")
            for folder in all_folders:
                owner_list = [owner['displayName'] for owner in folder.get('owners', [])]
                owners_str = ", ".join(owner_list)
                print(f"  - Name: {folder['name']}, Owner: {owners_str}, ID: {folder['id']}")
            print("----------------------------")

    except HttpError as error:
        print(f"An API error occurred: {error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    main()
