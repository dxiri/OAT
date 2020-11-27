#!/usr/bin/env python

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from urllib.parse import urljoin

import requests
import pdb
import pprint

from akamai.edgegrid import EdgeGridAuth, EdgeRc

parser = argparse.ArgumentParser(description='Interact with the AnswerX OPEN API to view or insert table data')
parser.add_argument('-t', '--table', help='Table to target, displays the table schema if dump is not provided', required=True)
parser.add_argument('-d', '--dump', help='Dump/Display the contents of the table', action='store_true')
parser.add_argument('-r', '--remove', help='Remove a domain from a table', type=str)
parser.add_argument('-D', '--debug', help='Enable Pragma headers for troubleshooting', action='store_true')
parser.add_argument('-i', '--insert', help='Toggle insert mode, if this is set, you need to specify what do you want to insert into the table', type=str)
parser.add_argument('-j', '--json', help='Insert custom JSON data from a file. You need to specify what do you want to insert into the table', type=str)
parser.add_argument('-k', '--key', help='If using custom JSON data from a file, you must specify a key, this is usually the domain name or subscriber', type=str)
parser.add_argument('-x', '--expiry', help='If insert mode is true, set the expiry time for the realtime table entry (TTL), default is 60 seconds', type=int)
parser.add_argument('-S', '--subscriber', help='Check subscriberID belongs to a table', type=str)
parser.add_argument('-C', '--cidr', help='Check CIDR belongs to a table', type=str)
parser.add_argument('-s', '--static', help='Tells the API to query a static table and not a real-time table', action='store_true')
parser.add_argument('-e', '--environment', help='Set target environment, this is a number related to the .edgerc section that contains the credentials where you want to run the script, if not specified, then the default section is used', type=int)
args = vars(parser.parse_args())

pp = pprint.PrettyPrinter(indent=4, width=80, compact=False)
edgerc_path = os.getenv("HOME")+'/'+'.edgerc'
edgerc = EdgeRc(edgerc_path)

if args['environment']:
    service_instance_id = args['environment']
    section = 'r_' + str(service_instance_id)
else:
    service_instance_id = '3'
    section = 'default'

baseurl = 'https://%s' % edgerc.get(section, 'host')

print("RUNNING ON service_instance_id = " + str(service_instance_id) + ' using ' + str(section) + ' section from ' + os.path.abspath(".edgerc"))

s = requests.Session()
s.auth = EdgeGridAuth.from_edgerc(edgerc, section)
s.headers = {'Accept': 'application/json'}
if args['debug']:
    s.headers.update({'Pragma': 'akamai-x-get-cache-key, akamai-x-cache-on, akamai-x-cache-remote-on, akamai-x-get-true-cache-key, akamai-x-check-cacheable, akamai-x-get-request-id, akamai-x-serial-no, akamai-x-get-ssl-client-session-id, edgegrid-fingerprints-on'})
    print(args)


def showTable(tablename):
    # result = s.get(urljoin(baseurl, '/recursive-dns-db/v1/service-instances/9/tables/r_9_IPToSubscriberTable'))
    if args['static']:
        table_type = 'table_type=static'
    else:
        table_type = 'table_type=rtt'

    if args['dump']:
        data_format = "txt"
        table_url = urljoin(baseurl, '/recursive-dns-db/v1/service-instances/' + str(
            service_instance_id) + '/tables/' + tablename + '?action=dump&' + table_type)
    else:
        data_format = "json"
        table_url = urljoin(baseurl, '/recursive-dns-db/v1/service-instances/'+str(service_instance_id)+'/tables/' + tablename + '?'+'action=schema'+'&'+table_type)

    table_data = s.get(table_url, stream=True)
    headers = dict(table_data.headers)
    for key, value in headers.items():
        pp.pprint("{}: {}".format(key, value))
    # pp.pprint(headers.items())
    print('GOT HTTP CODE: ' + str(table_data.status_code) + '\n' + table_url + '\n')
    if data_format == "json":
        table_rows = json.dumps(table_data.json(), indent=2)
    else:
        table_rows = table_data.text
    return table_rows


