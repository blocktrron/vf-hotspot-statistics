#!/usr/bin/env python3
import sys
import json
import geojson


def convert(input_list):
    features = []

    for location in input_list:
        features.append(geojson.Feature(geometry=geojson.Point((location["lon"], location["lat"])),
                                        properties={"mac": location["mac"], "vendor": location["vendor"],
                                                    "id": location["id"]}))

    feature_collection = geojson.FeatureCollection(features)
    return geojson.dumps(feature_collection, sort_keys=True)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: {} INPUT_FILE OUTPUT_FILE".format(sys.argv[0]))
        sys.exit(1)

    with open(sys.argv[1], "r") as input_file:
        with open(sys.argv[2], "w") as output_file:
            input_list = json.load(input_file)
            output_file.write(convert(input_list))
            output_file.close()
        input_file.close()
