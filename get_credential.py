import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
#from apiclient.discovery import build

storage = Storage('/tmp/OAuthcredentials.txt')

#retrieve if available
credentials = storage.get()

scope = ['https://spreadsheets.google.com/feeds', 'https://docs.google.com/feeds']
if  credentials is None:
    credentials = run(flow_from_clientsecrets("/home/tammy/.pes/client_secret_608725870488.apps.googleusercontent.com.json", scope=scope), storage)
else:
    print 'GDrive credentials are still current'

#authorise
http = httplib2.Http()
http = credentials.authorize(http)
print 'Authorisation successfully completed'

#store for next time
storage.put(credentials)
