from suds.client import Client
import requests
import time
import zipfile
import StringIO

client = Client(#Your ICAT WSDL URL here) #Get the WSDL file for SOAP. Currently uses the ICAT instance for public Diamond data
icat = client.service
factory = client.factory

#Get a session ID:
print("Logging in and obtaining sessionId ...")
credentials = factory.create("login.credentials")
entry = factory.create("login.credentials.entry")
entry.key = "username"
entry.value = #Your FedID here
credentials.entry.append(entry)
entry = factory.create("login.credentials.entry")
entry.key = "password"
entry.value = #Your password here
credentials.entry.append(entry)
sessionId = icat.login("ldap", credentials) 
print("sessionId is: " + sessionId)

#Search for all datasets and display one:
print("Querying ICAT Server for all datasets ...")
search = icat.search(sessionId, "SELECT ds.id FROM Dataset ds") #Replace this with whatever JPQL query you like
print("Dataset IDs found:")
print(search)
dsIndex = 20
ds = icat.get(sessionId, "Dataset", search[dsIndex]) #Extract dataset as an example
print("A dataset:")
print(ds)

#Use the IDS REST API to download this dataset:

#Tell IDS to prepare data for download:
print("Downloading data from IDS ...")
prepareDataURL = #Your IDS prepareData URL here
data = {"sessionId":str(sessionId),"datasetIds":str(search[dsIndex])}
prepareDataResp = requests.post(prepareDataURL, data = data)
print("prepareData Request Status: ")
print(prepareDataResp)
preparedId = str(prepareDataResp.text)
print("preparedId: " + preparedId)

#Ping isPrepared every 10 seconds until data is ready:
isPrepared ="false"
isPreparedURL = #Your IDS isPrepared URL here
isPreparedParams = {"preparedId":str(preparedId)}
print("Checking if data is ready yet ...")
while (isPrepared == "false"):
	isPrepared = (requests.get(isPreparedURL, params=isPreparedParams)).text
	print("isPrepared: " + isPrepared)
	time.sleep(10)

#Download the data to local directory:
print("Downloading data ...")
getDataURL = #Your IDS getData URL here
getDataParams = {"preparedId": preparedId, "outname": "myData"}
getDataResp = requests.get(getDataURL, params=getDataParams, stream=True)
z = zipfile.ZipFile(StringIO.StringIO(getDataResp.content)) #Store as zip file
z.extractall() #Extract zip file
print("Data downloaded to local directory")
