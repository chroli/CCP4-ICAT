from suds.client import Client
import requests
import time
import zipfile
import StringIO

#Copy a file from infile to outfile. Used for saving single datafiles:
def copyfile(infile, outfile, chunksize=8192):
    
    while True:
        chunk = infile.read(chunksize)
        if not chunk:
            break
        outfile.write(chunk)

#Check if the time on sessionId is running out and refresh if it is:
def checkSessionId(sessionId):

	client = Client("https://icat02.diamond.ac.uk/ICATService/ICAT?wsdl") 
	icat = client.service
	if (icat.getRemainingMinutes(sessionId) < 5):
		icat.refresh(sessionId)

#Queries ICAT Server to build a dictionary of visits, datasets and datafile metadata:
def queryICAT(fedID, userPassword):

	results = {"sessionID": "", "visits": []} #Initialise the dictionary to be returned

	client = Client("https://icat02.diamond.ac.uk/ICATService/ICAT?wsdl") #Get the WSDL file for SOAP. Currently uses the ICAT instance for public Diamond data
	icat = client.service
	factory = client.factory

	#Get a session ID:
	credentials = factory.create("login.credentials")
	entry = factory.create("login.credentials.entry")
	entry.key = "username"
	entry.value = fedID
	credentials.entry.append(entry)
	entry = factory.create("login.credentials.entry")
	entry.key = "password"
	entry.value = userPassword
	credentials.entry.append(entry)
	sessionId = icat.login("ldap", credentials) 
	results["sessionID"] = sessionId

	visitIDs = icat.search(sessionId, "SELECT i.visitId FROM Investigation i") #Query for all visit IDs

	#Build the dictionary for each visit ID:
	visitDict = {"visitID": "", "visitName": "", "visitDate": "", "datasets": []}
	visitDictList = []
	for vid in visitIDs:

		visitDict["visitID"] = vid
		visitDict["visitName"] = icat.search(sessionId, "SELECT v.name FROM Investigation v where v.visitId=" + "'" + vid + "'")
		visitDict["visitDate"] = icat.search(sessionId, "SELECT v.startDate FROM Investigation v where v.visitId=" + "'" + vid + "'")

		datasetDict = {"ID": "", "path": "", "size": "", "date": "", "files": []}
		datasetDictList = []	

		datasetIDs = icat.search(sessionId, "SELECT ds.id FROM Dataset ds WHERE ds.investigation.visitId=" + "'" + vid + "'")
		for did in datasetIDs:
			datasetDict["ID"] = did
			datasetDict["path"] = icat.search(sessionId, "SELECT ds.name FROM Dataset ds WHERE ds.id=" + "'" + str(did) + "'")
			datasetDict["date"] = icat.search(sessionId, "SELECT ds.startDate FROM Dataset ds WHERE ds.id=" + "'" + str(did) + "'")

			datafileDict = {"name": "", "size": "", "date": "", "ID": ""}
			datafileDictList = []
			datafileIDs = icat.search(sessionId, "SELECT df.id FROM Datafile df WHERE df.dataset.id=" + "'" + str(did) + "'")
			for dfid in datafileIDs:
				datafileDict["name"] = icat.search(sessionId, "SELECT df.name FROM Datafile df WHERE df.id=" + "'" + str(dfid) + "'")	
				datafileDict["size"] = icat.search(sessionId, "SELECT df.fileSize FROM Datafile df WHERE df.id=" + "'" + str(dfid) + "'") #Size returned in bytes
				datafileDict["date"] = icat.search(sessionId, "SELECT df.createTime FROM Datafile df WHERE df.id=" + "'" + str(dfid) + "'")
				datafileDict["ID"] = dfid
				datafileDictList.append(datafileDict.copy())		

			datasetDict["files"] = datafileDictList
			datasetDictList.append(datasetDict.copy())

		visitDict["datasets"] = datasetDictList	
		visitDictList.append(visitDict.copy())

	results["visits"] = visitDictList
	checkSessionId(sessionId)

	return results

#Given the information in the dictionary, download datafiles and datasets using IDS:
def fetchDataFromICAT(sessionId, datasetID, filesList, outputDirectory): #filesList is a list of file IDs

	idsBaseURL = "https://ids01.diamond.ac.uk/ids"
	prepareDataURL = idsBaseURL + "/prepareData"
	isPreparedURL = idsBaseURL + "/isPrepared"
	getDataURL = idsBaseURL + "/getData"

	try:
		if (len(filesList) == 0):
		
			#Use the IDS REST API to download the data:

			#Tell IDS to prepare data for download:
			data = {"sessionId":str(sessionId),"datasetIds":datasetID}
			prepareDataResp = requests.post(prepareDataURL, data = data)
			preparedId = str(prepareDataResp.text)

			#Ping isPrepared every 30 seconds until data is ready:
			isPrepared ="false"
			isPreparedParams = {"preparedId":str(preparedId)}
			while (isPrepared == "false"):
				isPrepared = (requests.get(isPreparedURL, params=isPreparedParams)).text
				time.sleep(30)
				checkSessionId(sessionId)

			#Download the data to local directory:
			getDataParams = {"preparedId": preparedId}
			getDataResp = requests.get(getDataURL, params=getDataParams, stream=True)
			z = zipfile.ZipFile(StringIO.StringIO(getDataResp.content)) #Store as zip file
			z.extractall(outputDirectory) #Extract zip file

		else:
			
			for f in filesList:
				
				#Use the IDS REST API to download the data:
				
				#Tell IDS to prepare data for download:
				data = {"sessionId":str(sessionId),"datafileIds": f}
				prepareDataResp = requests.post(prepareDataURL, data = data)
				preparedId = str(prepareDataResp.text)

				#Ping isPrepared every 30 seconds until data is ready:
				isPrepared ="false"
				isPreparedParams = {"preparedId":str(preparedId)}
				while (isPrepared == "false"):
					isPrepared = (requests.get(isPreparedURL, params=isPreparedParams)).text
					time.sleep(30)
					checkSessionId(sessionId)

				#Download the data to local directory:
				getDataParams = {"preparedId": preparedId}
				getDataResp = requests.get(getDataURL, params=getDataParams, stream=True)
				with open(outputDirectory + "/myData", 'wb') as f2:
            				copyfile(StringIO.StringIO(getDataResp.content), f2)

		return "success"

	except:
		return "failed"


#Code to test the functions:

result = queryICAT("Your FedId here", "Your password here")
print(result)
sessionId = result["sessionID"]
print(fetchDataFromICAT(sessionId, result["visits"][0]["datasets"][0]["ID"], [result["visits"][0]["datasets"][0]["files"][0]["ID"]], "path")) #Test datafile download
print(fetchDataFromICAT(sessionId, result["visits"][1]["datasets"][0]["ID"], [], "path")) #Test whole dataset download



