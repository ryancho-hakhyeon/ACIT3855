import mysql.connector
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

db_conn = mysql.connector.connect(host=app_config["datastore"]["hostname"],
                                  user=app_config["datastore"]["user"],
                                  password=app_config["datastore"]["password"],
                                  port=app_config["datastore"]["port"],
                                  database=app_config["datastore"]["db"])

#db_conn = mysql.connector.connect(host="localhost", user="root", password="password", database="events")

db_cursor = db_conn.cursor()
db_cursor.execute('''
            DROP TABLE crawling_image, list_category
        ''')

db_conn.commit()
db_conn.close()