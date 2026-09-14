import gspread

GOOGLE_CREDENTIALS = "google_service_account.json"

SPREADSHEET_ID = "18wgWkEVxE2FGeprjsIeNg8GvkMegKx56qJpoEhhwyCs"

WORKSHEET_NAME = "Sheet1"


client = gspread.service_account(
    filename=GOOGLE_CREDENTIALS
)

spreadsheet = client.open_by_key(
    SPREADSHEET_ID
)

worksheet = spreadsheet.worksheet(
    WORKSHEET_NAME
)

print("Successfully connected to Google Sheets!")
print(f"Spreadsheet: {spreadsheet.title}")
print(f"Worksheet: {worksheet.title}")