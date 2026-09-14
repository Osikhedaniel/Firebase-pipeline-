Firebase to Google Sheets Data Pipeline

This is an automated incremental data pipeline that extracts newly registered records from Firebase Firestore and loads them into Google Sheets.

The pipeline is designed for scenarios where application data is continuously written to Firebase and business decision makers need an up-to-date spreadsheet for reporting, monitoring, and operational purposes.

Instead of exporting the entire Firestore collection every time, the pipeline uses a watermark-based incremental loading strategy to identify and process only records that have not previously been exported.

🎯 Problem Statement

Zion tech hub a tech training school collects student registration data through an online form.

Every registration is stored in a Firestore collection:

course-registrants

As new students register, the business needs their information to appear automatically in a Google Sheet used for reporting, sales and operations.

A simple approach would be:

Read every document from Firebase → export everything to Google Sheets.

However, this becomes inefficient as the collection grows and can lead to duplicate records.

This project solves that problem by implementing incremental extraction.

The pipeline remembers the position of the last successfully processed record and uses it as a starting point for the next run.

🔄 How Incremental Loading Works

The pipeline uses two values to track its progress:

registered_at
document_id

The timestamp determines the chronological position of a record, while the Firestore document ID acts as a tie-breaker when multiple records have the same timestamp.

For example:

registered_at          document_id
2026-09-14 10:30:00    ABC123
2026-09-14 10:30:00    DEF456
2026-09-14 10:35:00    XYZ789

After processing the first two records, the pipeline stores:

{
  "registered_at": "2026-09-14T10:30:00",
  "document_id": "DEF456"
}

During the next execution, the pipeline uses this watermark to identify records that come after the last processed position.

This is more reliable than simply checking the timestamp because multiple documents can potentially share the same timestamp.

🛠️ Technologies Used

1. Python	Pipeline development
2. Firebase / Firestore	Source database
3. Google Sheets API	Destination
4. Google Service Account	Authentication
5. Firebase Admin SDK	Firestore access
6. Google API Client	Google Sheets interaction
7. JSON	Pipeline state management
8. Git / GitHub	Version control

📊 Data Flow

The pipeline follows a simple ETL process:

Extract

Retrieve new registration records from Firestore.

Transform

Convert Firestore documents into a format suitable for Google Sheets.

Typical transformations may include:

Timestamp formatting
Field selection
Data type conversion
Column ordering
Null handling
Load

Append the transformed records to Google Sheets.

State Update

After successful processing, update the watermark so the next run starts from the correct position.

👨‍💻 Author
Momodu Osikhe Daniel
Data Engineer
