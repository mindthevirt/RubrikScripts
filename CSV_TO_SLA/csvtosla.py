# Author: Jan Schwoebel
# Twitter: @mindtehvirt
# Github: https://github.com/mindthevirt

import json
import requests
import base64
import sys
import getpass
import argparse
import datetime
import csv
import urllib3

# Supress HTTPS cert warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# These two functions are used to encode/decode the username and password
def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))

def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')

def base(**kwargs):
    clusterip = raw_input("Rubrik Cluster IP/DNS: ")
    username = raw_input("Rubrik User: ")
    password = getpass.getpass('Rubrik Password: ')
    authheader = verify_credentials(username, password, clusterip)
    csvpath = kwargs.get('slafile')
    slas = read_csv(csvpath)
    create_sla_data(slas, authheader, clusterip)

def read_csv(csvpath):
    # Read CSV into List
    slas = []
    with open(csvpath) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                slas.append(row)
    return slas

def verify_credentials(username, password, clusterip):
    # Authentication with Rubrik Cluster
    creds = '%s:%s' % (username, password)
    credentials = stringToBase64(creds)
    headers = {'Content-Type': 'application/json','Authorization': 'Basic '+credentials}
    r = requests.request("GET", 'https://'+clusterip+'/api/v1/cluster/me', headers=headers, verify=False)
    if r.status_code != 200:
        print "Authentication failed. Please check credentials."
        sys.exit(1)
    return headers

def create_sla_data(slas, authheader, clusterip):
    # Reads CSV file and creats JSON data for SLAs
    for sla in slas:
        try:
            sla_data = '{"name":"%s","frequencies":[' % sla.get('\xef\xbb\xbfSLA_NAME')
            if sla.get('EVERY_X_YEARS'):
                yearlyfrequency = sla.get('EVERY_X_YEARS')
                yearlyretention = sla.get('KEEP_YEARLY_FOR_X_YEARS')
                sla_data = sla_data + '{"timeUnit":"Yearly","frequency":%s,"retention":%s},' % (yearlyfrequency, yearlyretention)
            if sla.get('EVERY_X_MONTHS'):
                monthlyfrequency = sla.get('EVERY_X_MONTHS')
                monthlyretentioninyears = sla.get('KEEP_MONTHLY_FOR_X_YEARS')
                monthlyretention = (int(monthlyretentioninyears)*12)
                sla_data = sla_data + '{"timeUnit":"Monthly","frequency":%s,"retention":%s},' % (monthlyfrequency, monthlyretention)
            if sla.get('EVERY_X_DAYS'):
                dailyfrequency = sla.get('EVERY_X_DAYS')
                dailyretention = sla.get('KEEP_DAILY_FOR_X_DAYS')
                sla_data = sla_data + '{"timeUnit":"Daily","frequency":%s,"retention":%s},' % (dailyfrequency, dailyretention)
            if sla.get('EVERY_X_HOURS'):
                hourlyfrequency = sla.get('EVERY_X_HOURS')
                hourlyretentionindays = sla.get('KEEP_HOURLY_FOR_X_DAYS')
                hourlyretention = (int(hourlyretentionindays)*24)
                sla_data = sla_data + '{"timeUnit": "Hourly","frequency":%s,"retention":%s}' % (hourlyfrequency, hourlyretention)
            sla_data = sla_data + '],"allowedBackupWindows":[],"firstFullAllowedBackupWindows":[],'
            if not sla.get('ARCHIVE_LOCATION') and not sla.get('REPLICATION_TARGET'):
                sla_data = sla_data + '"archivalSpecs":[],"replicationSpecs":[]}'
            if sla.get('ARCHIVE_LOCATION'):
                archive_name = sla.get('ARCHIVE_LOCATION')
                archive_days = sla.get('ARCHIVE_AFTER_X_DAYS')
                archive_days_seconds = (int(archive_days)*24*60*60)
                archiveid = get_archival_id(authheader, clusterip, archive_name)
                sla_data = sla_data + '"localRetentionLimit":%s,"archivalSpecs":[{"locationId":"%s","archivalThreshold":%s}],' % (archive_days_seconds, archiveid, archive_days_seconds)
            else:
                sla_data = sla_data + '"archivalSpecs":[],'
            if sla.get('REPLICATION_TARGET'):
                replication_target = sla.get('REPLICATION_TARGET')
                replication_days = sla.get('REPLICATE_FOR_X_DAYS')
                replication_days_seconds = (int(replication_days)*24*60*60)
                replica_id = get_replication_id(authheader, clusterip, replication_target)
                sla_data = sla_data + '"replicationSpecs": [{"locationId":"%s","retentionLimit":%s}]}' % (replica_id, replication_days_seconds)
            else:
                sla_data = sla_data + '"replicationSpecs":[]}'
            print "Creating SLA %s" % sla.get('\xef\xbb\xbfSLA_NAME')
            create_slas(sla_data, authheader, clusterip)
        except Exception as ex:
            print "Could not create SLA %s due to %s" % (sla.get('\xef\xbb\xbfSLA_NAME'), ex)

def get_archival_id(authheader, clusterip, archive_name):
    # Find archive location UUID
    response = requests.get('https://'+clusterip+'/api/internal/archive/location', headers=authheader, verify=False)
    get_archive = response.json()
    for i in get_archive["data"]:
        if i["name"] == archive_name:
            archiveid = i["id"]
    return archiveid

def get_replication_id(authheader, clusterip, replication_target):
    # Find replication partner UUID
    response = requests.get('https://'+clusterip+'/api/internal/replication/target', headers=authheader, verify=False)
    get_replica = response.json()
    for i in get_replica["data"]:
        if i["targetClusterName"] == replication_target:
            targetid = i["targetClusterUuid"]
    return targetid

def create_slas(sla_data, authheader, clusterip):
    # Creates SLAs on Rubrik Cluster
    try:
        create_sla = requests.post('https://'+clusterip+'/api/v1/sla_domain', headers=authheader, data=sla_data, verify=False)
        if create_sla.status_code != 201:
            print "SLA creation failed. %s" %create_sla.content
    except Exception as ex:
        print "Could not create SLA due to %s" % (ex)
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Insert default reports')
    parser.add_argument('slafile', action='store', help='CSV file with full path')
    parser.set_defaults(func=base)
    args = parser.parse_args()
    args = vars(args)

    args['func'](**args)
