import mysql.connector as mysqlCon
from mysql.connector.pooling import  MySQLConnectionPool
import logging
import pandas as pd
import os
import json

class DatabaseService:

    def __init__(self,logger):
        self.__logger=logger
        self.__logger.info("Connecting")
        self.config_data = json.load(open("./config/db_config.json","r"))
        #self.init_connection()

        #con = self.__database_connection.cursor()
        self.__connection_pool = MySQLConnectionPool(pool_size=10,pool_name="Database pool",
                                                     host = self.config_data["host"],
                                                     database = self.config_data["dbname"],
                                                     user = self.config_data["username"],
                                                     password = self.config_data["password"])
        #con.execute('SET GLOBAL connect_timeout=28800')
        #con.execute('SET GLOBAL interactive_timeout=28800')
        #con.execute('SET GLOBAL wait_timeout=28800')
        self.__logger.info("Connected")
        self.create_table()

    def init_connection(self):
        self.__database_connection = mysqlCon.connect(
        host=self.config_data['host'],
        user=self.config_data['username'],
        password=self.config_data['password'], 
        db= self.config_data['dbname'])
    def create_table(self):
        #if not self.__database_connection.is_connected():
        #    self.init_connection()
        connection = self.__connection_pool.get_connection()
        if connection.is_connected():
            query_cursor=connection.cursor()
            query_cursor.execute("create table if not exists `Readings`(R_ID int primary key auto_increment,timestamp mediumtext,heart_rate int, oxygen int, temperature float);")
            query_cursor.close()
            connection.close()

    def get_db_connection(self):
        return self.__database_connection
    def insert_records(self,timestamp_arr,heart_arr,oxygen_arr,temp_arr):
        #if not self.__database_connection.is_connected():
        #    self.init_connection()
        connection = self.__connection_pool.get_connection()
        if connection.is_connected():
            for i in range(len(timestamp_arr)):
                query_cursor = connection.cursor()
                insert_query = "INSERT INTO Readings (timestamp,heart_rate,oxygen,temperature) values(%s,%s,%s,%s)"
                insert_query_values = (timestamp_arr[i],heart_arr[i],oxygen_arr[i],temp_arr[i])
                query_cursor.execute(insert_query,insert_query_values)
                self.__database_connection.commit()
                query_cursor.close()
            connection.close()

    def get_records(self):
        #if not self.__database_connection.is_connected():
        #    self.init_connection()
        connection = self.__connection_pool.get_connection()
        if connection.is_connected():
            select_cursor = connection.cursor()
            select_cursor.execute("SELECT * FROM Readings")
            select_query_result = select_cursor.fetchall()
            self.__logger.info("Successfully fetched {} records".format(len(select_query_result)))
            select_cursor.close()
            connection.close()
            return select_query_result
    
    def generate_heartRate_json(self):
        #if not self.__database_connection.is_connected():
        #    self.init_connection()
        connection = self.__connection_pool.get_connection()
        if connection.is_connected():
            select_cursor = connection.cursor()
            select_cursor.execute("SELECT timestamp,heart_rate FROM Readings")
            select_query_result = select_cursor.fetchall()
            heart_rate_data = [[int(timestamp)*1000,heart_rate] for timestamp,heart_rate in select_query_result]
            select_cursor.close()
            connection.close()
            return heart_rate_data
    
    def generate_oxygenLevels_json(self):
        #if not self.__database_connection.is_connected():
        #    self.init_connection()
        connection = self.__connection_pool.get_connection()
        if connection.is_connected():
            select_cursor = connection.cursor()
            select_cursor.execute("SELECT timestamp,oxygen FROM Readings")
            select_query_result = select_cursor.fetchall()
            oxygen_level_data = [[int(timestamp)*1000,oxygen_level] for timestamp,oxygen_level in select_query_result]
            select_cursor.close()
            connection.close()
            return oxygen_level_data
    
    def generate_temperature_json(self):
        #if not self.__database_connection.is_connected():
        #    self.init_connection()

        connection = self.__connection_pool.get_connection()
        if connection.is_connected():
            select_cursor = connection.cursor()
            select_cursor.execute("SELECT timestamp,temperature FROM Readings")
            select_query_result = select_cursor.fetchall()
            temperature_data = [[int(timestamp)*1000,temperature] for timestamp,temperature in select_query_result]
            select_cursor.close()
            connection.close()
            return temperature_data
    
    def generate_heartRate_csv(self):
        connection = self.__connection_pool.get_connection()
        df = pd.read_sql("select timestamp,heart_rate from Readings order by timestamp",connection)
        connection.close()
        return df
    
    def generate_oxygen_csv(self):
        connection = self.__connection_pool.get_connection()
        df = pd.read_sql("select timestamp,oxygen from Readings",connection)
        connection.close()
        return df
    
    def generate_temperature_csv(self):
        connection = self.__connection_pool.get_connection()
        df = pd.read_sql("select timestamp,temperature from Readings",connection)
        connection.close()
        return df


#S = SHM_database(logging.getLogger())
#print(S.get_records())
#S.insert_records(["2020/02/10 23:59:59","2019/02/11 13:53:59"],[14,20],[60,55],[2,66])
#print(S.get_records())
