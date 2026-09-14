from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any
import firebase_admin  
from firebase_admin import credentials, firestore 
from google.cloud.firestore_v1.field_path import FieldPath
from dateutil import parser as date_parser 

# for log messages 
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# collection = the table the pipeline extracts data from
# credentials = for authentication, so the pipeline can extract data from firebase 
# watermark_file = The pipelines memory where the last row of data extracted is saved 

COLLECTION = "course-registrants"
CREDENTIALS = Path("firebase_service_account.json")
WATERMARK_FILE = Path("watermark.json") 

# custom data schema for the watermark that tells it what to save 
@dataclass
class Watermark:
    registered_at: datetime
    document_id: str 

# python function to retrieve current watermark from the watermark file 
def load_watermark() -> Watermark| None:
    try:
        if not WATERMARK_FILE.exists():
                logger.info("Watermark file is empty")
                return None 
        
        with WATERMARK_FILE.open("r", encoding="utf-8") as f:
                state = json.load(f) 
        
        return Watermark(
                registered_at = datetime.fromisoformat(state["registered_at"]),
                document_id = state["document_id"]
            )

    except Exception as e:
         logger.error(f"An error occurred while loading watermark: {e}")
         raise 

# Python function for saving water marks 
def save_watermark(watermark:Watermark) -> None:
    try:
         WATERMARK_FILE.parent.mkdir(parents=True,exist_ok=True) 
         
         TEMP_FILE = WATERMARK_FILE.with_suffix(".tmp")
         
         with TEMP_FILE.open("w", encoding="utf-8") as f:
                 json.dump(
                     {
                         "registered_at":watermark.registered_at.isoformat(),
                         "document_id":watermark.document_id
                     },
                     f
                 )
         
         TEMP_FILE.replace(WATERMARK_FILE) 

    except Exception as e:
         logger.error(f"An error occurred while saving watermark: {e}")
         raise 

# Python function for creating the firestore client 
def get_firestore_client():
     try:
           if not CREDENTIALS.exists():
                       logger.info(f"Missing credentials: {CREDENTIALS}") 
           
           if not firebase_admin._apps:
                       cred = credentials.Certificate(str(CREDENTIALS))
                       firebase_admin.initialize_app(cred) 
           
           return firestore.client()
     except Exception as e:
           logger.error(f"Failed to return firestore client: {e}")

# Python function for extracting data from firestore 
def extract_data_from_firestore(db,watermark: Watermark| None) -> tuple[list[dict[str:Any]], Watermark|None]:
      try:
            logger.info("Starting data extraction from firestore...")
            query = (
                  db.collection("course-registrants")
                    .order_by("registeredAt")
                    .order_by(FieldPath.document_id())
            )        

            if watermark is not None:
                  query = query.where(
                        "registeredAt",
                        ">=",
                        watermark.registeredAt
                  )

            records = []
            next_watermark = watermark

            for doc in query.stream():
                  data = doc.to_dict()
                  registered_at = data.get("registeredAt")

                  # if not isinstance(registered_at, datetime):
                  #       logger.warning("document %s: Invalid datetime format",doc.id)
                  #       continue 

                  if not isinstance(registered_at, datetime):
                         try:
                                registered_at = date_parser.parse(registered_at)
                         except (ValueError, TypeError):
                               logger.warning("document %s: Could not parse registered_at '%s', defaulting to None", doc.id, registered_at)
                               registered_at = None 

                  if registered_at.tzinfo is None:
                        registered_at = registered_at.replace(tzinfo=timezone.utc)

                  position = (registered_at, doc.id)

                  if watermark is not None and position <= (
                        watermark.registered_at,
                        watermark.document_id):
                        continue 

                  data["document_id"] = doc.id
                  records.append(data) 

                  next_watermark = Watermark(
                        registered_at = registered_at,
                        document_id= doc.id 
                  ) 

            logger.info(f"Finished extracting data from firestore: Data contains {len(records)} rows")

            return records, next_watermark 
      except Exception as e:
            logger.error(f"Failed to extract data from firestore: {e}")
            raise 

# def test():
#       watermark = load_watermark()
      
#       if not watermark:
#             logger.info("No previous watermark found, this would be the initial extraction")
#       else:
#             logger.info("Watermark Found: registered_at = %s, document_id = %s", watermark.registered_at, 
#                               watermark.document_id)
      
#               # connecting to firestore in firebase 
#       db = get_firestore_client() 
#       logger.info("Successfully connected to firestore")
      
#               # extracting documents from the course-registrants collection
#       records, next_watermark = extract_data_from_firestore()
#       logger.info("Successfully extracted %d records from course-registrants collection", len(records))
      
#       if not records:
#             logger.info("No new records found, nothing to transform or load")
#             return 

# if __name__ == "__main__":
#       test()
                  
