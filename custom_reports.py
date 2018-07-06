# Author: Jan Schwoebel
# Twitter: @mindtehvirt
# Github: https://github.com/mindthevirt

import json
import requests
import base64
import getpass
import sys
import argparse
import urllib3
from datetime import datetime

# Supress HTTPS cert warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# These two functions are used to encode/decode the username and password
def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))

def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')

def base(**kwargs):
    clusterip = kwargs.get('rubrikip')
    username = raw_input("Rubrik User: ")
    password = getpass.getpass('Rubrik Password: ')
    authheader = verify_credentials(username, password, clusterip)

    failure_report(clusterip, authheader)
    data_reduction(clusterip, authheader)
    average_job_duration(clusterip, authheader)
    system_capacity(clusterip, authheader)
    daily_backup_admin(clusterip, authheader)
    daily_dba(clusterip, authheader)
    print "Reports have been created"


def verify_credentials(username, password, clusterip):
    creds = '%s:%s' % (username, password)
    credentials = stringToBase64(creds)
    headers = {'Authorization': 'Basic '+credentials}
    r = requests.request("GET", 'https://'+clusterip+'/api/v1/cluster/me', headers=headers, verify=False)
    if r.status_code != 200:
        print "Authentication failed. Please check credentials and re-try."
        sys.exit(1)
    return headers


def failure_report(clusterip, authheader):
    print "Failure Report - Last 7 Days"
    create_payload = "{\"name\":\"Failure Report - Last 7 Days\",\"reportTemplate\":\"ProtectionTasksDetails\"}"
    create_report = requests.post('https://'+clusterip+'/api/internal/report', headers=authheader, data=create_payload, verify=False)
    if create_report.status_code != 201:
        print "Report creation failed. %s" %create_report.content
        sys.exit(1)
    returndata = json.loads(create_report.content)
    reportid = returndata['id'].replace(":", "%3A")
    report_payload = "{\"name\":\"Failure Report - Last 7 Days\",\"filters\":{\"dateConfig\":{\"period\":\"PastWeek\"},\"taskStatus\":[\"Failed\"]},\"chart0\":{\"id\":\"chart0\",\"name\":\"Failed Tasks by SLA Domain\",\"chartType\":\"Donut\",\"attribute\":\"SlaDomain\",\"measure\":\"FailedTaskCount\"},\"chart1\":{\"id\":\"chart1\",\"name\":\"Failed Tasks by Object Name\",\"chartType\":\"VerticalBar\",\"attribute\":\"ObjectName\",\"measure\":\"FailedTaskCount\"},\"table\":{\"columns\":[\"TaskStatus\",\"TaskType\",\"ObjectName\",\"ObjectType\",\"Location\",\"SlaDomain\",\"StartTime\",\"EndTime\",\"Duration\"]}}"
    update_report = requests.patch('https://'+clusterip+'/api/internal/report/'+reportid, headers=authheader, data=report_payload, verify=False)
    if update_report.status_code != 200:
        print "Report could not be updated. %s" %update_report.content


def data_reduction(clusterip, authheader):
    print "Data Reduction Summary - Last 30 Days"
    create_payload = "{\"name\":\"Data Reduction Summary - Last 30 Days\",\"reportTemplate\":\"ProtectionTasksSummary\"}"
    create_report = requests.post('https://'+clusterip+'/api/internal/report', headers=authheader, data=create_payload, verify=False)
    if create_report.status_code != 201:
        print "Report creation failed. %s" %create_report.content
        sys.exit(1)
    returndata = json.loads(create_report.content)
    reportid = returndata['id'].replace(":", "%3A")
    report_payload = "{\"name\":\"Data Reduction Summary - Last 30 Days\",\"filters\":{\"dateConfig\":{\"period\":\"Past30Days\"}},\"chart0\":{\"id\":\"chart0\",\"name\":\"Data Reduction by Object Type\",\"chartType\":\"HorizontalBar\",\"attribute\":\"ObjectType\",\"measure\":\"LogicalDataReductionPercent\"},\"chart1\":{\"id\":\"chart1\",\"name\":\"Data Reduction by SLA Domain\",\"chartType\":\"VerticalBar\",\"attribute\":\"SlaDomain\",\"measure\":\"LogicalDataReductionPercent\"},\"table\":{\"columns\":[\"Day\",\"TaskType\",\"ObjectType\",\"SlaDomain\",\"DedupRatio\",\"LogicalDataReductionPercent\",\"DataReductionPercent\",\"LogicalDedupRatio\",\"SuccessfulTaskCount\",\"CanceledTaskCount\",\"FailedTaskCount\",\"AverageDuration\",\"DataTransferred\",\"DataStored\"]}}"
    update_report = requests.patch('https://'+clusterip+'/api/internal/report/'+reportid, headers=authheader, data=report_payload, verify=False)
    if update_report.status_code != 200:
        print "Report could not be updated. %s" %update_report.content


