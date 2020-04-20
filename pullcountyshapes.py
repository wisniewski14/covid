import json
import requests

filepath="countyinfo"
countys={}
with open(filepath) as f:
	for line in f:
		dat = line.split("|")
		#countys[dat[6]] = dat[0]+"C"+dat[6][2:]
		countys[dat[0]+"C"+dat[6][2:]]= dat[6]


filename = "counties_nws.json"
with open(filename) as f:
	j = json.load(f)
	print(len(j["features"]))

allc=j["features"]
for c in allc:
	c1=c["properties"]["id"]
	c2=countys[c1]
	fips=c2
	nwscode=c1
	cname=c["properties"]["name"]
	print(cname)
	#if "Citrus" in cname:
	while True:
		r = requests.get("https://api.weather.gov/zones/county/"+nwscode)
		if r:
			break
	cinfo=r.json()
	print(c1,c2,cinfo["properties"]["state"],cinfo["properties"]["name"])
	cinfo.pop("@context")
	if cinfo["geometry"]["type"] == "GeometryCollection":
		geoms = cinfo["geometry"]["geometries"]
		cinfo.pop("geometry")
		cinfo["geometry"]={}
		cinfo["geometry"]["type"] = "MultiPolygon"
		cinfo["geometry"]["coordinates"] = []
		for geom in geoms:
			print("type:",geom["type"])
			if geom["type"] == "Polygon":
				cinfo["geometry"]["coordinates"].append(geom["coordinates"][0])
			else:
				cinfo["geometry"]["coordinates"].extend(geom["coordinates"])
	#print(cinfo)
	with open("allcounties/"+fips+".json","w") as f:
		f.writelines(json.dumps(cinfo,indent=2))
