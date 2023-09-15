import logging
import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import json
import csv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

api_key = os.getenv('CLOCKIFY_APIKEY')

ws_id = os.getenv('CLOCKIFY_WORKSPACEID')


def setTotalTime(entry):
	entry["total"] = hhmmFromMinutes(getWorkingTimeMinutes(entry["from"],entry["till"],entry["pause"]))


def mergeEntries(entries):
	retEntries = []
	for entry in entries:
		append = True
		for retEntry in retEntries:
			if retEntry["projectName"] == entry["projectName"] and retEntry["date"] == entry["date"] and retEntry["clientName"] == entry["clientName"] and retEntry["description"] == entry["description"]:
				mergeEntry(retEntry,entry)
				append = False
		if append == True:
			retEntries.append(entry)
	return retEntries

def mergeEntry(entryTarget,entrySource):
	# merge descriptions
	if entrySource["description"] not in entryTarget["description"]:
		entryTarget["description"] = entryTarget["description"] + "; "+entrySource["description"]

	workTimeTarget = getWorkingTimeMinutes(entryTarget["from"],entryTarget["till"],entryTarget["pause"])
	workTimeSource = getWorkingTimeMinutes(entrySource["from"],entrySource["till"],entrySource["pause"])
	workTimeAll = workTimeTarget + workTimeSource

	#print(workTimeTarget)
	#print(workTimeSource)
	entryTarget["from"] = getLowestHHMM(entryTarget["from"],entrySource["from"])
	entryTarget["till"] = getHighestHHMM(entryTarget["till"],entrySource["till"])

	newWorkTime = getWorkingTimeMinutes(entryTarget["from"],entryTarget["till"],"00:00")
	newPause = newWorkTime - workTimeAll
	entryTarget["pause"] = hhmmFromMinutes(newPause)
	setTotalTime(entryTarget)


def getLowestHHMM(one,two):
	if minutesFromHHMM(one) < minutesFromHHMM(two):
		return one
	return two

def getHighestHHMM(one,two):
	if minutesFromHHMM(one) > minutesFromHHMM(two):
		return one
	return two

def getWorkingTimeMinutes(start,end,pause):
	return minutesFromHHMM(end) - minutesFromHHMM(start) - minutesFromHHMM(pause)

def minutesFromHHMM(hhmm):
	t = 0
	for u in hhmm.split(':'):
		t = 60 * t + int(u)
	return t

def hhmmFromMinutes(minutes):
	return '{:02d}:{:02d}'.format(*divmod(minutes, 60))







headers = {
    'content-type': 'application/json', 
    'X-Api-Key': api_key
}
payloadJSON = {
	"dateRangeStart":   "2023-08-01T00:00:00.000",
	"dateRangeEnd":     "2023-08-31T23:59:59.000",
	"sortOrder":        "ASCENDING",
	"detailedFilter":   {
		"page": 1,
		"pageSize": 500
    }
}

r = requests.post("https://reports.api.clockify.me/v1/workspaces/"+ws_id+"/reports/detailed", json=payloadJSON, headers=headers)
value = r.json()   

retValue = {
	"response": value,
	"entries": []
}

for timeentry in value["timeentries"]:
		entry = {}

		startString = timeentry["timeInterval"]["start"]#.replace("+02:00","+0200") # needs to be a regex
		start = datetime.strptime(startString,"%Y-%m-%dT%H:%M:%S%z") #%z
		entry["date"] = start.strftime("%d.%m.%y")
		entry["from"] = start.strftime("%H:%M")
		end = datetime.strptime(timeentry["timeInterval"]["end"],"%Y-%m-%dT%H:%M:%S%z") #%z
		entry["till"] = end.strftime("%H:%M")
		#print(minutesFromHHMM(entry["till"]))
		entry["pause"] = "00:00"

		entry["description"] = timeentry["description"]
		entry["clientName"] = timeentry.get("clientName","")
		entry["projectName"] = timeentry.get("projectName","")
		entry["location"] = "Wildberg"
		setTotalTime(entry)
		retValue["entries"].append(entry)

retValue["entries"] = mergeEntries(retValue["entries"])
print(json.dumps(retValue,indent=2))
with open('demo.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    for entry in retValue["entries"]:
        csv_writer.writerow([
			entry.get("date"),
			entry.get("location"),
			entry.get("description"),
			entry.get("from"),
			entry.get("till"),
			entry.get("pause"),
			entry.get("total"),
			entry.get("clientName"),
			entry.get("projectName"),			
		])

