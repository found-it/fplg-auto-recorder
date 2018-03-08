import gspread
from oauth2client.service_account import ServiceAccountCredentials
from time import sleep
import spidev

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
sheet = client.open("autotest").sheet1

spi=spidev.SpiDev()
spi.open(0,0)
def readChannel(channel):
    adc=spi.xfer2([1,(8+channel)<<4,0])
    data=((adc[1]&3)<<8)+adc[2]
    return data
retI=1
def getDistance(reading):
	if reading is not 0:
		if retI:
			return int(43300*reading**(-1.236))
		else:	
			return 43300*reading**(-1.236)
	return 80
count =1
try:
    while 1:
        val=readChannel(0)
        sheet.update_cell(count, 1, getDistance(val))
        print "----------------------------"
        print val
        print getDistance(val)
        sleep(1)
        count+=1
finally:
    spi.close()
# Extract and print all of the values
#list_of_hashes = sheet.get_all_records()
#print(list_of_hashes)
#sheet.update_cell(1, 1, "I just wrote to a spreadsheet using Python!")
