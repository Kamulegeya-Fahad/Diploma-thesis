# -*- coding: utf-8 -*-
"""3 state trial Diploma thesis project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cG7w7v3c_VYr6IhS5HI8pT8_7OxVL4HK

#Important libraries
"""

import random
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import matplotlib.gridspec as gridspec
from matplotlib.ticker import PercentFormatter
import matplotlib.ticker
import seaborn as sns
from collections import Counter
import scipy


#!pip install control
import control

"""#The instructions to the walker"""

#the instructions
def freedman_diaconis(data, returnas="width"):
    """
    Use Freedman Diaconis rule to compute optimal histogram bin width. 
    ``returnas`` can be one of "width" or "bins", indicating whether
    the bin width or number of bins should be returned respectively. 

    Parameters
    ----------
    data: np.ndarray
        One-dimensional array.

    returnas: {"width", "bins"}
        If "width", return the estimated width for each histogram bin. 
        If "bins", return the number of bins suggested by rule.
    """
    data = np.asarray(data, dtype=np.float_)
    IQR  = stats.iqr(data, rng=(25, 75), scale="raw", nan_policy="omit")
    N    = data.size
    bw   = (2 * IQR) / np.power(N, 1/3)

    if returnas=="width":
        result = bw
    else:
        datmin, datmax = data.min(), data.max()
        datrng = datmax - datmin
        result = int((datrng / bw) + 1)
    return(result)


def Simulator(A):
 max_steps =10000        #maximum number of steps                                                          
 counter=0
 state=[1]  #initial state                                                                                               
 time=[0]

 #random rates              
 [k1,k2,k3,k4,k5,k6]=A#np.random.randint(1, 6, 6)                                  

 #print('\n k1 = ',k1,'\n k2 = ',k2,'\n k3 = ',k3,'\n k4 = ',k4,
 #     '\n k5 = ',k5,'\n k6 = ',k6)

 #k2=k4=k6=0.002


 a=k1+k6
 b=k3+k2
 c=k4+k5


#the walker

 while counter < max_steps:
      if state[-1]==1:
         props_sum=k1+k6
         weights=[k1,k6]
         q=random.uniform(0, 1)
         wait= (1.0 / props_sum)*np.log(1/q)
         new_state=random.choices([2,3], weights=weights)
         state=np.append(state,new_state)
         new_time=wait+time[-1]
         time=np.append(time,new_time)
         counter=counter+1
      elif state[-1]==2:
         props_sum=k2+k3
         weights=[k2,k3]
         q=random.uniform(0, 1)
         wait= (1.0 / props_sum)*np.log(1/q)
         new_state=random.choices([1,3], weights=weights)
         state=np.append(state,new_state)
         new_time=wait+time[-1]
         time=np.append(time,new_time)
         counter=counter+1
      elif state[-1]==3:
         props_sum=k4+k5
         weights=[k4,k5]
         q=random.uniform(0, 1)
         wait= (1.0 / props_sum)*np.log(1/q)
         new_state=random.choices([2,1], weights=weights)
         state=np.append(state,new_state)
         new_time=wait+time[-1]
         time=np.append(time,new_time)
         counter=counter+1


#visualizing the walker
#plt.figure(figsize=(20,4))
#plt.step(time,state)



#the searcher

 R_transition = [1,2]                                                                #the transitions to the right
 N = len(R_transition)
 possibles = np.where(state == R_transition[0])[0]
 R = []
 for p in possibles:
    check = state[p:p+N]
    if np.all(check == R_transition):
        R.append(p)
#print('R--------------------',R)


 L_transition = [2,1]                                                                  #the transitions to the left
 N = len(L_transition)
 possibles = np.where(state ==L_transition[0])[0]
 L = []
 for p in possibles:
    check = state[p:p+N]
    if np.all(check ==L_transition):
        L.append(p)
#print('L------------------',L)



#the mixer

 # R-L and R-R                                                                                                             
 RR=[]
 RL=[max_steps,max_steps]
 for i in R:
  k=[j for j in L if j>i]
  k=min(np.append(k,max_steps))

  if k==RL[-1]:
   RR=np.append(RR,[n,i])
   #print('x')
   RL[-2]=max_steps
   RL[-1]=max_steps
  n=i  
  RL=np.append(RL,[i,k])


