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
                CREATE TABLE crawling_image(
                    id INT NOT NULL AUTO_INCREMENT, 
                    image_id VARCHAR(100) NOT NULL, 
                    image_name VARCHAR(100) NOT NULL,
                    date_created VARCHAR(100) NOT NULL,
                    dir_path VARCHAR(250) NOT NULL,
                    dir_size VARCHAR(100),
                    CONSTRAINT crawling_image_pk PRIMARY KEY (id))
                ''')

db_cursor.execute('''
                CREATE TABLE list_category(
                    id INT NOT NULL AUTO_INCREMENT,
                    category_id VARCHAR(100) NOT NULL,
                    category_name VARCHAR(100) NOT NULL,
                    images_num INTEGER NOT NULL,
                    date_created VARCHAR(100) NOT NULL,
                    CONSTRAINT list_category_pk PRIMARY KEY (id))
                ''')
db_conn.commit()
db_conn.close()
