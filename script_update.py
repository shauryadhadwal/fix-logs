import os
from pprint import pprint
import logging
from pprint import pprint
import json
import datetime
import time
import requests

# Logger Settings
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
REQUESTS_DUMP_DIR = "requests"
REQUESTS_LIMIT_SIZE = 500

LAST_TEXT_FILE = ""
LAST_JSON_FILE = ""
LAST_INDEX = 0

STAGING_BASE_URL = "https://devserver.supplytics.com"
PRODUCTION_BASE_URL = "https://app.original4sure.com"


def getJsonFiles():
    files = os.listdir(REQUESTS_DUMP_DIR)
    return files


def getRequestsFromFile(filename):
    updateRequests = []
    path = REQUESTS_DUMP_DIR + "/" + filename
    LAST_JSON_FILE = filename
    with open(path, "r") as data_file:
        try:
            updateRequests = json.load(data_file)
        except Exception as exp:
            logger.error(exp)

    return updateRequests


def makeRequests(updateRequests):
    auth_token = ""
    header_info = {'content-type': 'application/json', 'authToken': auth_token}
    url = PRODUCTION_BASE_URL + "/supplytics/products/dispatch"
    body = {
        'records': updateRequests,
        'timestamp': updateRequests[-1]['plantActivatedAt']
    }
    try:
        response = requests.post(url, body, headers=header_info)
        logger.info(response.status_code)
        logger.info(response.json())
    except Exception as e:
        logger.error(e)
    pass


def makeBatchedRequests(updateRequests):
    length = len(updateRequests)
    batches = length//REQUESTS_LIMIT_SIZE
    start = 0
    end = 0

    if batches == 0 and length > 0:
        makeRequests(updateRequests)
        LAST_INDEX = length
        return

    for batchNumber in range(0, batches):
        start = batchNumber * REQUESTS_LIMIT_SIZE
        end = start + REQUESTS_LIMIT_SIZE
        logger.info(f"PROCESSING RANGE: {start} -> {end}")
        LAST_INDEX = end
        makeRequests(updateRequests[start: end])

    if length - end > 0:
        logger.info(f"PROCESSING RANGE: {end} -> {length}")
        LAST_INDEX = length
        makeRequests(updateRequests[end:])


def main():
    try:
        jsonFiles = getJsonFiles()
        logger.info(f"FILES = {len(jsonFiles)}")

        # Iterate over each file
        for filename in jsonFiles:
            logger.info("---------------------------------------------")
            logger.info(f"PROCESSING FILE: {filename}")
            logger.info("---------------------------------------------")
            updateRequests = getRequestsFromFile(filename)
            logger.info(f"REQUESTS = {len(updateRequests)}")
            makeBatchedRequests(updateRequests)
            LAST_JSON_FILE = filename

    except Exception as exp:
        logger.info(f"LAST_JSON_FILE : {LAST_JSON_FILE}")
        logger.info(f"LAST_INDEX : {LAST_INDEX}")


if __name__ == "__main__":
    logger.info("--------------------------------")
    logger.info("Script Started")
    logger.info("--------------------------------")

    main()

    logger.info("--------------------------------")
    logger.info("Script Ended")
    logger.info("--------------------------------")
