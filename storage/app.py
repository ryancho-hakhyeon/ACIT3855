import connexion
from connexion import NoContent
from threading import Thread
from pykafka import KafkaClient
from pykafka.common import OffsetType

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import and_
from base import Base
from crawling_image import CrawlingImage
from list_category import ListCategory

import logging.config
import yaml
import datetime
import json
import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)







DB_ENGINE = create_engine('mysql+pymysql://%s:%s@%s:%d/%s' % (app_config["datastore"]["user"],
                                                              app_config["datastore"]["password"],
                                                              app_config["datastore"]["hostname"],
                                                              app_config["datastore"]["port"],
                                                              app_config["datastore"]["db"]))

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info("connecting to DB. Hostname: %s, Port: %d" % (app_config["datastore"]["hostname"],
                                                          app_config["datastore"]["port"]))


def crawling_image(body):

    session = DB_SESSION()

    ci = CrawlingImage(body['image_id'],
                       body['image_name'],
                       body['features']['dir_path'],
                       body['features']['dir_size'])

    #logger.debug("DEBUG: " + str(body))

    session.add(ci)

    session.commit()
    session.close()
    logger.debug("Stored event Crawling Image request with a unique id of %s" % (body["image_id"]))

    #logger.info("INFO: Successful crawling image response ID: %s " % body["image_id"])
    #return NoContent, 201


def list_category(body):

    session = DB_SESSION()

    cl = ListCategory(body['category_id'],
                      body['category_name'],
                      body['images_num'])

    #logger.debug("DEBUG: " + str(body))

    session.add(cl)

    session.commit()
    session.close()
    logger.debug("Stored event List Category request with a unique id of %s" % (body["category_id"]))

    #logger.info("INFO: Successful list category response ID: %s " % body["category_id"])
    #return NoContent, 201



def get_crawling_image(start_timestamp, end_timestamp):
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")

    results = session.query(CrawlingImage).filter(
        and_(CrawlingImage.date_created >= start_timestamp_datetime,
             CrawlingImage.date_created < end_timestamp_datetime))

    result_list = []
    for result in results:
        result_list.append(result.to_dict())

    session.close()

    logger.info("Query for Crawling Image readings after %s returns %d results" % (start_timestamp_datetime, len(result_list)))

    return result_list, 200


def get_list_category(start_timestamp, end_timestamp):
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")

    results = session.query(ListCategory).filter(
        and_(ListCategory.date_created >= start_timestamp_datetime,
             ListCategory.date_created < end_timestamp_datetime))

    result_list = []
    for result in results:
        result_list.append(result.to_dict())

    session.close()

    logger.info("Query for List Category readings after %s returns %d results" % (start_timestamp_datetime, len(result_list)))

    return result_list, 200


def process_messages():
    hostname = "%s: %d" % (app_config["events"]["hostname"],
                           app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]

        if msg["type"] == "ci":
            crawling_image(payload)
        elif msg["type"] == "cl":
            list_category(payload)
        consumer.commit_offsets()
        

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()

    app.run(port=8090)