def average_job_duration(clusterip, authheader):
    print "Average Job Durations - Last 7 Days"
    create_payload = "{\"name\":\"Average Job Durations - Last 7 Days\",\"reportTemplate\":\"ProtectionTasksDetails\"}"
    create_report = requests.post('https://'+clusterip+'/api/internal/report', headers=authheader, data=create_payload, verify=False)
    if create_report.status_code != 201:
        print "Report creation failed. %s" %create_report.content
        sys.exit(1)
    returndata = json.loads(create_report.content)
    reportid = returndata['id'].replace(":", "%3A")
    report_payload = "{\"name\":\"Average Job Durations - Last 7 Days\",\"filters\":{\"dateConfig\":{\"period\":\"PastWeek\"},\"taskStatus\":[\"Succeeded\"]},\"chart0\":{\"id\":\"chart0\",\"name\":\"Average Duration by Object Type\",\"chartType\":\"VerticalBar\",\"attribute\":\"ObjectType\",\"measure\":\"AverageDuration\"},\"chart1\":{\"id\":\"chart1\",\"name\":\"Daily Tasks by Object Type\",\"chartType\":\"HorizontalBar\",\"attribute\":\"ObjectType\",\"measure\":\"TaskCount\"},\"table\":{\"columns\":[\"TaskStatus\",\"TaskType\",\"ObjectName\",\"ObjectType\",\"Location\",\"SlaDomain\",\"StartTime\",\"EndTime\",\"Duration\",\"DataTransferred\",\"DataStored\"]}}"
    update_report = requests.patch('https://'+clusterip+'/api/internal/report/'+reportid, headers=authheader, data=report_payload, verify=False)
    if update_report.status_code != 200:
        print "Report could not be updated. %s" %update_report.content


def system_capacity(clusterip, authheader):
    print "System Capacity by Object Type - Last 30 Days"
    create_payload = "{\"name\":\"System Capacity by Object Type - Last 30 Days\",\"reportTemplate\":\"ProtectionTasksSummary\"}"
    create_report = requests.post('https://'+clusterip+'/api/internal/report', headers=authheader, data=create_payload, verify=False)
    if create_report.status_code != 201:
        print "Report creation failed. %s" %create_report.content
        sys.exit(1)
    returndata = json.loads(create_report.content)
    reportid = returndata['id'].replace(":", "%3A")
    report_payload = "{\"name\":\"System Capacity by Object Type - Last 30 Days\",\"filters\":{\"dateConfig\":{\"period\":\"Past30Days\"}},\"chart0\":{\"id\":\"chart0\",\"name\":\"Total Data Stored by Object Type\",\"chartType\":\"Donut\",\"attribute\":\"ObjectType\",\"measure\":\"DataStored\"},\"chart1\":{\"id\":\"chart1\",\"name\":\"Data Transferred vs Stored by Object Type\",\"chartType\":\"StackedHorizontalBar\",\"attribute\":\"ObjectType\",\"measure\":\"StackedTotalData\"},\"table\":{\"columns\":[\"Day\",\"SlaDomain\",\"TaskType\",\"ObjectType\",\"Location\",\"SuccessfulTaskCount\",\"CanceledTaskCount\",\"FailedTaskCount\",\"DataTransferred\",\"DataStored\",\"LogicalDataProtected\"]}}"
    update_report = requests.patch('https://'+clusterip+'/api/internal/report/'+reportid, headers=authheader, data=report_payload, verify=False)
    if update_report.status_code != 200:
        print "Report could not be updated. %s" %update_report.content


