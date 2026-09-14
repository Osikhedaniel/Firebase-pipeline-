from datetime import date, datetime, time
import logging
from pathlib import Path
from typing import Any
import gspread


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)



# Configuration

GOOGLE_CREDENTIALS = Path("google_service_account.json")

SPREADSHEET_ID = "18wgWkEVxE2FGeprjsIeNg8GvkMegKx56qJpoEhhwyCs"

WORKSHEET_NAME = "Prospect Tracker"

UNIQUE_COLUMN = "Doc ID (ETL Ref)"



# Column Mapping

COLUMN_MAPPING = {
    "Lead Name": "name",
    "Email": "email",
    "Phone Number": "mobile",
    "Country": "country",
    "Course Interested In": "course",
    "Referral ID": "referral_id",
    "Registration_date": "registration_date",
    "Registration_time": "registration_time",
    "Doc ID (ETL Ref)": "document_id"
} 


# Google Sheets connection

def get_prospect_tracker():
    """
    Connect to the Prospect Tracker worksheet.
    """

    try:
        client = gspread.service_account(
            filename=GOOGLE_CREDENTIALS
        )

        spreadsheet = client.open_by_key(
            SPREADSHEET_ID
        )

        worksheet = spreadsheet.worksheet(
            WORKSHEET_NAME
        )

        return worksheet

    except Exception as e:
        logger.error(
            "Failed to connect to Prospect Tracker: %s",
            e
        )
        raise


# Value preparation

def handle_tracker_value(value: Any) -> Any:
    """
    Convert Python values into Google Sheets-compatible values.
    """

    if value is None:
        return ""

    if isinstance(value, (datetime, date, time)):
        return value.isoformat()

    return value


# Update Prospect Tracker

def update_prospect_tracker(
    records: list[dict[str, Any]]
) -> None:
    """
    Add new Firestore prospects to the Prospect Tracker.

    Existing prospects are identified using document_id.

    Existing sales-team information is never overwritten.
    """

    if not records:
        logger.info(
            "No records to update in Prospect Tracker."
        )
        return

    logger.info(
        "Updating Prospect Tracker..."
    )

    worksheet = get_prospect_tracker()

    # Get existing data

    existing_values = worksheet.get_all_values()

    if not existing_values:
        raise ValueError(
            "Prospect Tracker is empty. "
            "Please add the tracker headers first."
        )

    headers = existing_values[0]

    logger.info("Prospect Tracker headers: %s", headers)

    # Check that the unique column exists

    if UNIQUE_COLUMN not in headers:
        raise ValueError(
            f"Required unique column '{UNIQUE_COLUMN}' "
            f"is missing from Prospect Tracker."
        )

    unique_column_index = headers.index(
        UNIQUE_COLUMN
    )

    # Collect existing document IDs

    existing_document_ids = set()

    for row in existing_values[1:]:

        if (
            len(row) > unique_column_index
            and row[unique_column_index]
        ):
            existing_document_ids.add(
                row[unique_column_index]
            )

    logger.info(
        "Found %d existing prospects in Prospect Tracker.",
        len(existing_document_ids)
    )

    # Find new records

    new_records = []

    for record in records:

        document_id = record.get(
            "document_id"
        )

        if not document_id:

            logger.warning(
                "Record has no document_id. Skipping..."
            )

            continue

        if document_id in existing_document_ids:

            logger.info(
                "document_id '%s' already exists "
                "in Prospect Tracker. Skipping...",
                document_id
            )

            continue

        new_records.append(record)

        # Prevent duplicate document_ids within
        # the same extraction batch.
        existing_document_ids.add(
            document_id
        )

    # Nothing new

    if not new_records:

        logger.info(
            "No new prospects to add to Prospect Tracker."
        )

        return

    # Build rows according to tracker column order

    rows = []

    for record in new_records:

        row = []

        for column in headers:

            # Find the corresponding Firestore/
            # transformed-data column.
            source_column = COLUMN_MAPPING.get(
                column
            )

            if source_column is not None:

                value = record.get(
                    source_column
                )

            else:

                # Columns such as:
                # Assigned Rep
                # Status
                # Priority
                # Next Follow-Up
                # Last Contact
                # Feedback / Notes
                #
                # are sales-team columns and do not
                # come from Firestore.
                value = ""

            value = handle_tracker_value(
                value
            )

            row.append(value)

        rows.append(row)

    # Append new prospects

    worksheet.append_rows(
        rows,
        value_input_option="USER_ENTERED"
    )

    logger.info(
        "Successfully added %d new prospects "
        "to Prospect Tracker.",
        len(new_records)
    )