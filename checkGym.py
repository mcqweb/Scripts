#!/usr/bin/python3
import requests
import argparse
import urllib.parse
import os
import xml.etree.ElementTree as etree
from bs4 import BeautifulSoup 
import datetime
import smtplib
import html

	
gmail_user = 'abc@googlemail.com'
gmail_pwd = ''

fromaddr = gmail_user
toaddr = 'b@b.com;a@a.com'
emailBody = ''


BOOKING_URL = 'https://mobile-app-back.davidlloyd.co.uk/members/me/bookings?include-others-i-can-book-for'
OCCUPANCY_JSON = 'https://mobile-app-back.davidlloyd.co.uk/clubs/<clubid>/sessions/occupancy'
res = requests.get(OCCUPANCY_JSON)
Occupancy = res.json()
lastDate = ''

today = datetime.datetime.now()
tomorrow = today + datetime.timedelta(days=1)

header={'X-Auth-Token': '',
'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148  DLL/28.0.2'}


# Use 'with' to ensure the session context is closed after use.
res = requests.get(BOOKING_URL, headers=header)
Bookings = res.json()
def decodeMember(base64string):
	MM = ""
	JH = ""
	LM = ""
	if base64string == MM:
		return 'Michael'
	if base64string == JH:
		return 'Jo'
	if base64string == LM:
		return 'Lily'
	return 'Unknown User'

def checkOccupancy(gymClass):
	global emailBody, lastDate
	for instance in Occupancy['sessionsOccupancy']:
		if int(instance['courseInstanceId']) == int(gymClass['details']['courseInstanceId']):
			if gymClass['date'] != lastDate:
				if lastDate != '':
					#Insert a clean line
					emailBody += "\n"
				emailBody += gymClass['date'] +"\n\n"
				lastDate = gymClass['date']
			currentOccupancy = instance['currentOccupancy']
			maxOccupancy = instance['maxOccupancy']
			bookedMember = decodeMember(gymClass['bookedMemberEncodedContactId'])
			emailBody+=" " +gymClass['details']['name'] + " @ " +gymClass['startTime'] + " for "+bookedMember+ " " +str(int((currentOccupancy/maxOccupancy)*100))+"% full ("+str(currentOccupancy)+' out of '+str(maxOccupancy)+")\n"

def isToday(dateText,timeText):
	if dateText == today.strftime('%Y-%m-%d'):
		if int(timeText[:2]) >= int(today.strftime('%H')):
			return True
		else:
			return False
	
def isEarlyTomorrow(dateText,timeText):
	if dateText == tomorrow.strftime('%Y-%m-%d'):
		#It's tomorrow, is it before 5pm?
		if int(timeText[:2]) <= 16:
			return True
		else:
			return False
	
bookings = Bookings['bookings']
bookingcount = 0
for booking in bookings:
	if isToday(booking['date'],booking['startTime']) or isEarlyTomorrow(booking['date'],booking['startTime']):
		if booking['status']=='confirmed':
			bookingcount += 1
			checkOccupancy(booking)

	
print(emailBody)

if bookingcount == 0:
	#No Bookings today
	print("No Bookings in time window")
	exit()
	
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(gmail_user,gmail_pwd)
 

msg = 'Subject: {}\n\n{}'.format('David Lloyd Class Status', emailBody)
for recepient in toaddr.split(';'):
	server.sendmail(fromaddr, recepient, msg)
server.quit()

