#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2019 Pedro Gabaldón

from datetime import datetime

from colors import *

import sys

import json
import googlemaps

if __name__ == "__main__":
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except IOError:
        sys.exit("Config file not found.")

    gmaps = googlemaps.Client(key=config["api_key"])

    filtered_result = []
    for i in range(len(config["directions"])):
        origin = config["directions"][i]["origin"]
        destination = config["directions"][i]["destination"]
        now = datetime.now()
 
        result = gmaps.directions(origin, destination, alternatives=True, avoid=config["directions"][i]["avoid"], language="es", 
            units="metric", departure_time=now, traffic_model="best_guess")

        filtered_result.append([])
        for j in range(len(result)):
            duration_traffic = result[j]["legs"][0]["duration_in_traffic"]["value"]/60.0
            duration = result[j]["legs"][0]["duration"]["value"]/60.0
            distance = result[j]["legs"][0]["distance"]["value"]/1000.0

            summary = bcolors.OKBLUE + result[j]["summary"] + bcolors.ENDC

            duration_diference = duration_traffic - duration

            if duration_traffic <= duration + 4:
                info_traffic = bcolors.OKGREEN + "Normal" + bcolors.ENDC
                traffic_level = 0            
            elif duration_diference <= 10:
                info_traffic = bcolors.WARNING + "Algo lento" + bcolors.ENDC
                traffic_level = 1
            elif duration_diference <= 15:                
                info_traffic = bcolors.HEADER + "Lento" + bcolors.ENDC
                traffic_level = 2
            else:
                info_traffic = bcolors.FAIL + "Retención" + bcolors.ENDC
                traffic_level = 3

            filtered_result[i].append({})
            filtered_result[i][j]["summary"] = result[j]["summary"]
            filtered_result[i][j]["origin"] = result[j]["legs"][0]["start_address"]
            filtered_result[i][j]["destination"] = result[j]["legs"][0]["end_address"]
            filtered_result[i][j]["distance"] = distance
            filtered_result[i][j]["duration"] = duration
            filtered_result[i][j]["duration_traffic"] = duration_traffic
            filtered_result[i][j]["traffic_level"] = traffic_level
            filtered_result[i][j]["time"] = now.strftime("%H:%M:%S %d-%m-%Y")
            filtered_result[i][j]["original_origin"] = origin
            filtered_result[i][j]["original_destination"] = destination

    with open("last_update.json", "w") as f:
        json.dump(filtered_result, f, indent=4, sort_keys=True)