import os
from pprint import pprint
import logging
from pprint import pprint
import json

# Logger Settings
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
TEXT_DIR = "textfiles"
JSON_DIR = "jsonfiles"
LIMIT_SIZE = 500


def getTextFiles():
    files = os.listdir("textfiles")
    return sorted(files)


def getJsonFiles():
    files = os.listdir("jsonfiles")
    return sorted(files)


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
        with open(path, "r") as data_file:
            try:
                jsonData = json.load(data_file)
                lastUsedObject = jsonData[-1]
                codes.append(lastUsedObject)
            except Exception as exp:
                logger.error(exp)

    return codes


def createExpiryDate(date):
    return date


def createRequestBody(obj, productCode):
    body = {
        'batchId': obj["batchNo"],
        'plantActivatedAt': obj["datetime"],
        'productCode': productCode,
        'mfd': obj["manufacturingDate"],
        'mrp': obj["mrp"],
        'expiry': createExpiryDate(obj["manufacturingDate"]),
    }

    return body


def createRequestForRange(start, end, list, objectToReplicate):
    requests = []
    for index, code in enumerate(list):
        if index >= end:
            break
        if index < start:
            continue
        request = createRequestBody(objectToReplicate, code)
        requests.append(request)

    return requests


def createUpdateRequests(codes, lastUsedObjects):
    updateRequests = []
    lastUsedIndex = 0
    for lastUsedObject in lastUsedObjects:
        indexTillNow = codes.index(lastUsedObject['lastPrinteDUID'])
        requests = createRequestForRange(
            lastUsedIndex, indexTillNow, codes, lastUsedObject)
        updateRequests = updateRequests + requests
        lastUsedIndex = indexTillNow

    return updateRequests


def main():
    jsonFiles = getJsonFiles()
    uniqueFileNames = set()

    for filename in jsonFiles:
        name = filename.split("_log_")
        uniqueFileNames.add(name[0])

    print("Unique Files:")
    pprint(uniqueFileNames)

    # Iterate over each unique file
    for filename in uniqueFileNames:
        jsonFilesBatch = groupFilesByName(filename, jsonFiles)
        print("Json Files to Process:")
        pprint(jsonFilesBatch)
        codes = getCodesFromTextFile(filename+".txt")
        lastUsedObjects = getLastUsedObjectFromFiles(jsonFilesBatch)
        requests = createUpdateRequests(codes, lastUsedObjects)

        print("Total Codes:")
        pprint(len(codes))
        print("Total Udpate Requests:")
        pprint(len(requests))

    # getCodesFromTextFile("futmtu2nzqwmjixmze0ng_m1_fm2112t_20000.txt")


if __name__ == "__main__":
    main()