#split up the RR array
 split=[i for i in range(0,len(RR))]
#print(split)

 OG=[]
 for i in split:
  if i%2 == 0:
    i=int(i)
    OG.append([RR[i],RR[i+1]])

#print(OG)



 #the waiting time RR
 wait_RR=[]                                                                            
 for i in OG:
  #print(i)
  T1=i[0]
  T2=i[1]

  wait_RR=np.append(wait_RR,time[int(T2)]-time[int(T1)])
#print(wait_RR)

 return wait_RR


def NormalizeData(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))

[k1,k2,k3,k4,k5,k6]=[4,5,2,2,2,1]
#print('\n k1 = ',k1,'\n k2 = ',k2,'\n k3 = ',k3,'\n k4 = ',k4,
 #     '\n k5 = ',k5,'\n k6 = ',k6)
a=k1+k6
b=k3+k2
c=k4+k5

p3=control.TransferFunction([k1*k3*k5],[1,a+b+c,(a*b+a*c+b*c)-(k4*k3)-(k5*k6),(a*b*c)-(a*k3*k4)-(b*k5*k6)])

print('\n p3 \n',p3,'\n',p3.pole()) 

tm,p3=control.impulse_response(p3)
p3 =NormalizeData(p3)
plt.plot(tm,p3,label='First analytical RR distribution',linestyle='dashed',color='b')

'''
wait_RR= Simulator([4,5,2,2,2,1])
NBR_BINS= freedman_diaconis(wait_RR, returnas="bins")
sns.distplot(wait_RR, hist=True, kde=False,
bins=NBR_BINS, 
hist_kws={'edgecolor':'black','label':'First simulation RR distribution','color':'b'},norm_hist=True
,kde_kws={'label':'KDE simulation RR distribution'}) 

'''
x = Simulator([4,5,2,2,2,1])
NBR_BINS= freedman_diaconis(x, returnas="bins")
counts,bin_edges = np.histogram(x,NBR_BINS,density=True)
bin_centres = (bin_edges[:-1] + bin_edges[1:])/2.
err = np.random.rand(bin_centres.size)*0.5
plt.errorbar(bin_centres, counts,fmt='o',label='First simulation',marker='s',color='b')

#*************************************************************************

A=[k1,k2,k3,k4,k5,k6]=[1,2,1,1,3,5]#np.random.randint(1, 6, 6)
print('\n k1 = ',k1,'\n k2 = ',k2,'\n k3 = ',k3,'\n k4 = ',k4,
      '\n k5 = ',k5,'\n k6 = ',k6)
a=k1+k6
b=k3+k2
c=k4+k5

p3=control.TransferFunction([k1*k3*k5],[1,a+b+c,(a*b+a*c+b*c)-(k4*k3)-(k5*k6),(a*b*c)-(a*k3*k4)-(b*k5*k6)])

print('\n p3 \n',p3,'\n',p3.pole()) 

tm,p3=control.impulse_response(p3)
p3 =NormalizeData(p3)
plt.plot(tm,p3,label='Second analytical RR distribution',linestyle='dashed',color='r')


'''
wait_RR= Simulator(A)
NBR_BINS= freedman_diaconis(wait_RR, returnas="bins")
sns.distplot(wait_RR, hist=True, kde=False,
bins=NBR_BINS, 
hist_kws={'edgecolor':'black','label':'Second simulation RR distribution','color':'r'},norm_hist=True
,kde_kws={'label':'KDE simulation RR distribution'}) 
'''
x = Simulator(A)
NBR_BINS= freedman_diaconis(x, returnas="bins")
counts,bin_edges = np.histogram(x,NBR_BINS,density=True)
bin_centres = (bin_edges[:-1] + bin_edges[1:])/2.
err = np.random.rand(bin_centres.size)*0.5
plt.errorbar(bin_centres, counts,fmt='o',label='Second simulation',marker='v',color='r')

plt.title('RR transition times distributions\' comparison')
plt.yscale('log')
plt.ylabel('Density')
plt.xscale('log')
plt.xlabel('Time in seconds')
plt.legend()
#plt.show()

plt.savefig('3 state loglog comparison.png', dpi=300)
