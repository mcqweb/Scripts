#!/usr/bin/python3

import requests
import time
import datetime
from bs4 import BeautifulSoup

anyoneHome = False
def CheckHub():
	global anyoneHome

	# Check the time too, we want the camera on, even if someone's home at night
	now = datetime.datetime.now()
	#print(now.hour)
	if now.hour==23:
		print("It's 11pm, lets turn it on")
		ToggleKitchen('enable')
		exit()
	else:	
		# We're going to check if anyone's home
		r  = requests.get("http://192.168.1.254")

		data = r.text
		soup = BeautifulSoup(data,"html.parser")
		phoneCount = 0
		for mainTable in soup.find_all('div', {'id' : 'frame_div'}):	
			for innerTable in mainTable.find_all('table'):
				for TableCells in innerTable.find_all('td'):		
					if "iphone" in TableCells.text.lower():
						if not anyoneHome:
							print("{0}:{1} on {2}/{3}/{4}".format(now.hour,str(now.minute).zfill(2),now.day,now.month,now.year))
							if phoneCount==0:
								print("I think someone is home, I've found a phone")
							print(TableCells.text)
						phoneCount += 1
		
		if phoneCount == 0 and anyoneHome:
			#Someone's Gone Out
			print("No-one Home")
			anyoneHome = False
			ToggleKitchen('enable')
		elif phoneCount > 0 and not anyoneHome:
			print("Someone's Home")
			anyoneHome = True
			ToggleKitchen('disable')
		else:
			print(phoneCount)
			print(anyoneHome)

		time.sleep(300)
	CheckHub()
					

def ToggleKitchen(toggle):
	headers = {
		'Host': 'prod.immedia-semi.com',
		'Content-Type': 'application/json',
	}
	data = '{ "password" : "", "client_specifier" : "iPhone 9.2 | 2.2 | 222", "email" : "" }'
	res = requests.post('https://prod.immedia-semi.com/login', headers=headers, data=data)
	#print(res.json())
	authToken = res.json()["authtoken"]["authtoken"]
	#print(authToken)

	headers = {
		"Host": "prod.immedia-semi.com",
		'Content-Type': 'application/json',
	    "TOKEN_AUTH": authToken,
	}

	kitchenCamera = 'https://rest-prde.immedia-semi.com/network/<>/camera/<>/'+toggle
	print(kitchenCamera)
	res = requests.post(kitchenCamera, headers=headers)
	#CameraListJson = res.json()
	print(res)
	
CheckHub()
