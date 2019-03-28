#!/usr/bin/env python

import requests
import json
import urllib
import xml.dom.minidom
import sys
import os
import argparse
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urlparse import urljoin

edgerc_path = os.getenv("HOME")+'/'+'.edgerc'
edgerc = EdgeRc(edgerc_path)

parser = argparse.ArgumentParser(description='Interact with the AnswerX OPEN API to view or insert table data')
parser.add_argument('-t', '--table', help='Table to target, displays the table schema if dump is not provided', required=True)
parser.add_argument('-d', '--dump', help='Dump/Display the contents of the table', action='store_true')
parser.add_argument('-r', '--remove', help='Remove a domain from a table', type=str)
parser.add_argument('-D', '--debug', help='Enable Pragma headers for troubleshooting', action='store_true')
parser.add_argument('-i', '--insert', help='Toggle insert mode, if this is set, you need to specify what do you want to insert into the table', type=str)
parser.add_argument('-x', '--expiry', help='If insert mode is true, set the expiry time for the realtime table entry (TTL), default is 60 seconds', type=int)
parser.add_argument('-S', '--subscriber', help='Check subscriberID belongs to a table', type=str)
parser.add_argument('-C', '--cidr', help='Check CIDR belongs to a table', type=str)
parser.add_argument('-s', '--static', help='Tells the API to query a static table and not a real-time table', action='store_true')
parser.add_argument('-e', '--environment', help='Set target environment, this is a number related to the .edgerc section that contains the credentials where you want to run the script, if not specified, then the default section is used', type=int)
args = vars(parser.parse_args())
print args

if args['environment']:
    service_instance_id = args['environment']
    section = 'r_'+ str(service_instance_id)
else:
    service_instance_id = '3'
    section = 'default'

baseurl = 'https://%s' % edgerc.get(section, 'host')

print "RUNNING ON service_instance_id = " + str(service_instance_id) + ' using ' + str(section) + ' section from ' + os.path.abspath(".edgerc")

s = requests.Session()
s.auth = EdgeGridAuth.from_edgerc(edgerc, section)
s.headers = {'Accept': 'application/xml'}
if args['debug'] == True:
    s.headers.update({'Pragma': 'akamai-x-get-cache-key, akamai-x-cache-on, akamai-x-cache-remote-on, akamai-x-get-true-cache-key, akamai-x-check-cacheable, akamai-x-get-request-id, akamai-x-serial-no, akamai-x-get-ssl-client-session-id, edgegrid-fingerprints-on'})

def showTable(tablename):
    # result = s.get(urljoin(baseurl, '/recursive-dns-db/v1/service-instances/9/tables/r_9_IPToSubscriberTable'))
    if args['static'] == True:
        table_type = 'table_type=static'
    else:
        table_type = 'table_type=rtt'

    if args['dump'] == True:
        table_url = urljoin(baseurl, '/recursive-dns-db/v1/service-instances/' + str(
            service_instance_id) + '/tables/' + tablename + '?action=dump&' + table_type)
    else:
        table_url = urljoin(baseurl, '/recursive-dns-db/v1/service-instances/'+str(service_instance_id)+'/tables/'+tablename+'?'+'action=schema'+'&'+table_type)

    table_data = s.get(table_url, stream=True)
    print table_data.headers
    print 'GOT HTTP CODE: ' + str(table_data.status_code) + '\n' + table_url + '\n'

    try:
        global xml
        xml = xml.dom.minidom.parseString(table_data.content)
        return xml.toprettyxml()
    except xml.parsers.expat.ExpatError as e:
        return table_data.content

def showSub(tablename):
    key = args['subscriber']

    table_url = urljoin(baseurl,
                        '/recursive-dns-db/v1/service-instances/' + str(service_instance_id) + '/tables/' + tablename)
    subscriber_url = urljoin(table_url, '?key=%22' + key + '%22')

    subscriber = s.get(subscriber_url)
    print 'GOT HTTP CODE: ' + str(subscriber.status_code) + '\n' + subscriber_url + '\n'
    print subscriber.content
    return subscriber

def encodeCIDR(cidr):

    noslash_cidr = urllib.quote(cidr, safe='')
    encoded_cidr = str(noslash_cidr).replace(".","%2E")

    return encoded_cidr

def showCIDR(tablename):
    key = args['cidr']
    key = encodeCIDR(key)

    table_url = urljoin(baseurl,
                        '/recursive-dns-db/v1/service-instances/' + str(service_instance_id) + '/tables/' + tablename)
    cidr_url = urljoin(table_url, '?key=' + key)

    cidr = s.get(cidr_url)
    print 'GOT HTTP CODE: ' + str(cidr.status_code) + '\n' + cidr_url + '\n'

    try:
        global xml
        xml = xml.dom.minidom.parseString(cidr.content)
        return xml.toprettyxml()
    except xml.parsers.expat.ExpatError as e:
        return cidr

def insertDomain(tablename):

    s.headers = {'Accept': 'application/json'}

    key = args['insert']

    if args['expiry']:
        expiry = args['expiry']
    else:
        expiry = 315360000

    data = {"Expiry": expiry, }
    data["Field"] = [{"Name": key, "Type": "STRING"}]
    jsondata = json.dumps(data, sort_keys=True, indent=2)

    table_url = urljoin(baseurl,'/recursive-dns-db/v1/service-instances/' + str(service_instance_id) + '/tables/' + tablename)
    post_url = urljoin(table_url,'?key=%22'+ key +'%22')

    print jsondata
    table_post = s.post(post_url,data=jsondata)
    print 'GOT HTTP CODE: ' + str(table_post.status_code) + '\n' + post_url + '\n'
    print table_post.content
    return table_post

def removeDomain(tablename):

    key = args['remove']

    table_url = urljoin(baseurl,'/recursive-dns-db/v1/service-instances/' + str(service_instance_id) + '/tables/' + tablename)
    delete_url = urljoin(table_url,'?key=%22'+ key +'%22')


    domain_delete = s.delete(delete_url)
    print 'GOT HTTP CODE: ' + str(domain_delete.status_code) + '\n' + delete_url + '\n'
    print domain_delete.content
    return domain_delete

if __name__ == '__main__':
    if args['insert']:
        print "Inserting domain" + args['insert'] + "into " + args['table']
        print insertDomain(args['table'])
    if args['remove']:
        print "Removing domain " + args['remove'] + "from " + args['table']
        print removeDomain(args['table'])
    if args['subscriber']:
        print showSub(args['table'])
    if args['cidr']:
        print showCIDR(args['table'])
    else:
        print showTable(args['table'])