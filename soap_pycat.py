from icat.client import Client
import time
import zipfile
import os
import StringIO
import urllib2

#This function copies infile to outfile:
def copyfile(infile, outfile, chunksize=8192):
   
    while True:
        chunk = infile.read(chunksize)
        if not chunk:
            break
        outfile.write(chunk)

#Downloads a dataset given the ID:
def downloadDataset(datasetId):
	preparedId = myClient.prepareData({"Datasets":[datasetId]})
	print("preparedId:")
	print(preparedId)
	
	isPrepared = False
	while (isPrepared == False):
		print(isPrepared)
		isPrepared = myClient.isDataPrepared(preparedId)
		time.sleep(30)

	return myClient.getPreparedData(preparedId)

	
#Login:
myClient = Client("https://icat02.diamond.ac.uk/ICATService/ICAT?wsdl") #ICAT SOAP WSDL URL
credentials = {"username":"", "password":""} #Insert username and password
myClient.login("ldap", credentials)
myClient.add_ids("https://ids01.diamond.ac.uk/ids") #IDS URL

#Find all visit IDs:
visitIds = myClient.search("SELECT i.visitId FROM Investigation i")
print("Visit IDs found:")
print(visitIds)

#For each visit ID, list all datasets and metadata and download:
for vid in visitIds:

	#Get dataset IDs:
	datasetIdQuery = "SELECT ds.id FROM Dataset ds WHERE ds.investigation.visitId=" + "'" + vid + "'"
	datasetIds = myClient.search(datasetIdQuery)
	print("Dataset IDs found:")
	print(datasetIds)

	#Get dataset metadata:
	print("Dataset metadata:")
	datasetMetaQuery = "SELECT ds FROM Dataset ds WHERE ds.investigation.visitId=" + "'" + vid + "'"
	datasetMetadata = myClient.search(datasetMetaQuery )
	print(datasetMetadata)
	print("Downloading datasets for this visit ID...")

	#Download all datasets for the visit ID:
	for i in range(0, len(datasetIds) - 1):
		getDataResp = downloadDataset(datasetIds[i])

		#I have tried several methods to save the dataset, none of which work. It produces gibberish rather than a zip file. The request returns a file-like object, which is different from what the requests library returns:
		'''
		z = zipfile.ZipFile(StringIO.StringIO(getDataResp.content)) #Store as zip file
		z.extractall() #Extract zip file

		with open("code2.zip", "wb") as code:
		    code.write(myData.read())

		with open("myData.out", 'wb') as f:
            		copyfile(myData, f)

		'''		
		print("Data downloaded to local directory")





