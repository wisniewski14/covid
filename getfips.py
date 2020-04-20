import requests
import json

filepath="countyinfo"
countys={}
with open(filepath) as f:
	for line in f:
		dat = line.split("|")
		countys[dat[6]] = dat[0]+"C"+dat[6][2:]
	
print(json.dumps(countys,indent=4))
print(len(countys))

filepath="counties_merged.csv"
countysused=[]
with open(filepath) as f:
	f.readline()
	for line in f:
		dat = line.split(",")
		fips = dat[20][3:8]
		if fips not in countysused:
			countysused.append(fips)
	
print(json.dumps(countysused,indent=4))
print(len(countysused))


for fips in countysused:
	if fips not in countys:
		print("Lost",fips)

bad=[]
for fips in countys:
	if fips not in countysused:
		bad.append(fips)
		print("not here",fips)

print(len(bad))



exit()


cres={}
cres["type"]="FeatureCollection"
cres["features"]=[]
print("Fetching NWS county data...")
for fips in countysused:
	print("Getting",fips,countys[fips])
	c=0
	while True:
		r=requests.get("https://api.weather.gov/zones/county/"+countys[fips])
		c+=1
		if r or c>10:
			break
	if r:
		item=r.json()
		county = item["properties"]["name"]
		state = item["properties"]["state"]
		print(state,county,c)
		item.pop("@context")
		#print(json.dumps(item, indent=4))
		cres["features"].append(item)
		with open("countyjsons/"+fips+".json","w") as f:
			f.writelines(json.dumps(item,indent=2))
	
with open("cres.json","w") as f:
	f.writelines(json.dumps(cres,indent=2))
