import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv
load_dotenv()
# Load environment variables from .env file

sheet_id = os.getenv('SHEET_ID')
if not sheet_id:
    raise ValueError("Google Sheet ID .env faylda topilmadi!")
sheet_name = os.getenv('SHEET_NAME')
if not sheet_name:
    raise ValueError("Google Sheet name .env faylda topilmadi!")


def get_google_sheets_client():
    creds = Credentials.from_service_account_file('credentionals.json', 
                                                  scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    return client


def get_google_sheet():
    client = get_google_sheets_client()
    sheet = client.open_by_key(sheet_id)
    return sheet.get_worksheet(0)
