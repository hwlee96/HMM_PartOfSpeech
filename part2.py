#!/usr/bin/env python
# coding: utf-8

# In[1]:


import math
import copy
trainpath = r'C:\Users\user\Documents\MachineLearning01.112\MachineLearning-01.112\ML\Project\AL\train'
testpath = r'C:\Users\user\Documents\MachineLearning01.112\MachineLearning-01.112\ML\Project\AL\dev.in'
outputpath = r'C:\Users\user\Documents\MachineLearning01.112\MachineLearning-01.112\ML\Project\AL\devP2New.out'


# In[2]:


def emission(lines):
    xy={}
    y={}
    emi={}
    #bg = 0
    for i in range (len(lines)):
        #print(bg)
        if lines[i]!='\n':
            ls = lines[i].split(" ")
            y_ = ls[1].strip('\n')
            if ((ls[0],y_) not in xy):
                        xy[(ls[0],y_)] = 1
            else:
                        xy[(ls[0],y_)]+=1

            if (y_ not in y):
                        y[y_]= 1
            else:
                        y[y_]+=1
            #bg+=1
    for j in xy.keys():
                    emi[j]=(xy[j]/y[j[1]])
                    
    return(emi)     
            


# In[3]:


def smoothEmission(k,lines,lines2):
    x = {}
    Lines = copy.deepcopy(lines)
    Lines2= copy.deepcopy(lines2)
    for i in range (len(lines)):
        if lines[i]!='\n':
            ls = lines[i].split(" ")
            if ((ls[0]) not in x):
                    x[ls[0]] = 1
            else:
                    x[ls[0]] +=1
    print("step1 done")
    
    
    for i in range (len(lines)):
        if lines[i]!='\n':
            ls = lines[i].split(" ")
            if(x[ls[0]]<k):
                Lines[i]='unk '+ls[1]
                
    print("step2 done")
    
    for i in range(len(lines2)):
        if lines2[i]!='\n':
            if lines2[i].strip("\n") not in x:
                Lines2[i] = 'unk'
    print("step3 done")
    return(Lines,Lines2)


# In[4]:


def labelGenerator(lines,lines2):
    lines = smoothEmission(3,lines,lines2)[0]
    emi = emission(lines)  

    maxVal = {}
    d= {}
    w = {}
    for i in range (len(lines)):
        if lines[i]!='\n':
            ls = lines[i].split(" ")
            x_= ls[0]
            y_=ls[1].strip("\n")      
            if (x_ not in maxVal):
                maxVal[x_] = emi[(x_,y_)]
                d[x_ ]= y_
                w[x_] = [y_]
            elif(y_ not in w[x_] ):
                w[x_].append(y_)
                if(emi[(x_,y_)] > maxVal[x_]):
                    maxVal[x_] = emi[(x_,y_)]
                    d[x_] = y_
    return(d)
    


# In[5]:


def main(pathTrain,pathIn,pathOut):
    r = open(pathTrain,"r",encoding='utf-8')
    lines = r.readlines()
    r.close()

    r2 = open(pathIn,"r",encoding='utf-8')
    lines2 = r2.readlines()
    r.close()
    
   
    f = open(pathOut,"w+", encoding="utf-8")
    
    d = labelGenerator(lines,lines2)
    
    
    for line in lines2:
        if line[0]!="\n":
            if (line.strip("\n") in d):
                f.write(line.strip("\n") +" "+ d[line.strip("\n")]+"\n")
            else:
                f.write(line.strip("\n") +" "+ d["unk"]+"\n")
        else:
            f.write(line)
    f.close()
    #r.close()
    return (f)


# In[7]:


main(trainpath,testpath,outputpath)


# In[ ]:




