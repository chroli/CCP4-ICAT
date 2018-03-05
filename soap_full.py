from suds.client import Client
import requests
import time
import zipfile
import StringIO
import os

def downloadDataset(datasetID):

	#Use the IDS REST API to download this dataset:

	#Tell IDS to prepare data for download:
	print("Downloading data from IDS ...")
	prepareDataURL = #IDS prepareData URL here
	data = {"sessionId":str(sessionId),"datasetIds":datasetID}
	prepareDataResp = requests.post(prepareDataURL, data = data)
	print("prepareData Request Status: ") 
	print(prepareDataResp)
	preparedId = str(prepareDataResp.text)
	print("preparedId: " + preparedId)

	#Ping isPrepared every 30 seconds until data is ready:
	isPrepared ="false"
	isPreparedURL = #IDS isPrepared URL here
	isPreparedParams = {"preparedId":str(preparedId)}
	print("Checking if data is ready yet ...")
	while (isPrepared == "false"):
		isPrepared = (requests.get(isPreparedURL, params=isPreparedParams)).text
		print("isPrepared: " + isPrepared)
		time.sleep(30)

	#Download the data to local directory:
	print("Downloading data ...")
	getDataURL = #IDS getData URL here
	getDataParams = {"preparedId": preparedId}
	getDataResp = requests.get(getDataURL, params=getDataParams, stream=True)
	return getDataResp


client = Client(#ICAT Server WSDL URL here) #Get the WSDL file for SOAP. Currently uses the ICAT instance for public Diamond data
icat = client.service
factory = client.factory

#Get a session ID:
print("Logging in and obtaining sessionId ...")
credentials = factory.create("login.credentials")
entry = factory.create("login.credentials.entry")
entry.key = "username"
entry.value = #FedID here
credentials.entry.append(entry)
entry = factory.create("login.credentials.entry")
entry.key = "password"
entry.value = #Password here
credentials.entry.append(entry)
sessionId = icat.login("ldap", credentials) 
print("sessionId is: " + sessionId)

#Search for all visit IDs:
print("Querying ICAT Server for all visit IDs ...")
search = icat.search(sessionId, "SELECT i.visitId FROM Investigation i")
print("Visit IDs found:")
print(search)
visitIDs = search

#Extract dataset IDs and dataset metadata from visit IDs, and download the datasets:
datasetIDs = []
j = 0 #Used for renaming directories once downloaded
for vid in visitIDs:
	#Get dataset IDs:
	query = "SELECT ds.id FROM Dataset ds WHERE ds.investigation.visitId=" + "'" + vid + "'"
	search = icat.search(sessionId, query)
	print("Dataset IDs found:")
	print(search)
	print("Downloading datasets for this visit ID...")
	#Download all datasets for the visit ID:
	for i in range(0, len(search) - 1):
		getDataResp = downloadDataset(search[i])
		z = zipfile.ZipFile(StringIO.StringIO(getDataResp.content)) #Store as zip file
		z.extractall() #Extract zip file
		cwd = os.getcwd() #Current working directory, where the data is being placed
		os.rename(cwd + "/dls", cwd + "/dls" + str(j)) #Rename directory from 'dls' to stop overwriting
		print("Data downloaded to local directory")
		j = j + 1

	print("Dataset metadata:")
	#Get dataset metadata:
	query = "SELECT ds FROM Dataset ds WHERE ds.investigation.visitId=" + "'" + vid + "'"
	search = icat.search(sessionId, query)
	print(search)	


