#!/usr/bin/env python3

import bson
import click
import pymongo
import random
import sys

from misc.db.python.Open5GS import Open5GS


def add_user(imsi, key="FEC86BA6EB707ED08905757B1BB44B8F", op=None,
             opc="C42449363BBAD02B66D16BC975D77CC1", amf="8000", 
             apn="lance", qci="5", ip_alloc="", sst=1, sd="000001"):
    '''Add UE data to Open5GS mongodb'''

    if op is not None:
        opc = None

    slice_data = [
        {
            "sst": int(sst),
            "sd": sd,
            "default_indicator": True,
            "session": [
                {
                    "name": apn,
                    "type": 3, 
                    "pcc_rule": [], 
                    "ambr": {"uplink": {"value": 1, "unit": 3}, 
                            "downlink": {"value": 1, "unit": 3}},
                    "qos": {
                        "index": int(qci),
                        "arp": {"priority_level": 1, 
                               "pre_emption_capability": 1, 
                               "pre_emption_vulnerability": 1}
                    },
                    "ue": {
                        "ipv4": ip_alloc
                    }
                },
            ]
        }
    ]

    sub_data = {
        "imsi": imsi,
        "subscribed_rau_tau_timer": 12,
        "network_access_mode": 2,
        "subscriber_status": 0,
        "access_restriction_data": 32,
        "slice": slice_data,
        "ambr": {"uplink": {"value": 1, "unit": 3}, 
                "downlink": {"value": 1, "unit": 3}},
        "security": {
            "k": key,
            "amf": amf,
            "op": op,
            "opc": opc
        },
        "schema_version": 1,
        "__v": 0
    }

    return sub_data


def read_from_db(db_file):
    '''Read UE data from a subscriber db csv-file.'''
    subscriber_db = []
    try:
        with open(db_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                # Split the line and handle optional fields
                parts = line.split(',')
                if len(parts) < 8:
                    print(f"Error: Line doesn't have enough fields: {line}")
                    continue
                    
                # Extract required fields
                name = parts[0]
                imsi = parts[1]
                key = parts[2]
                op_type = parts[3]
                op_c = parts[4]
                amf = parts[5]
                qci = parts[6]
                ip_alloc = parts[7]
                
                # Extract optional fields with defaults
                apn = parts[8] if len(parts) > 8 else "internet"
                sst = parts[9] if len(parts) > 9 else "1"
                sd = parts[10] if len(parts) > 10 else "000001"
                
                opc = op_c
                op = None
                if op_type == "op":
                    op = op_c
                    opc = None

                subscriber_db.append({
                    "imsi": imsi, 
                    "key": key, 
                    "op": op,
                    "opc": opc, 
                    "amf": amf, 
                    "qci": qci, 
                    "ip_alloc": ip_alloc,
                    "apn": apn,
                    "sst": sst,
                    "sd": sd
                })
                
    except Exception as e:
        print(f"Error reading subscriber_db.csv: {e}")
        return None

    return subscriber_db


def read_from_string(sub_data):
    '''
    Read UE data from subscriber data string.
    Example string: "001010123456780,FEC86BA6EB707ED08905757B1BB44B8F,opc,C42449363BBAD02B66D16BC975D77CC1,8000,9,10.45.1.2,lance,1,000001"
    '''
    subscriber_db = []

    try:
        parts = sub_data.split(',')
        if len(parts) < 8:
            print(f"Error: String doesn't have enough fields: {sub_data}")
            return None
            
        imsi = parts[0]
        key = parts[1]
        op_type = parts[2]
        op_c = parts[3]
        amf = parts[4]
        qci = parts[5]
        ip_alloc = parts[6]
        
        # Optional fields with defaults
        apn = parts[7] if len(parts) > 7 else "lance"
        sst = parts[8] if len(parts) > 8 else "1"
        sd = parts[9] if len(parts) > 9 else "000001"

        opc = op_c
        op = None
        if op_type == "op":
            op = op_c
            opc = None

        subscriber_db.append({
            "imsi": imsi, 
            "key": key, 
            "op": op,
            "opc": opc, 
            "amf": amf, 
            "qci": qci, 
            "ip_alloc": ip_alloc,
            "apn": apn,
            "sst": sst,
            "sd": sd
        })

    except Exception as e:
        print(f"Error reading subscriber string: {e}")
        return None

    return subscriber_db


@click.command()
@click.option("--mongodb", default="127.0.0.1", help="IP address or hostname of the mongodb instance.")
@click.option("--mongodb_port", default=27017, help="Port to connect to the mongodb instance.")
@click.option("--subscriber_data", default="001010123456780,FEC86BA6EB707ED08905757B1BB44B8F,opc,C42449363BBAD02B66D16BC975D77CC1,8000,9,10.45.1.2,internet,1,000001", help="Single subscriber data string or full path to subscriber data csv-file.")
def main(mongodb, mongodb_port, subscriber_data):
    open5gs_client = Open5GS(mongodb, mongodb_port)

    if subscriber_data.endswith(".csv"):
        print("Reading subscriber data from csv-file.")
        subscriber_db = read_from_db(subscriber_data)
    else:
        print("Reading subscriber data from cmd.")
        subscriber_db = read_from_string(subscriber_data)

    if not subscriber_db:
        return sys.exit(1)

    for ue in subscriber_db:
        try:
            sub_data = add_user(**ue)
            print(open5gs_client.AddSubscriber(sub_data))
        except pymongo.errors.DuplicateKeyError:
            print(f"UE (IMSI={ue['imsi']}) already exists, updating it.")
            sub_data = add_user(**ue)
            print(open5gs_client.UpdateSubscriber(ue['imsi'], sub_data))


if __name__ == "__main__":
    main()
