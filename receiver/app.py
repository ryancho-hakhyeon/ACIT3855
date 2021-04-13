import json
import connexion
from connexion import NoContent
import os
import requests
from pykafka import KafkaClient

import yaml
import logging.config
import datetime
import time

EVENTS_FILE = "events.json"
MAX_EVENT = 10

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


def log_event(event):
    events_data = []

    while len(events_data) >= MAX_EVENT:
        events_data.pop(0)
    events_data.append(event)

    with open(EVENTS_FILE, "w") as fh:
        fh.write(json.dumps(events_data, indent=4))

RE_TRY = 20
count = 1

while count < RE_TRY:
    try:
        logger.info("Trying to connect.")
        hostname = "%s: %d" % (app_config["events"]["hostname"], app_config["events"]["port"])
        client = KafkaClient(hosts=hostname)
        topic = client.topics[str.encode(app_config["events"]["topic"])]

        producer = topic.get_sync_producer()
        break
    except:
        logger.error("Lost connection. (%d)" % count)
        time.sleep(app_config["event"]["period_sec"])
        count = count + 1
        
def crawling_image(body):
    """ Receives a Crawling List """

    logger.info("INFO: crawling list response ID: %s " % body["image_id"])

    msg = {"type": "ci",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info("Returned event Crawling Image response (Id: %s)" % body["image_id"])

    #headers = {"Content-Type": "application/json"}
    #response = requests.post(app_config["eventstore1"]["url"], json=body, headers=headers)

    #logger.info("INFO: crawling list response ID: %s %d" % (body["image_id"], response.status_code))


    return NoContent, 201


def list_category(body):
    """ Receives a Category List """

    logger.info("INFO: list category response ID: %s " % body["category_id"])

    msg = {"type":"cl",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body}

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    
    #headers = {"Content-Type": "application/json"}
    #response = requests.post(app_config["eventstore2"]["url"], json=body, headers=headers)
    #logger.info("INFO: list category response ID: %s  %d" % (body["category_id"], response.status_code))

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/receiver", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080)