def daily_backup_admin(clusterip, authheader):
    print "Daily Backup Administrator Report"
    create_payload = "{\"name\":\"Daily Backup Administrator Report\",\"reportTemplate\":\"ProtectionTasksDetails\"}"
    create_report = requests.post('https://'+clusterip+'/api/internal/report', headers=authheader, data=create_payload, verify=False)
    if create_report.status_code != 201:
        print "Report creation failed. %s" %create_report.content
        sys.exit(1)
    returndata = json.loads(create_report.content)
    reportid = returndata['id'].replace(":", "%3A")
    report_payload = "{\"name\":\"Daily Backup Administrator Report\",\"filters\":{\"dateConfig\":{\"period\":\"PastDay\"}},\"chart0\":{\"id\":\"chart0\",\"name\":\"Daily Protection Tasks by Status\",\"chartType\":\"StackedHorizontalBar\",\"attribute\":\"TaskType\",\"measure\":\"StackedTaskCountByStatus\"},\"chart1\":{\"id\":\"chart1\",\"name\":\"Failed Tasks by Object Type\",\"chartType\":\"VerticalBar\",\"attribute\":\"ObjectName\",\"measure\":\"FailedTaskCount\"},\"table\":{\"columns\":[\"TaskStatus\",\"TaskType\",\"ObjectName\",\"StartTime\",\"EndTime\",\"SlaDomain\",\"ObjectType\",\"Location\",\"Duration\",\"DedupRatio\",\"LogicalDedupRatio\",\"DataStored\",\"DataTransferred\"]}}"
    update_report = requests.patch('https://'+clusterip+'/api/internal/report/'+reportid, headers=authheader, data=report_payload, verify=False)
    if update_report.status_code != 200:
        print "Report could not be updated. %s" %update_report.content


def daily_dba(clusterip, authheader):
    print "Daily DBA Report "
    create_payload = "{\"name\":\"Daily DBA Report\",\"reportTemplate\":\"ProtectionTasksDetails\"}"
    create_report = requests.post('https://'+clusterip+'/api/internal/report', headers=authheader, data=create_payload, verify=False)
    if create_report.status_code != 201:
        print "Report creation failed. %s" %create_report.content
        sys.exit(1)
    returndata = json.loads(create_report.content)
    reportid = returndata['id'].replace(":", "%3A")
    report_payload = "{\"name\":\"Daily DBA Report\",\"filters\":{\"dateConfig\":{\"period\":\"PastDay\"},\"objectType\":[\"Mssql\"]},\"chart0\":{\"id\":\"chart0\",\"name\":\"Daily Protection Tasks by Status\",\"chartType\":\"StackedHorizontalBar\",\"attribute\":\"TaskType\",\"measure\":\"StackedTaskCountByStatus\"},\"chart1\":{\"id\":\"chart1\",\"name\":\"Failed Tasks by SQL Database\",\"chartType\":\"VerticalBar\",\"attribute\":\"ObjectName\",\"measure\":\"FailedTaskCount\"},\"table\":{\"columns\":[\"TaskStatus\",\"TaskType\",\"ObjectName\",\"ObjectType\",\"Location\",\"SlaDomain\",\"StartTime\",\"EndTime\",\"DataTransferred\",\"DataStored\",\"DedupRatio\",\"LogicalDedupRatio\",\"LogicalDataReductionPercent\"]}}"
    update_report = requests.patch('https://'+clusterip+'/api/internal/report/'+reportid, headers=authheader, data=report_payload, verify=False)
    if update_report.status_code != 200:
        print "Report could not be updated. %s" %update_report.content


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Insert default reports')
    parser.add_argument('rubrikip', action='store', help='Specify any Rubrik Node IP')
    parser.set_defaults(func=base)
    args = parser.parse_args()
    args = vars(args)

    args['func'](**args)
