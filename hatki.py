#! /usr/bin/python3
import argparse
import sys
import requests
import os
import re
from datetime import datetime


#####################
##  MAIN FUNCTION  ##
#####################

# This function is called at the bottom of the file
def main():
    printLogo()

    # Get command line arguments
    args = getCommandLineArguments()
    print("These command line arguments will be used: " + str(args))

    # Read the token file
    homeAssistantToken = readTokenFromFile(args.tokenfile)

    # Request the "States" from the Home Assistant API via REST
    homeAssistantStates = requestHomeAssistantStates(args.url, homeAssistantToken)

    # Read the HTML template file(s)
    htmlTemplates = readHtmlTemplateFiles(args.inputfolder)

    # Replace the placeholders in the HTML template files with the states from Home Assistant
    generatedHtml = replacePlaceholdersWithStates(htmlTemplates, homeAssistantStates, args.url, args.outputfolder)

    print("time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # Write the generated HTML files
    writeHtmlFiles(generatedHtml, args.outputfolder)



#################
##  FUNCTIONS  ##
#################

def printLogo():
    print(" __              __    __     __                                        ")
    print("|  |__  _____  _/  |_ |  | __|__|                                       ")
    print("|  |  \ \__  \ \   __\|  |/ /|  |  hatki - Home Assistant To Kindle/HTML")
    print("|   |  \ / __ \_|  |  |    \ |  |  v2.1 (2023-03-27) by Knoe-WG         ")
    print("|___|__/(______/|__|  |__|__\|__|                                       ")
    print("")


def getCommandLineArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="Home Assistant API URL, e.g. https://localhost:8123/api", required=True)
    parser.add_argument("-t", "--tokenfile", default="token.txt",
                        help="File that contains the Token for the Home Assistant API. (default value: %(default)s)")
    parser.add_argument("-i", "--inputfolder", default="html-templates",
                        help="Path to the folder that contains the HTML templates. NOTE: Subfolders are NOT supported. (default value: %(default)s)")
    parser.add_argument("-o", "--outputfolder", default="generated-html", 
                        help="Path to the folder where the generated HTML files will be written. (default value: %(default)s)")

    try:
        args = parser.parse_args()
    except:
        print("Use -h for help")
        sys.exit(0)
    return args


def readTokenFromFile(fileName):
    print("Reading the Home Assistant token from file [" + fileName + "] ...")
    token = open(fileName, "r").read()

    # Check if the token starts with "Bearer", which it should not
    # HINT: Make sure to have no \n (newline in your token)
    if token.startswith("Bearer"):
        print("[ ERROR ] The Home Assistant token must not start with \"Bearer\". Instead, only put the token itself into the file.")
        sys.exit(1)

    print("[ OK ] The Home Assistant token has a length of [" + str(len(token)) + "] characters")
    return token


def requestHomeAssistantStates(url, token):
    print("Validating the given URL ...")
    # Check if the URL ends with "api"
    if not (url.endswith("api") or url.endswith("api/")):
        print("[ ERROR ] The Home Assistant URL must end with \"api\"")
        sys.exit(1)

    # Append "/" if needed
    if not url.endswith("/"):
        url += "/"
    
    url += "states"
    headers = {"Authorization": "Bearer " + token}

    print("Requesting the \"States\" from the Home Assistant API with URL: [" + url + "] ...")
    response = requests.get(url, headers=headers)

    if not response.status_code == 200:
        print("[ ERROR ] The HTTP status code is [" + str(response.status_code) + "]. Response body: [" + response.text + "]")
        sys.exit(1)
    else:
        responseJson = response.json()
        print("[ OK ] The response is [" + str(len(response.text)) + "] characters long and contains [" + str(len(response.json())) + "] states")
        return responseJson


