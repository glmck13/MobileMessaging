#!/usr/bin/env python3

import sys, os
import requests
from urllib.parse import parse_qs
from getenv import *

QUERY_STRING = os.getenv("QUERY_STRING", "")
if not QUERY_STRING and os.getenv("REQUEST_METHOD", "") != "GET":
    QUERY_STRING = sys.stdin.read().strip()

Fields = parse_qs(QUERY_STRING)
Token = Fields.get("token", [""])[0]
Contacts = Fields.get("contacts", [""])[0]
Text = Fields.get("text", [""])[0]

print("Content-Type: text/plain\n")

if Token not in TOKEN_ALLOW:
    exit()

headers = {"Content-Type" : "application/vnd.api+json"}

if MSGAPP_BACKEND == "SXMO":
    tmpfile = "sms{}.txt".format(os.getpid())
    with open("{}/{}".format(MSGAPP_MYCDN, tmpfile), "w") as f:
        f.write(Text)
    msg = {
        "data": {
            "type": "message",
            "attributes": {
                "from": MSGAPP_DID,
                "body": None,
                "is_mms": False,
                "media_urls": ["{}/{}".format(MSGAPP_MYURL, tmpfile)]
            }
        }
    }
    phone_list = []
    for phone in Contacts.split(','):
        if phone[0:2] != '+1':
            phone = '+1' + phone
        phone_list.append(phone)
    msg["data"]["attributes"]["to"] = phone_list
    rsp = requests.post(MSGAPP_SENDAPI, auth=(MSGAPP_KEY, MSGAPP_SECRET), headers=headers, json=msg)
    print(rsp.text)
    os.remove("{}/{}".format(MSGAPP_MYCDN, tmpfile))

else:
    msg = {
        "data": {
            "type": "message",
            "attributes": {
                "from": MSGAPP_DID,
                "body": Text,
            }
        }
    }

    for phone in Contacts.split(','):
        if phone[0:2] != '+1':
            phone = '+1' + phone
        msg["data"]["attributes"]["to"] = phone
        rsp = requests.post(MSGAPP_SENDAPI, auth=(MSGAPP_KEY, MSGAPP_SECRET), headers=headers, json=msg)
        print(rsp.text)
