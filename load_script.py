from datetime import date, datetime, time 
import logging
from pathlib import Path
from typing import Any
import gspread 


logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

GOOGLE_CREDENTIALS = Path("google_service_account.json")

SPREADSHEET_ID = "18wgWkEVxE2FGeprjsIeNg8GvkMegKx56qJpoEhhwyCs"

WORKSHEET_NAME = "Input"

UNIQUE_COLUMN = "document_id"


def get_worksheet():
    try:
        client = gspread.service_account(GOOGLE_CREDENTIALS)
        
        spread_sheet = client.open_by_key(SPREADSHEET_ID)
        
        work_sheet = spread_sheet.worksheet(WORKSHEET_NAME)
        
        return work_sheet 
    except Exception as e:
        logger.error(f"Failed to get worksheet: {e}")

def handle_values(value:Any) -> Any:
    try:
        if value is None:
                return ""
        
        if isinstance(value, (datetime, date, time)):
            return value.isoformat()

        return value 
    except Exception as e:
        logger.error(f"Failed to handle values: {e}")
        raise 

# def load_values_to_google_sheets(records:list[dict[str:Any]]):
#     if not records:
#         logger.info("No Data to load into Google sheets")
#         return 

#     logger.info("Loading data into Google sheets...")

#     worksheet = get_worksheet()

#     existing_values = worksheet.get_all_values()

#     if not existing_values:
#         headers = list(records[0].keys()) 

#         worksheet.append_row(
#             headers,
#             value_input_option = "USER_ENTERED"
#         ) 

#         logger.info("Created table headers") 

#         existing_values = [headers]

#     headers = existing_values[0]

#     # if UNIQUE_COLUMN not in headers:
#     #     raise ValueError(f"Required unique column '{UNIQUE_COLUMN}' is missing from Google sheets")
#     if UNIQUE_COLUMN not in headers:

#         logger.info(
#             "Adding missing '%s' column to Google Sheets...",
#             UNIQUE_COLUMN
#         )

#         worksheet.insert_cols(
#             [[UNIQUE_COLUMN]],
#             col=1
#         )

#         headers.insert(0, UNIQUE_COLUMN)

#     unique_column_index = headers.index(UNIQUE_COLUMN)

#     existing_document_ids = set()
        
#     for row in existing_values[1:]:
#         if len(row) > unique_column_index and row[unique_column_index]:
#             existing_document_ids.add(row[unique_column_index])

#     logger.info("Found %d existing records in Google sheets",len(existing_document_ids))

#     new_records = []

#     for record in records:
#         document_id = record.get(UNIQUE_COLUMN)

#         if not document_id:
#             logger.warning("Record has no document_id, Skipping...")
#             continue 

#         if document_id in existing_document_ids:
#             logger.info("document_id '%s' already present in Google Sheets, Skipping...",document_id)
#             continue 

#         new_records.append(record)

#         existing_document_ids.add(document_id)

#     if not new_records:
#         logger.info("No new records to load")
#         return 

#     rows = []

#     for record in new_records:
#         row = []

#         for column in headers:
#             value = record.get(column)
#             value = handle_values(value)
#             row.append(value)

#         rows.append(row) 

#     worksheet.append_rows(
#         rows,
#         value_input_option = "USER_ENTERED"
#     )

#     logger.info("Successfully loaded %d rows into Google sheets",len(new_records))


def load_values_to_google_sheets(records: list[dict[str, Any]]):
    if not records:
        logger.info("No Data to load into Google sheets")
        return

    logger.info("Loading data into Google sheets...")

    worksheet = get_worksheet()
    existing_values = worksheet.get_all_values()

    # Union of all keys across all incoming records, preserving first-seen order
    all_record_keys = []
    seen = set()
    for record in records:
        for key in record.keys():
            if key not in seen:
                seen.add(key)
                all_record_keys.append(key)

    if not existing_values:
        # Make sure UNIQUE_COLUMN is first
        headers = [UNIQUE_COLUMN] + [k for k in all_record_keys if k != UNIQUE_COLUMN]

        worksheet.append_row(headers, value_input_option="USER_ENTERED")
        logger.info("Created table headers")
        existing_values = [headers]

    headers = existing_values[0] 

    if UNIQUE_COLUMN not in headers:
        logger.info("Adding missing '%s' column to Google Sheets...", UNIQUE_COLUMN)
        worksheet.insert_cols([[UNIQUE_COLUMN]], col=1)
        headers.insert(0, UNIQUE_COLUMN) 

    # NEW: detect and add any other columns present in records but missing from the sheet
    missing_columns = [k for k in all_record_keys if k not in headers]
    if missing_columns:
        logger.info("Adding missing columns to Google Sheets: %s", missing_columns)
        start_col = len(headers) + 1
        worksheet.update(
            [missing_columns],
            range_name=gspread.utils.rowcol_to_a1(1, start_col),
            value_input_option="USER_ENTERED",
        )
        headers.extend(missing_columns)

    unique_column_index = headers.index(UNIQUE_COLUMN)

    existing_document_ids = set() 
    for row in existing_values[1:]:
        if len(row) > unique_column_index and row[unique_column_index]:
            existing_document_ids.add(row[unique_column_index])

    logger.info("Found %d existing records in Google sheets", len(existing_document_ids))

    new_records = []
    for record in records:
        document_id = record.get(UNIQUE_COLUMN)
        if not document_id:
            logger.warning("Record has no document_id, Skipping...")
            continue   
        if document_id in existing_document_ids:
            logger.info("document_id '%s' already present in Google Sheets, Skipping...", document_id)
            continue
        new_records.append(record)
        existing_document_ids.add(document_id)

    if not new_records:
        logger.info("No new records to load")
        return 

    rows = []
    for record in new_records:
        row = [handle_values(record.get(column)) for column in headers]
        rows.append(row)

    worksheet.append_rows(rows, value_input_option="USER_ENTERED")
    logger.info("Successfully loaded %d rows into Google sheets", len(new_records))




