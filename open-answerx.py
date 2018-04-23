import requests
import xml.dom.minidom
import argparse
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urlparse import urljoin

edgerc = EdgeRc('.edgerc')
section = 'default'
baseurl = 'https://%s' % edgerc.get(section, 'host')

parser = argparse.ArgumentParser(description='Interact with the AnswerX OPEN API to view or insert table data')
parser.add_argument('-t', '--table', help='Table to target, displays the table schema')
parser.add_argument('-d', '--dump', help='Dump/Display the contents of the table', action='store_true')
parser.add_argument('-p', '--production', help='Production flag, set to target the production environment, if not present, script will target the staging environment', action='store_true')
args = vars(parser.parse_args())
print args

if args['production'] == True:
        print "RUNNING ON PROD service_instance_id = 10"
        service_instance_id = 10
else:
        print "RUNNING ON STAGING service_instance_id = 9"
        service_instance_id = 9


s = requests.Session()
s.auth = EdgeGridAuth.from_edgerc(edgerc, section)
s.headers = {'Accept': 'application/xml'}

def showTable(tablename):
    # result = s.get(urljoin(baseurl, '/recursive-dns-db/v1/service-instances/9/tables/r_9_IPToSubscriberTable'))

    if args['dump'] == True:
        table_url = urljoin(baseurl, '/recursive-dns-db/v1/service-instances/' + str(
            service_instance_id) + '/tables/' + tablename + '?action=dump')
    else:
        table_url = urljoin(baseurl, '/recursive-dns-db/v1/service-instances/'+str(service_instance_id)+'/tables/'+tablename)

    table_data = s.get(table_url)
    print 'GOT HTTP CODE: ' + str(table_data.status_code) + '\n' + table_url + '\n'
    try:
        global xml
        xml = xml.dom.minidom.parseString(table_data.content)
        return xml.toprettyxml()
    except xml.parsers.expat.ExpatError as e:
        return table_data.content

print showTable(args['table'])