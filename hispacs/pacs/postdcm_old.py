#!/usr/bin/python

import recover
import pydicom
import sys
import json
import requests
import ConfigParser
import datetime
from pathlib import Path

# Read config file
config = ConfigParser.ConfigParser()
config.read('config.ini')
host = config.get('Mirth','host')
port = config.get('Mirth','port')
base_url = config.get('Mirth','base_url')
log = config.get('Mirth','log')

argn = len(sys.argv)

if argn < 2:

    print ("wrong number or argument given")
    exit (1)

dcm_file = Path(sys.argv[1])

if dcm_file.is_file():

	ds = pydicom.dcmread(sys.argv[1], force=True)
	pat_name = ds.PatientName
	pat_id = ds.PatientID
	acc_no = ds.AccessionNumber
	pat_dob = ds.PatientBirthDate
	pat_sex = ds.PatientSex
	mod = ds.Modality
	sopc_uid = ds.SOPClassUID
	sopi_uid = ds.SOPInstanceUID
	stud_uid = ds.StudyInstanceUID
	ser_uid = ds.SeriesInstanceUID
else:
	print 'DICOM File not found. Program Exit(1)'
	exit(1)

host_web = config.get('WebDicomServer', 'host')
port_web = config.get('WebDicomServer', 'port')
web_url = 'http://'+host_web+':'+port_web

if sopc_uid == 'Encapsulated PDF Storage':
	mime_type = 'application/pdf'
	url = web_url+'/rid/IHERetrieveDocument?requestType=DOCUMENT&documentUID='+sopi_uid+'&preferredContentType=application%2Fpdf'
else:
	mime_type = 'image/jpeg'
	url = web_url+'/wado?requestType=WADO&studyUID='+stud_uid+'&seriesUID='+ser_uid+'&objectUID='+sopi_uid

resjson = {
  "patient": {
    "patient_id": pat_id,
    "patient_dob": pat_dob,
    "patient_name": pat_name,
    "patient_gender": pat_sex
  },
  "result_exam_data": {
    "his_order_id": acc_no,
    "order_status":"COMPLETED",
    "format_type": mime_type,
	"url" : url,
    "entry": ""
  }
}

# Construct post url
post_url = 'http://'+host+':'+port+base_url

r = requests.post(post_url, data = json.dumps(resjson))

if r.status_code != 200:
	print recover.is_created
	if recover.is_created != True:
		recover.create()
	recover.insert(pat_id,sys.argv[1],'failed')
	recover.close()

# Reformat date
date = datetime.datetime.now()
f = date.strftime("%Y-%m-%d %H:%M:%S")

print f + ' --- POST '+post_url+ ' ['+str(r.status_code)+']'