def showSub(tablename):
    key = args['subscriber']

    table_url = urljoin(baseurl,
                        '/recursive-dns-db/v1/service-instances/' + str(service_instance_id) + '/tables/' + tablename)
    subscriber_url = urljoin(table_url, '?key=%22' + key + '%22')

    subscriber = s.get(subscriber_url)
    print('GOT HTTP CODE: ' + str(subscriber.status_code) + '\n' + subscriber_url + '\n')
    return subscriber.text


def encodeCIDR(cidr):

    noslash_cidr = urllib.parse.quote(cidr, safe='')
    encoded_cidr = str(noslash_cidr).replace(".", "%2E")

    return encoded_cidr


def showCIDR(tablename):
    key = args['cidr']
    key = encodeCIDR(key)

    table_url = urljoin(baseurl,
                        '/recursive-dns-db/v1/service-instances/' + str(service_instance_id) + '/tables/' + tablename)
    cidr_url = urljoin(table_url, '?key=' + key)

    cidr = s.get(cidr_url)
    print('GOT HTTP CODE: ' + str(cidr.status_code) + '\n' + cidr_url + '\n')
    #pp.pprint(cidr.content)
    return cidr.text


def insertDomain(tablename):

    s.headers = {'Accept': 'application/json'}

    key = args['insert']

    if args['expiry']:
        expiry = args['expiry']
    else:
        expiry = 315360000

    data = {"Expiry": expiry, "Field": [{"Name": key, "Type": "STRING"}]}
    jsondata = json.dumps(data, sort_keys=True, indent=2)

    table_url = urljoin(baseurl, '/recursive-dns-db/v1/service-instances/' + str(service_instance_id) + '/tables/' + tablename)
    post_url = urljoin(table_url, '?key=%22' + key + '%22')

    print(jsondata)
    table_post = s.post(post_url, data=jsondata)
    print('GOT HTTP CODE: ' + str(table_post.status_code) + '\n' + post_url + '\n')
    #print(table_post.text)
    return table_post.text


def removeDomain(tablename):

    key = args['remove']

    table_url = urljoin(baseurl, '/recursive-dns-db/v1/service-instances/' + str(service_instance_id) + '/tables/' + tablename)
    delete_url = urljoin(table_url, '?key=%22' + key + '%22')

    domain_delete = s.delete(delete_url)
    print('GOT HTTP CODE: ' + str(domain_delete.status_code) + '\n' + delete_url + '\n')
    #print(domain_delete.content)
    return domain_delete.text


def insertjson(json_file, tablename, key):

    key = args['key']
    s.headers = {'Accept': 'application/json'}
    # Give an arbitrary piece of json data on a file and insert it on a table, useful for custom schemas not covered
    # on the other methods
    # key = args['json']
    table_url = urljoin(baseurl, '/recursive-dns-db/v1/service-instances/' + str(service_instance_id) + '/tables/' + tablename)
    with open(json_file) as file:
        json_data = json.load(file)
    print(json.dumps(json_data, indent=2))
    # Get the key from the arguments, which is the first field
    # key = (json_data["Columns"][0]["Value"])
    key_url = urljoin(table_url, '?key=%22' + key + '%22')
    json_data_post = s.post(key_url, json=json_data)
    print('GOT HTTP CODE: ' + str(json_data_post.status_code) + '\n' + key_url + '\n')
    return json_data_post.content


if __name__ == '__main__':
    if args['insert']:
        print("Inserting domain " + args['insert'] + " into " + args['table'])
        print(insertDomain(args['table']))
    if args['json']:
        if not args['key']:
            print("You must provide a key value to insert JSON data, this is usually the domain or subscriber ID")
            sys.exit()
        print("JSON Data file provided, inserting into table " + args['table'])
        print(insertjson(args['json'], args['table'], args['key']))
    if args['remove']:
        print("Removing domain " + args['remove'] + " from " + args['table'])
        print(removeDomain(args['table']))
    if args['subscriber']:
        print(showSub(args['table']))
    if args['cidr']:
        print(showCIDR(args['table']))
    else:
        print(showTable(args['table']))