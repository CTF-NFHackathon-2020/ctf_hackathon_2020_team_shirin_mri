
import os

import synapseclient

import synread

syn = synapseclient.Synapse()
syn.login()

def getSynData() :
	l = syn.tableQuery('select * from syn20686637')
	return l.asDataFrame()

def filterdf(df, f1, f2 = lambda row : row) :
	return [f2(row) for i,row in df.iterrows() if f1(row)]

def getXlsFiles(ldf) :
	xlsRows = filterdf(ldf, lambda row : row['name'].endswith('.xls'))
	for row in xlsRows :
		syn.get(row['id'],downloadLocation='xls')

def checkPatientFiles() :
	xlsPatients = synread.getXlsPatients()
	segPatients = synread.getSegPatients()
	assert len(xlsPatients)==50, 'wrong number of patients'
	assert xlsPatients==segPatients, 'xls - segmentation patient numbers mismatch'

def getImsFor(ldf, patientNos=None) :
	imRows = filterdf(ldf,lambda row : row['name'].endswith('.dcm'))
	patientsWithIms = set(int(imRow['individualId'][-3:]) for imRow in imRows)
	segPatients = synread.getSegPatients()
	if patientNos is None :
		patientNos = segPatients
	for patientNo in patientNos :
		print(f'Patient {patientNo:03d}')
		if patientNo not in segPatients :
			print('not found!')
			continue
		patientImRows = [imRow for imRow in imRows if int(imRow['individualId'][-3:])==patientNo]
		print('segmentation shape',synread.getPatientSeg(patientNo).shape)
		patientDir = f'imstacks-{patientNo:03d}'
		for imRow in patientImRows :
			stackDir = os.path.join(patientDir,imRow['parentId'])
			if not os.path.exists(stackDir) :
				os.makedirs(stackDir)
			syn.get(imRow['id'], downloadLocation=stackDir)
