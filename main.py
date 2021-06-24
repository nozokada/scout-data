import logging

from constants import LOG_FILENAME
from data_service import DataService

logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
data_service = DataService()
# data_service.execute_scout_data_generation_cycle(page_number=6014)
data_service.copy_geo_hash()
