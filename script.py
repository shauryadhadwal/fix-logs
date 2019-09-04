import os
from pprint import pprint
import logging
from pprint import pprint
import json
import datetime
import time

# Logger Settings
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
TEXT_DIR = "textfiles"
JSON_DIR = "jsonfiles"
REQUESTS_DUMP_DIR = "requests"
REQUESTS_LIMIT_SIZE = 500

LAST_TEXT_FILE = ""
LAST_JSON_FILE = ""
LAST_INDEX_IN_LOG = 0


def getTextFiles():
    files = os.listdir("textfiles")
    return sorted(files)


def getJsonFiles():
    files = os.listdir("jsonfiles")
    return sorted(files)


def writeRequestsToJsonFile(filename, data):
    path = f"{REQUESTS_DUMP_DIR}/{filename}_requests.json"
    try:
        with open(path, "w", encoding='utf-8') as data_file:
            json.dump(data, data_file, ensure_ascii=False, indent=4)
    except Exception as exp:
        logger.error(exp)


def getCodesFromTextFile(file):
    codes = []
    path = TEXT_DIR + "/" + file
    try:
        with open(path, 'r') as read_text_file:
            rows = read_text_file.readlines()
            for row in rows:
                codes.append(row.strip())

    except Exception as exp:
        logger.error(exp)

    return codes


def groupFilesByName(name, list):
    files = []
    for element in list:
        if element.find(name) > -1:
            files.append(element)

    return files


def getLastUsedObjectFromFiles(filesList):
    codes = []
    for filename in filesList:
        path = JSON_DIR + "/" + filename
        LAST_JSON_FILE = filename
        with open(path, "r") as data_file:
            try:
                jsonData = json.load(data_file)
                lastUsedObject = jsonData[-1]
                codes.append(lastUsedObject)
            except Exception as exp:
                logger.error(exp)

    return codes


def parseManufacturingDate(inputDate):
    dateString = inputDate.split("=")[1]
    year = dateString.split(".")[1]
    day = dateString[:2]
    month = dateString[2:5].title()
    dateString = f"{day}-{month}-20{year}"
    retval = createTimeStampFromString(dateString.strip(), "%d-%b-%Y")
    return retval


def createExpiryDate(inputDate):
    date = datetime.datetime.fromtimestamp(inputDate//1000)
    expiryDate = date + datetime.timedelta(days=90)
    return createTimeStampFromDate(expiryDate)


def createTimeStampFromDate(inputDate):
    return time.mktime(inputDate.timetuple()) * 1000


def createTimeStampFromString(inputDate, format="%d-%m-%Y %H:%M:%S"):
    date = datetime.datetime.strptime(inputDate, format).date().timetuple()
    return time.mktime(date) * 1000


def createRequestBody(obj, productCode):
    mfd = parseManufacturingDate(obj["manufacturingDate"])
    exp = createExpiryDate(mfd)
    plantActivatedAt = createTimeStampFromString(obj["datetime"])

    body = {
        'batchId': obj["batchNo"],
        'plantActivatedAt': plantActivatedAt,
        'productCode': productCode,
        'mfd': mfd,
        'mrp': obj["mrp"],
        'expiry': exp,
    }

    return body


def createRequestForRange(start, end, list, objectToReplicate):
    requests = []
    logger.info(f"REQUESTS RANGE: {start} -> {end}")
    for index, code in enumerate(list):
        if index >= end:
            break
        if index < start:
            continue
        request = createRequestBody(objectToReplicate, code)
        requests.append(request)

    logger.info(f"REQUEST BODY: {requests[-1]}")

    return requests


def createUpdateRequests(codes, objetcsToReplicate):
    updateRequests = []
    LAST_INDEX_IN_LOG = 0
    for lastUsedObject in objetcsToReplicate:
        indexTillNow = codes.index(lastUsedObject['lastPrinteDUID'])
        requests = createRequestForRange(
            LAST_INDEX_IN_LOG, indexTillNow, codes, lastUsedObject)
        updateRequests = updateRequests + requests
        LAST_INDEX_IN_LOG = indexTillNow

    return updateRequests


def main():
    try:
        jsonFiles = getJsonFiles()
        uniqueFileNames = set()

        for filename in jsonFiles:
            name = filename.split("_log_")
            uniqueFileNames.add(name[0])

        logger.info(f"UNIQUE FILES = {len(uniqueFileNames)}")

        # Iterate over each unique file
        for filename in uniqueFileNames:
            logger.info("---------------------------------------------")
            logger.info(f"PROCESSING FILE: {filename}")
            LAST_TEXT_FILE = filename
            jsonFilesBatch = groupFilesByName(filename, jsonFiles)
            logger.info(f"RELATED JSON FILES = {jsonFilesBatch}")
            codesFromTextFile = getCodesFromTextFile(filename+".txt")
            logger.info(f"CODES FROM TEXT FILE = {len(codesFromTextFile)}")
            objetcsToReplicate = getLastUsedObjectFromFiles(jsonFilesBatch)
            requests = createUpdateRequests(
                codesFromTextFile, objetcsToReplicate)
            writeRequestsToJsonFile(filename, requests)

            logger.info(f"TOTAL CODES: {str(len(codesFromTextFile))}")
            logger.info(f"TOTAL REQUESTS: {str(len(requests))}")

    except Exception as exp:
        logger.info(f"LAST_TEXT_FILE : {LAST_TEXT_FILE}")
        logger.info(f"LAST_TEXT_FILE : {LAST_JSON_FILE}")
        logger.info(f"LAST_INDEX_IN_LOG : {LAST_INDEX_IN_LOG}")


if __name__ == "__main__":
    logger.info("--------------------------------")
    logger.info("Script Started")
    logger.info("--------------------------------")

    main()

    logger.info("--------------------------------")
    logger.info("Script Ended")
    logger.info("--------------------------------")
