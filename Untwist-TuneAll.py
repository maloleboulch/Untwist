#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Load all package
from pycaret.regression import *
import pandas as pd
import os
import pycaret
import random


# In[2]:


#Where are we?
loc = os.getcwd()


# In[3]:


pycaret.utils.version()


# In[4]:


#Load all metabolic profile presents in /Data/Metabolic/ directory (Control, Drought and Heat)
dOfMetabolicProfil={}
for file in os.listdir("./Data/Metabo/Metabolic/"):
    df=pd.read_csv("./Data/Metabo/Metabolic/"+file)
    dOfMetabolicProfil[file[:-4]]=df


# In[5]:


#cheack headers
dOfMetabolicProfil["control"].head()


# In[6]:


#Load all CSV presents in /Data/TKW/ directory (Control, Drought and Heat)
# dOfEntry={}
# for file in os.listdir("./Data/TKW/"):
#     df=pd.read_csv("./Data/TKW/"+file)
#     dOfEntry[file[:-4]]=df


# In[7]:


#Load all CSV presents in /Data/Pheno directory
dOfEntry={}
for root, dirs, files in os.walk("./Data/Variable/OnlyTKW/"):
    if files:
        for item in files:
            df=pd.read_csv(root+"/"+item)
            dOfEntry[item[:-4]]=df
            


# In[8]:


#Merge all metabolic profile with metabolic profile
dVariableInstituteTreatments={}
for item in dOfMetabolicProfil:
    for key in dOfEntry:
        dVariableInstituteTreatments[key+"_"+item]=pd.merge(dOfEntry[key], dOfMetabolicProfil[item], on="Lines", how='inner')


# In[9]:


#print (dVariableInstituteTreatments.keys())


# In[10]:

seedID = random.randint(1,4294967295)

for key in dVariableInstituteTreatments:
    with open("./Output/CompareModel/"+str(seedID)+".csv",'a') as outputfile:
        print (key)
        demo = setup(data=dVariableInstituteTreatments[key],
                     numeric_features = list(dVariableInstituteTreatments[key])[2:],
                     target= dVariableInstituteTreatments[key].columns[1],
                     ignore_features=["Lines"],
                     normalize = True,
                     fold= 2,
                     remove_multicollinearity = True, multicollinearity_threshold = 0.9,
                     train_size=0.75,
                     session_id= seedID
                    )
        test=pull()
    #fold=43 allowing us to use LOOCV because of the small number of sample
    #fold=11 for 4 vs 40
        best=compare_models(n_select = 16,exclude=["lar","dt","omp","par","mlp","kr","tr","svm","dummy","xgboost","catboost"],turbo=False)
        compare_model_results=pull()
        with open("./Output/"+str(key)+"_"+str(seedID)+".csv","w") as dataframe:
            compare_model_results.to_csv(dataframe,sep="\t",encoding='utf-8')
        outputfile.write(key+"\t")
        print (best)
        for item in best:
            print (item)
			#Pas de Tuned model
            outputfile.write(str(item)+"\t")
            test=create_model(item)
            final=predict_model(test)
            BestModel=pull()
            with open("./Output/AllModel/"+str(key)+"_"+str(seedID)+"_"+str(item)+".csv",'w') as BestFile:
                BestModel.to_csv(BestFile,sep="\t",encoding='utf-8')
            TunedModel=tune_model(test,n_iter = 2000,optimize="R2",fold=2)
            resultsTunedModel=pull()
            with open("./Output/AllTunedModel/"+str(key)+"_"+str(seedID)+"_"+str(item)+".csv",'w') as TunedFile:
                resultsTunedModel.to_csv(TunedFile,sep="\t",encoding='utf-8')
            finalTunedModel=predict_model(TunedModel)
            ResultsFinalTunedModel=pull()
            with open("./Output/AllFinalTunedModel/"+str(key)+"_"+str(seedID)+"_"+str(item)+".csv",'w') as FinalTunedFile:
                ResultsFinalTunedModel.to_csv(FinalTunedFile,sep="\t",encoding='utf-8')

        outputfile.write("\n")
        outputfile.close()
        
        
