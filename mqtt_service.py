import sys
import ssl
import time
import csv
import datetime
import logging, traceback
import paho.mqtt.client as mqtt
import json
import time
from email_service import EmailService
from threading import Thread
from datetime import datetime, timedelta
from activity_classifier import ActivityClassifier

config_data = json.load(open("./config/mqtt_config.json","r"))

IOT_PROTOCOL_NAME = "x-amzn-mqtt-ca"
AWS_IOT_ENDPOINT = config_data['endpoint']
ROOT_CA = config_data['ca_certificate_location']
CERTIFICATE = config_data['pem_certificate_location']
PRIVATE_KEY = config_data['private_key_location']
PORT = config_data['port']
CLIENT_ID = config_data['client_id']
TOPIC = config_data['topic']
url = "https://{}".format(AWS_IOT_ENDPOINT)

class MqttService(Thread):
    def __init__(self,logger,db_client):
        Thread.__init__(self)
        self.__logger = logger
        self.__client = mqtt.Client()
        self.__ssl_context = ssl.create_default_context()
        self.__db_client=db_client
        self.counter = 0
        self.buffer = []
        self.classifier = ActivityClassifier()

    def __config_ssl(self):
        try:
            self.__logger.info("open ssl version:{}".format(ssl.OPENSSL_VERSION))
            self.__ssl_context.set_alpn_protocols([IOT_PROTOCOL_NAME])
            self.__ssl_context.load_verify_locations(cafile=ROOT_CA)
            self.__ssl_context.load_cert_chain(certfile=CERTIFICATE, keyfile=PRIVATE_KEY)
        except Exception as e:
            self.__logger.error("exception ssl_alpn()")
            raise e
    def __config_mqtt(self):
        self.__client.tls_set_context(context = self.__ssl_context)
        self.__logger.info("Connecting to {}".format(AWS_IOT_ENDPOINT))
        self.__client.connect(AWS_IOT_ENDPOINT,PORT)
        self.__logger.info("Successfully connected to broker")
        self.__client.on_message=self.__on_receive_callback

    def __on_receive_callback(self,client,userdata,message):

        parsed_json = json.loads(str(message.payload.decode('utf-8')))
        self.__logger.info("Message received:{0}".format(parsed_json))
        number_of_readings = len(parsed_json["oxygen_level_readings"])
        delay = parsed_json["delay_interval"]
        timestamps = self.__generate_timestamps(number_of_readings,delay//1000)
        self.__db_client.insert_records(timestamps,parsed_json["heart_rate_readings"],parsed_json["oxygen_level_readings"],parsed_json["accel_x"],parsed_json["accel_y"],parsed_json["accel_z"],parsed_json["magneto_x"],parsed_json["magneto_y"],parsed_json["magneto_z"])
        self.validate_readings(parsed_json["oxygen_level_readings"],parsed_json["heart_rate_readings"])
        self.__logger.info("Successfully inserted {} records in the database".format(number_of_readings))

        for i in range(5):
            row = []
            row = [parsed_json["heart_rate_readings"][i],parsed_json["accel_x"][i],parsed_json["accel_y"][i],parsed_json["accel_z"][i],parsed_json["magneto_x"][i],parsed_json["magneto_y"][i],parsed_json["magneto_z"][i]]
            self.buffer.append(row)
        self.counter+=1

        if self.counter == 6:
            data = []
            current_activity = self.classifier.predict(self.buffer)
            ts = time.time()
            data.append(ts)
            data.append(current_activity)

            with open('activity.csv','a') as file:
                writer = writer(file)
                writer.writerow(data)
                file.close()

            self.buffer = []
            self.counter = 0

    def validate_readings(self,oxygen_arr,heart_rate_arr):
        Email_data = json.load(open("Emails.json"))
        Em = EmailService(self.__logger)

        for oxygen in oxygen_arr:
            if oxygen<95 or oxygen>100:
                Em.send_alert_notification([Email_data["User_Emails"],Email_data["Trusted_Emails"]])
                break

        for heart_rate in heart_rate_arr:
            if heart_rate>90 or heart_rate<60:
                Em.send_alert_notification([Email_data["User_Emails"],Email_data["Trusted_Emails"]])
                break

    def __generate_timestamps(self,n,delay):
        #current_timestamp = datetime.fromtimestamp(int(time.time()))
        #result = [current_timestamp.strftime('%Y-%m-%d %H:%M:%S')]
        current_timestamp = int(time.time())
        result = [current_timestamp]
        for _ in range(n-1):
            #current_timestamp-=timedelta(milliseconds=delay)
            current_timestamp-=delay
            #result.append(current_timestamp.strftime('%Y-%m-%d %H:%M:%S'))
            result.insert(0,current_timestamp)
        return result

    def run(self):
        try:
            self.__config_ssl()
            self.__config_mqtt()
            self.__client.loop_start()
            self.__client.subscribe(TOPIC)
            while True:
                time.sleep(0.1)
        except Exception as e:
            self.__logger.error("exception main()")
            self.__logger.error("e obj:{}".format(vars(e)))
            self.__logger.error("message:{}".format(e))
            traceback.print_exc(file=sys.stdout)
