import requests
import json
link = "https://api.weather.gov/"
#response = requests.get(link)
#print(response.json())

link = "https://api.weather.gov/alerts/"
r=requests.get(link)
alertlist={}
for alert in r.json()["features"]:
	event = alert["properties"]["event"]
	last = event.split()[-1]
	if alert["properties"]["severity"] == "Severe" and any(x == last for x in ["Watch","Warning"]):
		area = alert["properties"]["areaDesc"]
		area = alert["properties"]["areaDesc"]
		zones = alert["properties"]["affectedZones"]
		sames = alert["properties"]["geocode"]["SAME"]
		#for zone in zones:
		for same in sames:
			if same in alertlist:
				if event not in alertlist[same]:
					alertlist[same].append(event)
			else:
				alertlist[same]=[event]
		#print(json.dumps( alert["properties"]["areaDesc"],indent=4))
		#print 
for same in sorted(alertlist):
	print(same[1:6],alertlist[same])
exit()
statelist={}
for key in alertlist:
	r2 = requests.get(key)
	name = r2.json()["properties"]["name"] 
	state = r2.json()["properties"]["state"] 
	if name != None and state != None:
		#print(state,",",name,",",alertlist[key])
		print(json.dumps(r2.json(),indent = 4))
		if state not in statelist:
			statelist[state]={}
		statelist[state][name] = alertlist[key]
for state in sorted(statelist):
	#print(state)
	for county in sorted(statelist[state]):
		print(state+", "+county+", "+statelist[state][county])
#print(json.dumps(sorted(statelist),indent = 4))
exit()

link = "https://api.weather.gov/products/types/ADA"
link = "https://api.weather.gov/products/types/"
s = requests.Session()
#s.headers.update({'': ''})
r=s.get(link)
print(json.dumps(r.json(),indent=4))
for type in r.json()["@graph"]:
	name = type["productName"]
	final = name.split()[-1]
	#if any(x in type["productName"] for x in ["Watch","Warning"]):
	if any(x == final for x in ["Watch","Warning"]):
		code = type["productCode"]
		#print(type["productCode"])
		print("Getting",code,"(",name,")...")
		r2=requests.get(link+code)
		print(len(r2.json()["@graph"]))
		print(json.dumps(r2.json(),indent=4))
		
		
