from datetime import datetime
import logging
from typing import Any

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


def removing_duplicates(records:list[dict[str:Any]]) -> list[dict[str:Any]]:
    try:
        seen = set()
        unique_values = []

        for record in records:
            document_id = record.get("document_id")

            if document_id in seen:
                continue 

            seen.add(document_id)
            unique_values.append(record)

        return unique_values

    except Exception as e:
        logger.error(f"Failed to remove duplicates: {e}") 

def remove_whitespaces(records:list[dict[str:Any]]) -> list[dict[str:Any]]:
    try:
        cleaned_records = []

        for record in records:
            cleaned_record = {}

            for key,value in record.items():
                if isinstance(value, str):
                    cleaned_record[key] = value.strip()

                else:
                    cleaned_record[key] = value 
            cleaned_records.append(cleaned_record)

        return cleaned_records
    except Exception as e:
        logger.error(f"Failed to remove whitespaces: {e}") 

def rename_columns(records:list[dict[str:Any]]) -> list[dict[str:Any]]:
    try:
         renamed_columns = []
        
         for record in records:
            records_copy = record.copy()
        
            if "referralId" in records_copy:
                records_copy["referral_id"] = records_copy.pop("referralId")
        
            if "registeredAt" in records_copy:
                records_copy["registered_at"] = records_copy.pop("registeredAt")
        
            renamed_columns.append(records_copy)
        
         return renamed_columns 
    except Exception as e:
        logger.error(f"Failed to rename columns: {e}")

def seperate_registeredAt_columns(records:list[dict[str,Any]]) -> list[dict[str,Any]]:
    try:
        logger.info("Seperating registeredAt columns...")
        
        cleaned_data = []
        
        for record in records:
            record_copy = record.copy()
        
            registered_at = record_copy.pop("registered_at", None)
        
            if isinstance(registered_at, datetime):
                record_copy["registration_date"] = registered_at.date()
                record_copy["registration_time"] = registered_at.time()
            else:
                record_copy["registration_date"] = None 
                record_copy["registration_time"] = None 
        
            cleaned_data.append(record_copy)
        
        return cleaned_data 
    except Exception as e:
        logger.error(f"Failed to seperate columns: {e}")  

def main_transformation(records:list[dict[str,Any]]) -> list[dict[str,Any]]:
    try:
         records = removing_duplicates(records)
        
         records = remove_whitespaces(records)
        
         records = rename_columns(records)
        
         records = seperate_registeredAt_columns(records)
        
         return records
    except Exception as e:
        logger.error(f"an error occurred during Data Transformation: {e}") 
        
            
