#!/usr/bin/python

import dcmlogger
import recover
import pydicom
import sys
import json
import requests
import ConfigParser
import datetime
from pathlib import Path

class Config:
	mirth_host = ''
	mirth_port = ''
	mirth_base = ''
	dcm_host = ''
	dcm_port = ''
	
class Patient:
	id = ''
	name = ''
	access_no = ''
	dob = ''
	gender = ''
	modality = ''
	sop_class = ''
	sop_instance = ''
	study_instance = ''
	series_instance = ''
	mime_type = ''

dcmlogger.logger.info('postdcm is started')

def attachment_url(patient, config):
	p = patient
	c = config

	base = 'http://{0}:{1}'.format(c.dcm_host,c.dcm_port)
	
	if p.sop_class == 'Encapsulated PDF Storage':
		att_url = '{0}/rid/IHERetrieveDocument?requestType=DOCUMENT&documentUID={1}&preferredContentType=application%2Fpdf'.format(base, p.sop_instance)
		p.mime_type = 'application/pdf'
	else:
		att_url = '{0}/wado?requestType=WADO&studyUID={1}&seriesUID={2}&objectUID={3}'.format(base, p.study_instance, p.series_instance, p.sop_instance)
		p.mime_type = 'image/jpeg'
	
	return att_url
	
def json_data(patient, url):

	pat = patient
	result_json = {
	  "patient": {
		"patient_id": pat.id,
		"patient_dob": pat.dob,
		"patient_name": pat.name,
		"patient_gender": pat.gender
	  },
	  "result_exam_data": {
		"his_order_id": pat.access_no,
		"order_status":"COMPLETED",
		"format_type": pat.mime_type,
		"url" : url,
		"entry": ""
	  }
	}
		
	return result_json
		
def post(json_data, config):

	conf = config
	mirth_url = 'http://{0}:{1}{2}'.format(conf.mirth_host, conf.mirth_port, conf.mirth_base)
	
	r = requests.post(mirth_url, data = json.dumps(json_data))
	
	dcmlogger.logger.info('POST ' +mirth_url)

	return r.status_code

	
# Read Config file
config = ConfigParser.ConfigParser()
config.read('config.ini')

# Set config to conf
conf = Config()
conf.mirth_host = config.get('Mirth','host')
conf.mirth_port = config.get('Mirth','port')
conf.mirth_base = config.get('Mirth','base_url')
conf.dcm_host = config.get('WebDicomServer', 'host')
conf.dcm_port = config.get('WebDicomServer', 'port')

# Check Dicom file
filename = sys.argv[1]
dcm_file = Path(filename)

if dcm_file.is_file():

	dcmlogger.logger.info('Read DICOM file')	
	pat = Patient()
	with pydicom.dcmread(filename, force=True) as ds:
	
		try: 
			pat.id = ds.PatientID
			pat.name = ds.PatientName
			pat.access_no = ds.AccessionNumber
			pat.dob = ds.PatientBirthDate
			pat.gender = ds.PatientSex
			pat.modality = ds.Modality
			pat.sop_class = ds.SOPClassUID
			pat.sop_instance = ds.SOPInstanceUID
			pat.study_instance = ds.StudyInstanceUID
			pat.series_instance = ds.SeriesInstanceUID
		
		except AttributeError as e:
			dcmlogger.logger.error(e)
				

	# Construct attachement URL
	att_url = attachment_url(pat, conf)
	
	# Construct Json data
	result = json_data(pat, att_url)
	
	# Ready to POST json
	status = post(result, conf)
	if status != 200:
		
		dcmlogger.logger.error('HTTP Response : ' + str(status) + ' [error]')
		dcmlogger.logger.warning('Retry sending')
		# Recover loss sending
		if recover.is_created != True:
			recover.create()
		recover.insert(pat.id,filename, status)
		recover.close()
	else:
		dcmlogger.logger.info('HTTP Response : ' + str(status) + ' [success]')
		sys.exit(0)
	
