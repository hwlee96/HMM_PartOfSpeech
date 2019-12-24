#!/usr/bin/env python
# coding: utf-8

import copy
import math
import sys

#########################################
#######    CHANGE PATHS BELOW     #######
#########################################

trainpath = "/Users/khai/Home Documents/Term 6/Machine Learning/EN/train"
testpath = "/Users/khai/Home Documents/Term 6/Machine Learning/EN/dev.in"
outputpath = "/Users/khai/Home Documents/Term 6/Machine Learning/EN/dev.p3_1.out"

# From Part 2:
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
    #print("step1 done")

    for i in range (len(lines)):
        if lines[i]!='\n':
            ls = lines[i].split(" ")
            if(x[ls[0]]<k):
                Lines[i]='unk '+ls[1]

    #print("step2 done")

    for i in range(len(lines2)):
        if lines2[i]!='\n':
            if lines2[i].strip("\n") not in x:
                Lines2[i] = 'unk'
    #print("step3 done")
    return(Lines,Lines2)

def emission(lines):
    xy={}
    y={}
    emi={}
    bg = 0
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
            bg+=1
    for j in xy.keys():
                    emi[j]=(xy[j]/y[j[1]])

    return(emi)


# Part 3:
def transition(path):
    # q(u -> v) = count(u,v)/count(u)

    u_label = {}
    uv_label = {}

    prevState = ''
    currState = '***START***'

    for line in open(path, 'r'):

        if currState == '***STOP***':
            prevState = '***START***'
        else:
            prevState = currState

        line = line.rstrip()
        xy = line.split(' ')

        if len(xy) > 1:
            x, currState = xy

        else:
            if prevState == '##START##': break
            currState = '***STOP***'
            if currState in u_label:
                u_label[currState] += 1
            else:
                u_label[currState] = 1

        if prevState in u_label:
            u_label[prevState] += 1
        else:
            u_label[prevState] = 1

        if (prevState, currState) in uv_label:
            uv_label[(prevState,currState)] += 1

        else:
            uv_label[(prevState,currState)] = 1

        q = {}

        for i, count in u_label.items():
            for j in u_label:
                if (i,j) in uv_label:
                    countuv = uv_label[(i,j)]
                    q[(i,j)] = countuv/count


    return list(u_label.keys()), q


#viterbi:
def viterbi(states, emission, transition, sentence):
    e = emission
    t = transition
    n = len(sentence)

    smallest = math.log(sys.float_info.min)-1

    #initialize score dict
    scores = {}

    #i=0
    scores[0] = {}
    for j in states:
        if ("***START***", j) in t:
            trans = math.log(t[("***START***", j)])
        else:
            trans = smallest
        if (sentence[0], j) in e:
            emis = math.log(e[(sentence[0], j)])
        else:
            emis = smallest

        ans = trans + emis
        scores[0][j] = (ans, "***START***")


    for i in range(1, n):
        scores[i] = {}
        for j in states:
            findmax = []
            for l in states:
                if (l,j) in t:
                    trans = math.log(t[(l,j)])
                else:
                    trans = smallest
                if (sentence[i],j) in e:
                    emis = math.log(e[(sentence[i],j)])
                else:
                    emis = smallest
                score = scores[i-1][l][0] + trans + emis
                findmax.append(score)

            ans = max(findmax)
            state_ans = states[findmax.index(ans)]
            scores[i][j] = (ans, state_ans)


    #STOP state
    scores[n] = {}
    findmax = []
    for j in states:
        if (j,"***STOP***") in t:
            trans = math.log(t[(j,"***STOP***")])
        else:
            trans = smallest
        score = scores[n-1][j][0] + trans
        findmax.append(score)

    stop = max(findmax)
    state_ans = states[findmax.index(stop)]
    scores[n] = (stop, state_ans)

    #backtracking
    path = ['***STOP***']
    last = scores[n][1]
    path.append(last)

    for k in range((n-1), -1, -1):
        last = scores[k][last][1]
        path.append(last)


    return scores, list(reversed(path))


#get lines of training data
r1 =  open(trainpath,"r",encoding='utf-8')
lines1 = r1.readlines()
r1.close()

#get lines of test data
r2 =  open(testpath,"r",encoding='utf-8')
lines2 = r2.readlines()
r2.close()

print("smoothing the data...")
#smooth the data
train, test = smoothEmission(3, lines1, lines2)

#clean data
x = train
for i in range(len(x)):
    if x[i] != '\n':
        x[i]= x[i].rstrip('\n')

y = test
biglist = []
temp = []
for i in range(len(y)):
    if y[i] != '\n':
        y[i]= y[i].rstrip('\n')

for j in y:
    if j != "\n":
        temp.append(j)
    else:
        biglist.append(temp)
        temp = []

print("getting emission and transition...")
#get emission, transitions and states
e = emission(train)
labels, q = transition(trainpath)

lab = copy.deepcopy(labels)
lab.remove('***START***')
lab.remove('***STOP***')


# viterbi with whole training and test set
print("running viterbi...")
final = []
for sen in biglist:
    scores, path = viterbi(lab,e,q,sen)
    for i in path:
        if i != '***START***':
            final.append(i)

f = open(outputpath,"w+", encoding="utf8")

for i in range(len(final)):
    if final[i] != '***STOP***':
        f.write(test[i]+' '+final[i]+'\n')
    else:
        f.write('\n')

f.close()

print("done!!!")
