import requests
import json
from shapely.geometry import MultiPolygon, Polygon, shape, GeometryCollection

print("making dict of NWS codes, adding FIPS...")
filepath="countyinfo"
countys={}
with open(filepath) as f:
        for line in f:
                dat = line.split("|")
                countys[dat[0]+"C"+dat[6][2:]]= {"fips": dat[6]}


print("Loading county geometries...")
for coun in countys:
	filename="allcounties/"+countys[coun]["fips"]
	with open(filename) as f:
		cdata=json.load(f)
	countys[coun]["geometry"]=cdata["geometry"] 
	countys[coun]["state"]=cdata["properties"]["state"]
	countys[coun]["name"]=cdata["properties"]["name"]
	countys[coun]["events"]=[]

print("Fetching NWS alert data...")
#r=requests.get("https://api.weather.gov/alerts?severity=severe&certainty=observed")
r=requests.get("https://api.weather.gov/alerts?severity=severe")
events = r.json()["features"]

for event in events:
	for nwscode in event["properties"]["geocode"]["UGC"]:
		if nwscode in countys:
			print(event["properties"]["event"],"in",countys[nwscode]["name"],countys[nwscode]["state"])
			countys[nwscode]["events"].append(event["geometry"]["coordinates"])


for coun in countys:
	en=len(countys[coun]["events"])
	if en>1:
		print(countys[coun]["name"],countys[coun]["state"],en)

for coun in countys:
	en=len(countys[coun]["events"])
	if en==0:
		countys[coun]["affected"]=0
	else:
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
		# Get event polygons
		egeoms=countys[coun]["events"]
		eventcount=0
		for event in countys[coun]["events"]:
			if len(event)==1:
				epoly=Polygon(event[0])
			else:
				polys=[]
				for poly in event:
					polys.append(Polygon(poly[0]))
				epoly=MultiPolygon(polys)
			if eventcount==0:
				combinedpoly=epoly
			else:	
				combinedpoly=combinedpoly.union(epoly)
			eventcount+=1
		# Get intersection
		covered=(combinedpoly.intersection(cpoly).area/cpoly.area)*100
		countys[coun]["affected"]=covered
		print(countys[coun]["name"],countys[coun]["state"],covered)


# Generate csv
csvlist=[]
for coun in countys:
	csvlist.append([countys[coun]["fips"],str(round(countys[coun]["affected"],2)),countys[coun]["state"],countys[coun]["name"]])
print(csvlist)

with open("counties_weatheralerts_severe.csv","w") as f:
	for c in sorted(csvlist):
		f.write(",".join(c)+'\n')
	


exit()


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

with open("affectedsevere.json","w") as f:
	f.writelines(json.dumps(res,indent=4))



