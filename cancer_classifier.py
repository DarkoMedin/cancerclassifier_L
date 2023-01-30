# -*- coding: utf-8 -*-
"""Cancer classifier.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1teVe6N3JPBOoTLwMZwxOPB2cCfAa7f6r
"""

#Import the libraries for the project
import numpy as np
import pandas  as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import lightgbm as lgbm
from lightgbm import LGBMClassifier
from sklearn.preprocessing import LabelEncoder 
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from sklearn.impute import KNNImputer
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import accuracy_score
from sklearn.utils import shuffle

#Load the dataset
df=pd.read_csv(r'E-MTAB-2770-query-results.tpms.tsv',
             sep="\t", comment='#')

df

#Define the targets for prediction (cancer samples)
target=list(df.columns[2:])

#A function to engineer the labels  list
# The 2 labels of interest are 'leukemia' and 'other cancers'
def eng_labels(x):
   labs=[]
   for s in x:
         if 'leukemia' in s:
             labs.append('leukemia')
         else: 
             labs.append('other cancers')
   return(labs)

#Engineer the labels
labs=eng_labels(target)
labs=['Gene']+labs
labs=pd.Series(labs)

#Engineer the data
data=df.iloc[:,1:]   
data.columns=labs
data=data.transpose()
data.columns=data.loc['Gene',:]
data=data.iloc[1:,:]
pd.set_option('display.max_rows', 20)
pd.set_option('display.max_columns', 20)
data.head(20)

"""# New Section"""

#Visualize SCYL3 gene expression across the sample
sns.histplot(data['SCYL3'], kde=True)

sns.histplot(data['DPM1'], kde=True)

sns.histplot(data['MSMO1'], kde=True)

#Data preprocessing
data_x=data                       
data_x=np.array(data_x)
le = LabelEncoder()
le.fit(data.index)
data_y=le.transform(data.index) 
data_y=pd.Series(data_y)

#Train/Test split
xtrain, xtest, ytrain, ytest = train_test_split(
 data_x, data_y, test_size=0.33, random_state=5)

#Converting the data to np.arrays
#This is needed to facilitate the training process
xtrain=np.array(xtrain, dtype=np.float32)
ytrain=np.array(ytrain, dtype=np.float32)


xtrain, ytrain=shuffle(xtrain, ytrain)
xtest, ytest=shuffle(xtest, ytest)

#These are the parameters to use for tuning the training process
p={ 'boosting':'dart', 'learning_rate':0.01, 'objective':'binary', 'max_depth':6
   , 'num_leaves':102, 'min_data_in_leaf':40, 'bagging_fraction':1,'device_type':'cpu',
   'feature_fraction':1, 'verbose':0, 'bagging_freq':7, 'extra_trees':'true','cegb_tradeoff':5,
  'max_bin':100, 'min_data_in_bin':6,'n_estimators':15750}

#Train the classifier and name is lgbmodel
lgbmodel=LGBMClassifier(**p).fit(xtrain, ytrain)

#Make predictions and calculate accuracy
predictions = lgbmodel.predict(xtest)
rpreds = [round(i) for i in predictions]
accuracy = accuracy_score(ytest, rpreds)
accuracy



#Make the confusion matrix
cm = confusion_matrix(ytest, predictions)
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot()
plt.show()

#Extract the feature importances
importances=lgbmodel.feature_importances_
importances=pd.Series(importances)
importances.index=data.columns
importances= importances.sort_values(ascending=False)
importances[0:29].to_csv(r'important_genes.csv', sep='\t', header='true')

#Data visualization of the feature importances
plt.figure(figsize=(28,20))
plt.bar(importances[0:29].index, importances[0:29], width=0.7, bottom=None, align='center', data=None)