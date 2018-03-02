import requests, json
import time
import zipfile
import StringIO

#Login and get a session ID:
loginData = {"plugin":"ldap", "credentials":[{"username":#Your FedID here}, {"password":#Your password here}]}
loginResp = requests.post(#Your ICAT session URL here, data={"json": json.dumps(loginData)})
loginDict = json.loads(loginResp.content) #Convert JSON string to dict
sessionId = loginDict["sessionId"]
print("sessionId: " + sessionId)

#Search for all datasets and display one:
print("Querying ICAT Server for all datasets ...")
searchURL = #Your ICAT entity manager URL here
searchParams = {"sessionId": sessionId, "query": "SELECT ds.id FROM Dataset ds"}
search = requests.get(searchURL, params=searchParams)
print("Dataset IDs found:")
print(search.text)
dsIndex = 25
getParams = {"sessionId": sessionId, "query": "Dataset", "id": json.loads(search.text)[dsIndex]}
ds = requests.get(searchURL, params=getParams)
print("A dataset:")
print(ds.text)

#Use the IDS REST API to download this dataset (this is the same as the soap.py script):

#Tell IDS to prepare data for download:
print("Downloading data from IDS ...")
prepareDataURL = #Your IDS URL here
data = {"sessionId":str(sessionId),"datasetIds":str(json.loads(search.text)[dsIndex])}
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
