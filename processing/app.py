import connexion
import swagger_ui_bundle
from apscheduler.schedulers.background import BackgroundScheduler

import os
import datetime

import requests
import json
import logging.config
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def get_stats():
    stats = {}
    if os.path.isfile(app_config["datastore"]["filename"]):
        stats_file = open(app_config["datastore"]["filename"])
        data = stats_file.read()
        stats_file.close()

        full_stats = json.loads(data)

        if "num_ci_readings" in full_stats:
            stats["num_ci_readings"] = full_stats["num_ci_readings"]
        if "num_cl_readings" in full_stats:
            stats["num_cl_readings"] = full_stats["num_cl_readings"]
        if "image_name" in full_stats:
            stats["image_name"] = full_stats["image_name"]
        if "category_name" in full_stats:
            stats["category_name"] = full_stats["category_name"]

        logger.info("Found valid stats")
        logger.debug(stats)
    else:
        return "Statistics Do Not Exist", 404

    return stats, 200


def populate_stats():
    """ """
    logger.info("Processing")
    stats = {}
    if os.path.isfile(app_config["datastore"]["filename"]):
        stats_file = open(app_config["datastore"]["filename"])
        data = stats_file.read()
        stats = json.loads(data)

        stats_file.close()

    last_updated = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    if "last_updated" in stats:
        last_updated = stats["last_updated"]

    current_updated = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    response = requests.get(app_config["eventstore"]["url"] + "/crawling-image?timestamp=" + last_updated)

    if response.status_code == 200:
        if "num_ci_readings" in stats.keys():
            stats["num_ci_readings"] += len(response.json())
        else:
            stats["num_ci_readings"] = len(response.json())

        for event in response.json():
            if "image_name" in stats.keys():
                stats["image_name"] = event["image_name"]
            elif "image_name" not in stats.keys():
                stats["image_name"] = event["image_name"]

        logger.info("Processed Crawling Image %d" % len(response.json()))

    response = requests.get(app_config["eventstore"]["url"] + "/list-category?timestamp=" + last_updated)

    if response.status_code == 200:
        if "num_cl_readings" in stats.keys():
            stats["num_cl_readings"] += len(response.json())
        else:
            stats["num_cl_readings"] = len(response.json())

        for event in response.json():
            if "category_name" in stats.keys():
                stats["category_name"] = event["category_name"]
            elif "category_name" not in stats.keys():
                stats["category_name"] = event["category_name"]

        logger.info("Processed List Category %d" % len(response.json()))

    stats["last_updated"] = current_updated

    stats_file = open(app_config["datastore"]["filename"], "w")
    stats_file.write(json.dumps(stats, indent=4))
    stats_file.close()
    logger.info("Done Processing")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    # run our standalone gevent server
    init_scheduler()
    app.run(port=8100, use_reloader=False)