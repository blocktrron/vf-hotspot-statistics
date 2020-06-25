#!/usr/bin/env python3
import json
import re
import sys
import time

import requests

API_PATH = "https://www.hotspot.vodafone.de/api/v4/map/area?lat1={toprightlat}&lng1={toprightlon}" \
           "&lat2={lowleftlat}&lng2={lowleftlon}&dpi=72 "

MAC_REGEX = re.compile(r'(?:[0-9a-fA-F]:?){12}')
OUI_REGEX = re.compile(r'([0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2})\s+\(hex\)\s+(.+)')


def get_ieee_oui():
    data = requests.get("http://standards-oui.ieee.org/oui/oui.txt").text
    out = {}
    for line in data.splitlines():
        try:
            mac, company = re.search(OUI_REGEX, line).groups()
            out[mac.replace('-', ':').lower()] = company
        except AttributeError:
            continue

    return out


def get_location_from_point(oui_list, point):
    mac = None
    vendor = None
    mac_list = re.findall(MAC_REGEX, point["hotspot_id"])

    if len(mac_list) >= 1:
        mac = mac_list[0]
        oui = mac[:8]
        if oui in oui_list.keys():
            vendor = oui_list[mac[:8]]

    return {"id": point["hotspot_id"], "mac": mac, "lat": point["lat"], "lon": point["lng"], "vendor": vendor}


def get_points(oui_list, lowleftlat, lowleftlon, toprightlat, toprightlon):
    content = requests.get(API_PATH.format(toprightlat=toprightlat, toprightlon=toprightlon,
                                           lowleftlat=lowleftlat, lowleftlon=lowleftlon)).json()
    time.sleep(0.1)

    locations = []
    recurse = False

    if "points" not in content or content["points"] is None:
        return locations

    for point in content["points"]:
        points = [point]

        # Nested points. Happens if the point has multiple locations.
        if "points" in point:
            points = point["points"]

        for p in points:
            if "hotspot_id" in p:
                locations.append(get_location_from_point(oui_list, p))
            else:
                # Many locations at this point. Need to recurse.
                recurse = True

    if recurse:
        lat_delta = float(toprightlat) - float(lowleftlat)
        lon_delta = float(toprightlon) - float(lowleftlon)

        lat_per_box = lat_delta * 0.5
        lon_per_box = lon_delta * 0.5

        if lat_per_box < 0.0001 or lon_per_box < 0.0001:
            return locations

        for x in range(0, 2):
            for y in range(0, 2):
                locations += get_points(oui_list,
                                        lowleftlat + lat_per_box * y,
                                        lowleftlon + lon_per_box * x,
                                        lowleftlat + lat_per_box * (y + 1),
                                        lowleftlon + lon_per_box * (x + 1))

    # Deduplicate on return
    return [dict(y) for y in set(tuple(x.items()) for x in locations)]


if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Usage: {} OUT_FILE LOWLEFTLAT LOWLEFTLON TOPRIGHTLAT TOPRIGHTLON".format(sys.argv[0]))
        sys.exit(1)

    out_filename = sys.argv[1]
    with open(out_filename, "w") as file:
        oui_list = get_ieee_oui()
        points = get_points(oui_list, float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))

        file.write(json.dumps(points, indent=4, sort_keys=True))
        file.close()
