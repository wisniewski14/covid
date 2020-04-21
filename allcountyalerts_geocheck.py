import requests
import datetime
import json
from shapely.geometry import MultiPolygon, Polygon, shape, GeometryCollection
laxfile="lax_fips_list.csv"
laxfips=[]
with open(laxfile) as f:
	f.readline()
	for line in f:
		laxfips.append(line.strip())


print("making dict of NWS codes, adding FIPS...")
filepath="countyinfo"
countys={}
with open(filepath) as f:
	for line in f:
		dat = line.split("|")
		print(dat[6])
		if dat[6] in laxfips:
			countys[dat[0]+"C"+dat[6][2:]]= {"fips": dat[6]}


print("Loading county geometries...")
for coun in countys:
	filename="allcounties/"+countys[coun]["fips"]+".json"
	with open(filename) as f:
		cdata=json.load(f)
	countys[coun]["geometry"]=cdata["geometry"] 
	countys[coun]["state"]=cdata["properties"]["state"]
	countys[coun]["name"]=cdata["properties"]["name"]
	countys[coun]["events"]=[]

print("Fetching NWS alert data...")
link="https://api.weather.gov/alerts/active?severity=severe"
#link="https://api.weather.gov/alerts/"
r=requests.get(link)
datestr=datetime.datetime.strftime(datetime.datetime.now(),"%Y%m%d_%H%M")
with open(datestr+"_nws_alerts_active_severe.json","w") as f:
	f.writelines(json.dumps(r.json(),indent=4))

events = r.json()["features"]


#for event in events:
#	for nwscode in event["properties"]["geocode"]["UGC"]:
#		if nwscode in countys:
#			print(event["properties"]["event"],"in",countys[nwscode]["name"],countys[nwscode]["state"])
#			if event["geometry"]:
#				countys[nwscode]["events"].append(event["geometry"]["coordinates"])
#			else:
#				print("No geometry.")


for coun in countys:
	en=len(countys[coun]["events"])
	if en>1:
		print(countys[coun]["name"],countys[coun]["state"],en)

for coun in countys:
	# Get county polygon
	cgeom=countys[coun]["geometry"]["coordinates"]
	ctype = countys[coun]["geometry"]["type"]
	if ctype == "Polygon":
		cpoly=Polygon(cgeom[0])
	else:
		polys=[]
		for poly in cgeom:
			polys.append(Polygon(poly[0]))
		cpoly=MultiPolygon(polys)
	cpoly=cpoly.buffer(0)
	eventcount=0
	for event in events:
		# Get event polygon
		if event["geometry"]:
			ecoords=event["geometry"]["coordinates"]
			if len(ecoords)==1:
				epoly=Polygon(ecoords[0])
			else:
				polys=[]
				for poly in ecoords:
					polys.append(Polygon(poly[0]))
				epoly=MultiPolygon(polys)
			epoly=epoly.buffer(0)
			if epoly.intersects(cpoly):
				if eventcount==0:
					combinedpoly=epoly
				else:	
					combinedpoly=combinedpoly.union(epoly)
				eventcount+=1
	if eventcount>0:
		# Get intersection
		combinedpoly=combinedpoly.buffer(0)
		covered=(combinedpoly.intersection(cpoly).area/cpoly.area)*100
		countys[coun]["affected"]=covered
		print(countys[coun]["name"],countys[coun]["state"],covered)
	else:
		countys[coun]["affected"]=0.0

# Generate csv
csvlist=[]
for coun in countys:
	csvlist.append([countys[coun]["fips"],str(round(countys[coun]["affected"],2)),countys[coun]["state"],countys[coun]["name"]])
print(csvlist)

with open(datestr+"_counties_alerts_active_severe_affected.csv","w") as f:
	f.write("FIPS,percent_affected,state,county\n")
	for c in sorted(csvlist):
		f.write(",".join(c)+'\n')
	




# Generate geojson (~600MB)
res={}
res["type"]="FeatureCollection"
res["features"]=[]
for coun in countys:
	cjson={}
	cjson["id"]=countys[coun]["fips"]
	cjson["type"]="Feature"
	cjson["geometry"]=countys[coun]["geometry"]
	cjson["properties"]={}
	cjson["properties"]["affected"]=countys[coun]["affected"]
	cjson["properties"]["state"]=countys[coun]["state"]
	cjson["properties"]["name"]=countys[coun]["name"]
	res["features"].append(cjson)

with open(datestr+"_counties_alerts_active_severe_affected.json","w") as f:
	f.writelines(json.dumps(res,indent=4))



