import pandas as pd
import os
import math
import collections
import shutil

def nested_dict():
    return collections.defaultdict(nested_dict)

dOfMetabolicProfil={}

#Paths
DirectoryPath="./Output/CompareModel/"
OutputPath="./Output/OutputCompare/"

# threshold
RValue=0
MAPEValue=0.5
TTValue=10000
RMSLEValue=10000
RMSEValue=100000
MSEValue=100000
MAEValue=100000


#Creation of directory
shutil.rmtree(OutputPath)
os.makedirs(OutputPath)
os.makedirs(OutputPath+"Full/")
os.makedirs(OutputPath+"Summary/")



setInstitutes=set()
setTreatments=set()
setVariables=set()

#No underscore in file name

dVariabletoDataframe={}

#load all files and find all institutes/treatments/Variables
#Data are stored in d(Variable)>d(Institues)>d(Treatments)
for file in os.listdir(DirectoryPath):
	lCarac=[]
	lCarac=file[:-4].split("_")
	Variable=lCarac[0]
	Institute=lCarac[1]
	Treatments=lCarac[2]
	setVariables.add(Variable)
	setInstitutes.add(lCarac[1])
	setTreatments.add (Treatments)
	df=pd.read_csv(DirectoryPath+file, sep="\t", header=0, index_col=0)
	df.columns = [c.replace('TT (Sec)', 'TT') for c in df.columns]
	ModelColumn=df["Model"]
	df=df.drop('Model', axis=1)
	if Variable in dVariabletoDataframe:
		if Institute in dVariabletoDataframe[Variable]:
			if Treatments in dVariabletoDataframe[Variable][Institute]:
				dVariabletoDataframe[Variable][Institute][Treatments][file[:-4]]=df
			else:
				dVariabletoDataframe[Variable][Institute][Treatments]={}
				dVariabletoDataframe[Variable][Institute][Treatments][file[:-4]]=df	
		else:
			dVariabletoDataframe[Variable][Institute]={}
			dVariabletoDataframe[Variable][Institute][Treatments]={}
			dVariabletoDataframe[Variable][Institute][Treatments][file[:-4]]=df
	else:
		dVariabletoDataframe[Variable]={}
		dVariabletoDataframe[Variable][Institute]={}
		dVariabletoDataframe[Variable][Institute][Treatments]={}
		dVariabletoDataframe[Variable][Institute][Treatments][file[:-4]]=df
		

#Write all files
for Variable in dVariabletoDataframe:
	print (Variable)
	dResults=nested_dict()
	print (OutputPath+"Summary/"+Variable+"_summary.csv")
	with open(OutputPath+"Summary/"+Variable+"_summary.csv","w") as outputfile:
		i=0
		for Institutes in dVariabletoDataframe[Variable]:
			for Treatments in dVariabletoDataframe[Variable][Institutes]:
				with open(OutputPath+"Full/"+Variable+"_"+Institutes+"_"+Treatments+"_summary.csv","w") as FullFile:
					lOfFrame=[]
					for frame in dVariabletoDataframe[Variable][Institutes][Treatments]:
						lOfFrame.append(dVariabletoDataframe[Variable][Institutes][Treatments][frame])
					df = pd.concat(lOfFrame)
					by_row_index = df.groupby(df.index)
					df_means = by_row_index.mean()
					df_std = by_row_index.std()
					df_std = df_std.add_suffix('_STD')
					df_final= pd.concat([df_means,df_std,ModelColumn],axis=1)
					df_final=df_final.sort_index(axis=1)
					column_to_move = df_final.pop("Model")
					df_final.insert(0, "Model", column_to_move)
					df_final.to_csv(FullFile,sep='\t')
					df_summary=df_final[(df_final["R2"]>RValue)&(df_final["MAE"]<MAEValue)&(df_final["MAPE"]<MAPEValue)&(df_final["MSE"]<MSEValue)&(df_final["RMSE"]<RMSEValue)&(df_final["RMSLE"]<RMSLEValue)&(df_final["TT"]<TTValue)]
					dResults[Treatments][Institutes]=df_summary
		lTreatments=sorted(dResults.keys(), key=lambda x:x.lower())
		for Treatments in lTreatments:
			lInstitutes=sorted(dResults[Treatments].keys(), key=lambda x:x.lower())
			for Institutes in lInstitutes:
				if not dResults[Treatments][Institutes].empty:
					outputfile.write(Treatments+"\t"+Institutes+"\n")
					dResults[Treatments][Institutes].to_csv(outputfile,sep='\t')
					outputfile.write("\n")
					i+=1
		if i==0:
			outputfile.write("No results")
	outputfile.close()			
		

