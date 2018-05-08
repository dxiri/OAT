import requests
import xml.dom.minidom
import sys
import argparse
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urlparse import urljoin

edgerc = EdgeRc('.edgerc')
section = 'default'
#section = 'r_3'
baseurl = 'https://%s' % edgerc.get(section, 'host')

parser = argparse.ArgumentParser(description='Interact with the AnswerX OPEN API to view or insert table data')
parser.add_argument('-t', '--table', help='Table to target, displays the table schema', required=True)
parser.add_argument('-d', '--dump', help='Dump/Display the contents of the table', action='store_true')
parser.add_argument('-r', '--remove', help='Remove a domain from a table', type=str)
#parser.add_argument('-D', '--data', help='Data to insert into the table', type=str)
parser.add_argument('-i', '--insert', help='Toggles insert mode, if this is set, you need to specify what do you want to insert into the table', type=str)
parser.add_argument('-s', '--static', help='Tells the API to query a static table and not a real-time table', action='store_true')
parser.add_argument('-p', '--production', help='Production flag, set to target the production environment, if not present, script will target the staging environment', action='store_true')
args = vars(parser.parse_args())
print args

if args['production'] == True:
        service_instance_id = 10
        print "RUNNING ON PROD service_instance_id = " + str(service_instance_id)

else:
        service_instance_id = 10
    #    service_instance_id = 3
        print "RUNNING ON STAGING service_instance_id = " + str(service_instance_id)


s = requests.Session()
s.auth = EdgeGridAuth.from_edgerc(edgerc, section)
s.headers = {'Accept': 'application/xml'}

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
        table_url = urljoin(baseurl, '/recursive-dns-db/v1/service-instances/'+str(service_instance_id)+'/tables/'+tablename+'?'+table_type)

    table_data = s.get(table_url)
    print 'GOT HTTP CODE: ' + str(table_data.status_code) + '\n' + table_url + '\n'
    try:
        global xml
        xml = xml.dom.minidom.parseString(table_data.content)
        return xml.toprettyxml()
    except xml.parsers.expat.ExpatError as e:
        return table_data.content


def insertDomain(tablename):

    s.headers = {'Accept': 'application/json'}

    data = """
    {
  "Expiry": 60,
  "Columns": []
}
    """

    key = args['insert']

    table_url = urljoin(baseurl,'/recursive-dns-db/v1/service-instances/' + str(service_instance_id) + '/tables/' + tablename)
    post_url = urljoin(table_url,'?key=%22'+ key +'%22')


    table_post = s.post(post_url,data=data)
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

if args['insert']:
    print "Inserting domain" + args['insert'] + "into " + args['table']
    print insertDomain(args['table'])
if args['remove']:
    print "Removing domain " + args['remove'] + "from " + args['table']
    print removeDomain(args['table'])
else:
    print showTable(args['table'])
