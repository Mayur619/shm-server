from flask import Flask, render_template, send_from_directory,make_response,jsonify
from flask_cors import CORS,cross_origin
from threading import Thread
import json

class WebService(Thread):
    def __init__(self,logger,db_client):
        Thread.__init__(self)
        self.__logger = logger
        self.__db_client = db_client
        self.__app = Flask(__name__)
        self.__create_routes()
    def __config_cors(self):
        self.__app.config['CORS_HEADERS'] = 'Content-Type'
        cors = CORS(self.__app,resources = {r'/data/*':{'origins':'http://18.234.181.159:5000/'}})
    def __create_routes(self):
        @self.__app.route("/records",methods = ['GET'])
        def records():
            return render_template("show_records.html",
                                   records = self.__db_client.get_records())
        
        
        @self.__app.route("/chart/<name>",methods = ['GET'])
        def show_chart(name):
            if name == 'heartrate':
                template_name = "show_heart_rate.html"
            elif name == 'oxygen':
                template_name = "show_oxygen.html"
            else:
                template_name = "show_temperature.html"
            return render_template(template_name)
        
        
        @self.__app.route("/data/<path:path>")
        @cross_origin()
        def send_json(path):
            if path=="heartRate.json":
                json_data=self.__db_client.generate_heartRate_json()
            elif path=="oxygenLevel.json":
                json_data=self.__db_client.generate_oxygenLevels_json()
            elif path=="temperature.json":
                json_data=self.__db_client.generate_temperature_json()
            
            return jsonify(json_data)
        
        @self.__app.route("/",methods = ['GET'])
        def index():
            return render_template("index.html")
        self.__logger.info("Successfully registered all web routes")
        
        
        
    def run(self):
        self.__logger.info("Initializing web server")
        self.__config_cors()
        config_data = json.load(open("./config/flask_config.json"))
        self.__app.run(host = config_data['host'],port = config_data['port'])
