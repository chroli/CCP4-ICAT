The Python scripts in this repo will talk to an ICAT/IDS setup to find metadata and download the corresponding data

`soap.py` uses the SOAP interface of ICAT Server to get metadata, which is then downloaded via the IDS REST API. `rest.py` is similar, but it uses the REST API of ICAT Server instead of SOAP. `soap_pycat.py` abstracts away from this by using the Python-ICAT module. This script has a problem - I cannot get the datasets to save as zip files. It is therefore in a less well-developed state than `soap_final.py`. `soap_full.py` extends `soap.py` to be of practical use by adding new SQL queries. `soap_final.py` is the final version of the SOAP scripts that constructs a Python dictionary of metadata based on visit IDs and then downloads datasets and datafiles.

They can all be run simply with `python <script name>`

They require the `requests` and `suds` modules to run so ensure that they are installed via pip. `soap_pycat.py` will need Python-ICAT to be installed. 




