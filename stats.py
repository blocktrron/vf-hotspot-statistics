#!/usr/bin/env python3
import json
import sys


def convert(input_list):
    vendor_map = {}

    for element in input_list:
        vendor = element["vendor"]
        if vendor not in vendor_map:
            vendor_map[vendor] = 0

        vendor_map[vendor] += 1

    return vendor_map


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {} INPUT_FILE".format(sys.argv[0]))
        sys.exit(1)

    with open(sys.argv[1], "r") as input_file:
        input_list = json.load(input_file)
        stats = convert(input_list)

        for k in sorted(stats, key=stats.get, reverse=True):
            print("{} - {}".format(stats[k], k))

        input_file.close()