def readHtmlTemplateFiles(inputfolder):
    print("Reading the HTML template files from folder [" + inputfolder + "] ...")
    folderContent = os.listdir(inputfolder) # also includes folders, which we don't want
    htmlTemplates = {}
    for fileName in folderContent:
        filePath = os.path.join(inputfolder, fileName)
        # Filter out sub-folders and files that don't end with ".html"
        if os.path.isfile(filePath) and fileName.endswith(".html"):
            print("Reading file [" + fileName + "] ... ", end="")
            htmlTemplates[fileName] = open(filePath, "r").read()
            print("[ OK ] length: [" + str(len(htmlTemplates[fileName])) + "] characters")

    print("[ OK ] Read [" + str(len(htmlTemplates)) + "] file(s)")
    return htmlTemplates


def replacePlaceholdersWithStates(htmlTemplates, homeAssistantStates, url, outputFolder):
    print("Replacing placeholders with States from Home Assistant...")

    # For every HTML template file
    for htmlTemplateName in htmlTemplates:
        htmlTemplate = htmlTemplates[htmlTemplateName]
        placeholders = re.findall("\{\{\S+\}\}", htmlTemplate)
        
        # For every placeholder in that file
        for placeholder in placeholders:

            placeholderWithoutBraces = placeholder[2:-2]

            # Split up the placeholder in the entity ID and the JsonPath (not a real JsonPath...)
            splitResult = placeholderWithoutBraces.split(":")

            if len(splitResult) < 2:
                print("[ WARNING ] The placeholder [" + placeholder + "] does not include a \":\". It will be ignored.")
                state = "?"
            else:
                stateEntityId = placeholderWithoutBraces.split(":")[0]
                stateJsonPath = placeholderWithoutBraces.split(":")[1]
                state = getState(stateEntityId, stateJsonPath, homeAssistantStates)

                if state == "unavailable" or state == "unknown":
                    print("[ WARNING ] The state [" + placeholderWithoutBraces + "] has value [" + state + "] and will be replaced with \"?\".")
                    state = "?"
                # TODO: Think about moving requesting streams to other function    
                if re.match("^/api", state):
                    mr = url[:-4]
                    r = requests.get(mr + state , stream = True)
                    f = open(outputFolder +"/"+ stateEntityId + ".jpg",'wb')
                    f.write(r.content)
                    f.close()
                #If it is a number: Only one decimal place, unless its a special attribute
                match = re.match("^-{0,1}\d+\.{0,1}\d{0,1}", state)
                match_auto = re.match('^attributes*', stateJsonPath)
                if match and not match_auto:
                    state = match.group(0)
            htmlTemplate = htmlTemplate.replace(placeholder, state)
        
        htmlTemplates[htmlTemplateName] = htmlTemplate

    print("[ OK ] Done!")
    return htmlTemplates



def getState(stateId, stateJsonPath, homeAssistantStates):
    # Go through all states
    for state in homeAssistantStates:

        # Find state with given ID
        if state["entity_id"] == stateId:

            # Find the correct JSON value to return
            return getJsonValueWithPath(stateJsonPath, state)

    print("[ WARNING ] The placeholder [" + stateId + "] was in the HTML template but was not foud in Home Assistant. It will be replaced by \"?\".")
    return "?"

def getJsonValueWithPath(path, jsonData):
    path = path.split(".")
    jsonValue = jsonData

    # Go through each path entry and get the corresponding json value
    # This works better than expected
    # TODO: JSON Arrays not yed supported :>
    for pathEntry in path:
        try:
            jsonValue = jsonValue[pathEntry]
        except:
            print("[ WARNING ] Could not read the JSON value with path [" + str(path) + "]. Is the path correct? Will use \"?\"")
            return "?"
    
    return jsonValue



def writeHtmlFiles(generatedHtml, outputFolder):
    print("Writing the generated HTML files to folder [" + outputFolder + "] ... ")

    # TODO create output folder if it does not exist

    for fileName in generatedHtml:
        htmlContent = generatedHtml[fileName]
        filePath = os.path.join(outputFolder, fileName)
        print("Writing file ["  + filePath + "] ...", end="")
        f = open(filePath, "w")
        length = f.write(htmlContent)
        f.close()

        print("[ OK ] Wrote [" + str(length) + "] characters")
    
    print("[ OK ] Done!")



##########################
##  MAIN FUNCTION CALL  ##
##########################
main()
