import logging
from extract_script import load_watermark, save_watermark, get_firestore_client, extract_data_from_firestore
from transformation_script import main_transformation 
from load_script import  load_values_to_google_sheets 
from sales_tracker import update_prospect_tracker 

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Retrieving watermark
        logger.info("Starting Data Pipeline....")
        watermark = load_watermark()

        if not watermark:
            logger.info("No previous watermark found, this would be the initial extraction")
        else:
            logger.info("Watermark Found: registered_at = %s, document_id = %s", watermark.registered_at, 
                        watermark.document_id)

        # connecting to firestore in firebase 
        db = get_firestore_client() 
        logger.info("Successfully connected to firestore")

        # extracting documents from the course-registrants collection
        records, next_watermark = extract_data_from_firestore(db,watermark)
        logger.info("Successfully extracted %d records from course-registrants collection", len(records))

        if not records:
            logger.info("No new records found, nothing to transform or load")
            return 

        # transforming the data 
        transformed_data = main_transformation(records)

        logger.info("Successfully transformed %d records",len(transformed_data))

        # loading the data into Google sheets 
        logger.info("Loading transformed data to Google sheets....")

        load_values_to_google_sheets(transformed_data) 

        logger.info("Successfully loaded transformed data to Google sheets")

        update_prospect_tracker(transformed_data)

        logger.info("Successfully loaded transformed data to Prospect tracker")

        # Saving next watermark 

        if next_watermark is not None:
            save_watermark(next_watermark)
            logger.info("Successfully saved next watermark")

        logger.info("Pipeline run successfully completed!!!")

    except Exception as e:
        logger.error(f"Failed to complete the pipeline run: {e}")
        raise 

if __name__ == "__main__":
    main()





