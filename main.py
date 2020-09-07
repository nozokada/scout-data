import logging

from constants import LOG_FILENAME
from data_service import DataService

logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
data_service = DataService()
data_service.execute_scout_data_generation_cycle(page_number=5996)
# data_service.download_scout_data(collection_id=TP_PHOTOS_REF_NAME)
# data_service.upload_scout_data(collection_id=TP_PHOTOS_REF_NAME)
