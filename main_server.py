import sys
import logging

from database_service import DatabaseService
from mqtt_service import MqttService
from flask_server import WebService

def config_default_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    log_format = logging.Formatter('%(asctime)s * %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(log_format)
    logger.addHandler(handler)
    return logger

if __name__ == '__main__':
    logger = config_default_logger()
    db_client = DatabaseService(logger)
    
    mqtt = MqttService(logger,db_client)
    web_server = WebService(logger,db_client)
    
    mqtt.start()
    web_server.start()