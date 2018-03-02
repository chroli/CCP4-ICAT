from suds.client import Client
from icat.ids import IDSClient

client = Client(#Your ICAT WSDL URL here) #Get the WSDL file for SOAP. Currently uses the ICAT instance for public Diamond data
icat = client.service
factory = client.factory

#Get a session ID:
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
print(sessionId)

#Search for all datasets and display the first one:
search = icat.search(sessionId, "SELECT ds.id FROM Dataset ds") #Replace this with whatever JPQL query you like
print(search)
ds = icat.get(sessionId, "Dataset", search[0]) #Extract first dataset as an example
print(ds)

#Use Python-ICAT to download data:
idsURL = #Your IDS URL here
myClient = IDSClient(idsURL, sessionId)
