import pandas as pd
import os
import math
import collections
import shutil

def nested_dict():
    return collections.defaultdict(nested_dict)

dOfMetabolicProfil={}

#Paths
DirectoryPath="./Output/AllFinalTunedModel/"
OutputPath="./Output/OutputFinalModel/"

# threshold
RValue=0
MAPEValue=0.5
TTValue=100000
RMSLEValue=100000
RMSEValue=1000000
MSEValue=1000000
MAEValue=1000000


#Creation of directory
shutil.rmtree(OutputPath)
os.makedirs(OutputPath)
os.makedirs(OutputPath+"Full/")
os.makedirs(OutputPath+"Summary/")



setInstitutes=set()
setTreatments=set()
setVariables=set()
setModel=set()
#No underscore in file name


dVariabletoDataframe={}

#load all files and find all institutes/treatments/Variables
#Data are stored in d(Variable)>d(Institues)>d(Treatments)>d(Model)


for file in os.listdir(DirectoryPath):
	lCarac=[]
	lCarac=file[:-4].split("_")	
	Variable=lCarac[0]
	Institute=lCarac[1]
	Treatments=lCarac[2]
	Model=lCarac[4].split("(")[0]
	setVariables.add(Variable)
	setInstitutes.add(lCarac[1])
	setTreatments.add(Treatments)
	setModel.add(Model)
	df=pd.read_csv(DirectoryPath+file, sep="\t", header=0, index_col=0)
	df.columns = [c.replace('TT (Sec)', 'TT') for c in df.columns]
	ModelColumn=df["Model"]
	df=df.drop('Model', axis=1)
	#print (file[:-4]) #Changer le nom qui est chargé?
	if Variable in dVariabletoDataframe:
		if Institute in dVariabletoDataframe[Variable]:
			if Treatments in dVariabletoDataframe[Variable][Institute]:
				if Model in dVariabletoDataframe[Variable][Institute][Treatments]:
					dVariabletoDataframe[Variable][Institute][Treatments][Model][file[:-4]]=df
				else:
					dVariabletoDataframe[Variable][Institute][Treatments][Model]={}
					dVariabletoDataframe[Variable][Institute][Treatments][Model][file[:-4]]=df
			else:
				dVariabletoDataframe[Variable][Institute][Treatments]={}
				dVariabletoDataframe[Variable][Institute][Treatments][Model]={}
				dVariabletoDataframe[Variable][Institute][Treatments][Model][file[:-4]]=df
		else:
			dVariabletoDataframe[Variable][Institute]={}
			dVariabletoDataframe[Variable][Institute][Treatments]={}
			dVariabletoDataframe[Variable][Institute][Treatments][Model]={}
			dVariabletoDataframe[Variable][Institute][Treatments][Model][file[:-4]]=df
	else:
		dVariabletoDataframe[Variable]={}
		dVariabletoDataframe[Variable][Institute]={}
		dVariabletoDataframe[Variable][Institute][Treatments]={}
		dVariabletoDataframe[Variable][Institute][Treatments][Model]={}
		dVariabletoDataframe[Variable][Institute][Treatments][Model][file[:-4]]=df

#Write all files
for Variable in dVariabletoDataframe:
	#print (Variable)
	dResults=nested_dict()
	#print (OutputPath+"Summary/"+Variable+"_summary.csv")
	with open(OutputPath+"Summary/"+Variable+"_summary.csv","w") as outputfile:
		i=0
		for Institutes in dVariabletoDataframe[Variable]:
			for Treatments in dVariabletoDataframe[Variable][Institutes]:
				for Model in dVariabletoDataframe[Variable][Institutes][Treatments]:
					with open(OutputPath+"Full/"+Variable+"_"+Institutes+"_"+Treatments+"_"+Model+"_summary.csv","w") as FullFile:
						lOfFrame=[]
						for frame in dVariabletoDataframe[Variable][Institutes][Treatments][Model]:
							lOfFrame.append(dVariabletoDataframe[Variable][Institutes][Treatments][Model][frame])
						df = pd.concat(lOfFrame)
						by_row_index = df.groupby(df.index)
						df_means = by_row_index.mean()
						df_std = by_row_index.std()
						df_std = df_std.add_suffix('_STD')
						df_final= pd.concat([df_means,df_std,ModelColumn],axis=1)
						df_final=df_final.sort_index(axis=1)
						column_to_move = df_final.pop("Model")
						df_final.insert(0, "Model", pd.Series(Model))
						df_final.to_csv(FullFile,sep='\t')
						df_summary=df_final[(df_final["R2"]>RValue)&(df_final["MAE"]<MAEValue)&(df_final["MAPE"]<MAPEValue)&(df_final["MSE"]<MSEValue)&(df_final["RMSE"]<RMSEValue)&(df_final["RMSLE"]<RMSLEValue)]
						dResults[Treatments][Institutes][Model]=df_summary
					FullFile.close()
		lTreatments=sorted(dResults.keys(), key=lambda x:x.lower())
		for Treatments in lTreatments:
			lInstitutes=sorted(dResults[Treatments].keys(), key=lambda x:x.lower())
			for Institutes in lInstitutes:
				lModel=sorted(dResults[Treatments][Institutes].keys(), key=lambda x:x.lower())
				outputfile.write(Treatments+"\t"+Institutes+"\n")
				outputfile.write("Model\tMAE\tMAE_STD\tMAPE\tMAPE_STD\tMSE\tMSE_STD\tR2\tR2_STD\tRMSE\tRMSE_STD\tRMSLE\tRMSLE_STD\n")
				lOfDatadrame=[]
				for Model in lModel:
					if not dResults[Treatments][Institutes][Model].empty:
						lOfDatadrame.append(dResults[Treatments][Institutes][Model])
						# ~ dResults[Treatments][Institutes][Model].to_csv(outputfile,sep='\t',header=False,index=False)
						i+=1
				if not i==0:
					if not lOfDatadrame==[]:
						df_temp=pd.concat(lOfDatadrame)
						df_temp=df_temp.sort_values('R2',ascending=False)
						df_temp.to_csv(outputfile,sep='\t',header=False,index=False)
					else:
						print (lOfDatadrame)
						print (len(lOfDatadrame))
						print (Institutes)
						print (Treatments)
						print (Variable)
				
		if i==0:
			outputfile.write("No results")
	outputfile.close()				
