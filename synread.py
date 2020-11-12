
import os

import numpy as np
import pandas as pd

import nibabel
import pydicom

def getXlsPatients() :
	return set(int(fn[6:9]) for fn in os.listdir('xls'))
def getSegPatients() :
	return set(int(fn[13:16]) for fn in os.listdir('segmentation'))

def getPatientIms(patientNo) :
	imDir = f'imstacks-{patientNo:03d}'
	if not os.path.exists(imDir) :
		return []
	stacks = sorted(os.listdir(imDir))
	res = [[] for stackDir in stacks]
	for i,stackDir in enumerate(stacks) :
		imFNames = sorted(os.listdir(os.path.join(imDir,stackDir)))
		for imFName in imFNames :
			res[i].append(pydicom.dcmread(os.path.join(imDir,stackDir,imFName)))
	return res
def printPatientInfo(patientNo) :
	seg = getPatientSeg(patientNo)
	imStacks = getPatientIms(patientNo)
	print(f'patient {patientNo:03d} ss{seg.shape},',end='')
	segImShape = {(seg.shape[1],seg.shape[0])}
	for i,imStack in enumerate(imStacks) :
		imShapes = set()
		for j,dcmIm in enumerate(imStack) :
			imShapes.add((dcmIm.Rows,dcmIm.Columns))
		assert len(imShapes)==1,"multiple image shapes found!"
		print(f' s{i} - {len(imStack)}',imShapes,end='')
		if imShapes==segImShape and len(imStack)==seg.shape[2] :
			print(' ***',end='')
	print()

def printAllPatientInfo() :
	for patientNo in sorted(getSegPatients()) :
		printPatientInfo(patientNo)

import math
def getPatientSeg(patientNo) :
	arr = nibabel.load(os.path.join('segmentation',f'segmentation-{patientNo:03d}.nii.gz'))
	return arr.get_data().astype(np.uint8)
allPatientNos = sorted(getSegPatients())
def getPatientXls(patientNo) :
	return pd.read_excel(os.path.join('xls',f'wbmri_{patientNo:03d}.xls'))
def getPatientTumorTypes(patientNo) :
	df = getPatientXls(patientNo)
	assert df.iloc[3,2].lower()=='type', "missing tumor type header"
	pos = 4
	res = []
	while isinstance(df.iloc[pos,2],int) :
		res.append(df.iloc[pos,2])
		pos += 1
	return res
def getTumorTypeMap(patientNos) :
	return dict((patientNo,getPatientTumorTypes(patientNo))
				 for patientNo in patientNos)
allPatientTumorTypes = getTumorTypeMap(allPatientNos)
allPatientSegs = {}
def checkAllPatientSegs() :
	for patientNo in allPatientNos :
		tumorTypes = allPatientTumorTypes[patientNo]
		print(patientNo,end='')
		if not set(tumorTypes) <= {0,1} :
			print(' unexpected tumor type',tumorTypes,end='')
		seg = getPatientSeg(patientNo)
		tumorsMarked = set(seg.flatten())
		tumorsInXls = set(range(len(tumorTypes)+1))
		if tumorsMarked-tumorsInXls :
			print(' tumors marked but not in XLS',tumorsMarked-tumorsInXls,end='')
		if tumorsInXls-tumorsMarked :
			print(' tumors in XLS but not marked',tumorsInXls-tumorsMarked,end='')
		mp = np.zeros(256,dtype=np.uint8)
		for i,tumorType in enumerate(tumorTypes) :
			mp[i+1] = tumorType+1
		allPatientSegs[patientNo] = mp[seg]
		print()
