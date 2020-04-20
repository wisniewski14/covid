import json
import requests
from shapely.geometry import MultiPolygon, Polygon, shape, GeometryCollection
import os

print("Loading zip code geojson...")
filepath="zippolys.json"
with open(filepath) as f:
	zips=json.load(f)["features"]

print("Converting zip code polygons...")
zippolys=[]
c=0
for zip in zips:
	c+=1
	if c>1000:
		break
	ztype=zip['geometry']['type']
	if ztype == "MultiPolygon":
		polys=[]
		for poly in zip['geometry']['coordinates']:
			polys.append(Polygon(poly[0]))
		zippolys.append(MultiPolygon(polys))
	else:	
		zippolys.append(Polygon(zip['geometry']['coordinates'][0]))

print("Fetching NWS alert data...")
r=requests.get("https://api.weather.gov/alerts?severity=severe&certainty=observed")
events = r.json()["features"]

print("Converting alert polygons...")
eventpolys=[]
for event in events:
	if event['geometry']:
		eventpolys.append(Polygon(event['geometry']['coordinates'][0]))

print("Finding zip codes with >10% event coverage...")
eventzips={}
for k in range(len(eventpolys)):
	for i in range(len(zippolys)):
		if eventpolys[k].intersects(zippolys[i]):
			zip = zips[i]["properties"]["ZIP_CODE"]
			event = events[k]["properties"]["event"]
			covered=(eventpolys[k].intersection(zippolys[i]).area/zippolys[i].area)*100
			if covered > 10:
				if zip not in eventzips:
					eventzips[zip]={"zipind": i, "events": [event]}
				elif event not in eventzips[zip]["events"]:
					eventzips[zip]["events"].append(event)

print("Generating results geojson...")
results={}
results["type"]="FeatureCollection"
results["features"]=[]
for zip in eventzips:
	results["features"].append(zips[eventzips[zip]["zipind"]])
	results["features"][-1]["properties"]={"zip": zip, "events": eventzips[zip]["events"]}
	
print("Writing to results.json file...")
with open("results.json","w") as r:
	r.writelines(json.dumps(results,indent=4))

print("Done.")
