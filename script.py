import os
from pprint import pprint
import logging
from pprint import pprint

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

def createUpdateRequests(codes, filesList):
    


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
        createUpdateRequests(codes, jsonFilesBatch)


    # getCodesFromTextFile("futmtu2nzqwmjixmze0ng_m1_fm2112t_20000.txt")


if __name__ == "__main__":
    main()
