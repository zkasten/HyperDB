import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# The scope allows the script to read Drive metadata.
# Using .readonly is sufficient and safer for listing.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def main():
    """
    Lists all Shared Drives the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    # It's created automatically when the authorization flow completes for the first time.
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
        # Build the Google Drive API service
        service = build("drive", "v3", credentials=creds)

        # Call the Drives V3 API to list Shared Drives
        print("Fetching list of Shared Drives...")
        response = service.drives().list().execute()
        print(response)
        drives = response.get("drives", [])

        if not drives:
            print("No Shared Drives found.")
            return

        print("\n--- Accessible Shared Drives ---")
        for drive in drives:
            # Print the name and ID of each Shared Drive
            print(f"  - Name: {drive['name']}, ID: {drive['id']}")
        print("------------------------------")


    except HttpError as error:
        print(f"An API error occurred: {error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
