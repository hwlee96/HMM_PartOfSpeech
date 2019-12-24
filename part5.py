import copy
import math
import sys
import argparse

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

def emission(lines):
    xy={}
    y={}
    emi={}
    bg = 0
    for i in range (len(lines)):
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

def transition(path):
    # q(u -> v) = count(u,v)/count(u)
    u_label = {}
    uv_label = {}
    
    prevState = ''
    currState = '***START***'
    
    for line in open(path, 'r', encoding='utf-8'):
        
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
                else:
                    q[(i,j)] = 0
                
    return list(u_label.keys()), q

def viterbi_log(states, emission, transition, sentence, transition_back): #emission and transition are already logged
    e = emission
    t = transition
    n = len(sentence)
    t_back = transition_back
    
    smallest = math.log(sys.float_info.min)-1
    
    #initialize score dict
    scores = {}
    
    #i=0
    scores[0] = {}

    #START STATE
    for j in states:
        if ("***START***", j) in t and t[("***START***", j)] != 0:
        #print (t[("***START***", j)])
            trans = t[("***START***", j)]
        else:
            trans = smallest

        #trans_back
        if (j,"***START***") in t_back and t_back[(j,"***START***")] != 0:
            trans_back = t[(j,"***START***")]
        else:
            trans_back = smallest

        if (sentence[0], j) in e and e[(sentence[0], j)] != 0:
            emis = e[(sentence[0], j)]
        else:
            emis = smallest
        
        ans = trans + emis
        scores[0][j] = (ans, "***START***")
    
    
    for i in range(1, n):
        scores[i] = {}
        for j in states:
            findmax = []
            for l in states:
                if (l,j) in t and t[(l,j)] != 0:
                    trans = t[(l,j)]
                else:
                    trans = smallest

                #trans_back
                if (j,l) in t_back and t_back[(j,l)] != 0:
                    trans_back = t_back[(j,l)]
                else:
                    trans_back = smallest

                if (sentence[i],j) in e and e[(sentence[i],j)] != 0:
                    emis = e[(sentence[i],j)]
                else:
                    emis = smallest
                score = scores[i-1][l][0] + trans + emis + trans_back
                findmax.append(score)

            ans = max(findmax)
            state_ans = states[findmax.index(ans)]
            scores[i][j] = (ans, state_ans)
        
            
    #STOP state
    scores[n] = {}
    findmax = []
    for j in states:
        if (j,"***STOP***") in t and t[(j,"***STOP***")] != 0:
            trans = t[(j,"***STOP***")]
        else:
            trans = smallest

        #trans_back
        if ("***STOP***", j) in t_back and t_back[("***STOP***", j)] != 0:
            trans_back = t[("***STOP***", j)]
        else:
            trans_back = smallest

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

def perceptropUpdate(gold, predicted, sentence_words, e, q, q_back):
        
    for i in range(1, len(gold)):
        gold_previous = gold[i-1]
        gold_current = gold[i]
        predicted_previous = predicted[i-1]
        predicted_current = predicted[i]
        
        if (gold_previous, gold_current) != (predicted_previous, predicted_current):
            q[gold_previous, gold_current] += 1
            q[predicted_previous, predicted_current] -= 1
        
    for i in range(1, len(gold) - 1):
        gold_state = gold[i]
        predicted_state = predicted[i]
        word = sentence_words[i-1]
        
        if (word, gold_state) != (word, predicted_state):
            if (word, gold_state) in e:
                e[word, gold_state] += 1

            if (word, predicted_state) in e:
                e[word, predicted_state] -= 1
    
    #Update q_back
    for i in range(0, len(gold)-2):
        gold_previous = gold[i+1]
        gold_current = gold[i]
        predicted_previous = predicted[i+1]
        predicted_current = predicted[i]
        
        if (gold_previous, gold_current) != (predicted_previous, predicted_current):
            q_back[gold_previous, gold_current] += 1
            q_back[predicted_previous, predicted_current] -= 1

    return

def sum_param(e, q, q_back):
    for i in q_sum:
        q_sum[i] = q_sum[i] + q[i]
    for i in e_sum:
        e_sum[i] = e_sum[i] + e[i]
    for i in q_back_sum:
        q_back_sum[i] = q_back_sum[i] + q_back[i]

def smoothed_sentence_just_words(sent_pair):
    smoothed_sentence_words = []
    for i in sent_pair:
        splittt = i.split(' ')
        smoothed_sentence_words.append(splittt[0])
    return smoothed_sentence_words  

def test_parameters(iteration, results_path):
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

    final = []
    for sen in biglist:
        scores, path = viterbi_log(lab,e_avg,q_avg,sen, q_back_avg)

        for i in path:
            if i != '***START***':
                final.append(i)

    f = open(results_path ,"w+", encoding="utf8")
    for i in range(len(final)):
        if final[i] != '***STOP***':
            f.write(test[i]+' '+final[i]+'\n')
        else:
            f.write('\n')
            
    f.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='01.112 Project Part 5')
    parser.add_argument('-d', '--dataset', type=str, choices=["EN", "AL"], required=True)
    parser.add_argument('-t', '--test_set', type=str, choices=["y", "n"], required=True)
    parser.add_argument('-k', '--k_value', type=int, default=3)
    parser.add_argument('-i', '--iterations', type=int, default=3)

    args = parser.parse_args()

    dataset_choice = args.dataset
    test_set = args.test_set
    k_value = args.k_value
    iterations = args.iterations
    if test_set == 'n': #Validation results
        results_path = "datasets/"+ args.dataset +"/dev.p5.out"
    else:#Testing results
        results_path = "datasets/"+ args.dataset +"/test.p5.out"

    #get lines of training data
    r1 =  open("datasets/" + dataset_choice + "/train","r",encoding='utf-8')
    lines1 = r1.readlines()
    r1.close()

    #get lines of test data
    if test_set == 'n': #Validation set
        r2 =  open("datasets/" + dataset_choice + "/dev.in","r",encoding='utf-8')
    else: #Testing set 
        r2 =  open("datasets/" + dataset_choice + "/test.in","r",encoding='utf-8')

    lines2 = r2.readlines()
    r2.close()

    #smooth the data
    train, test = smoothEmission(k_value, lines1, lines2)

    #clean data
    x = train
    for i in range(len(x)):
        if x[i] != '\n':
            x[i]= x[i].rstrip('\n')

    #get emission, transitions and states
    e = emission(train)
    labels, q = transition("datasets/" + dataset_choice + "/train")

    #necessary q, e parameters
    for i in q:
        q[i]=0
    for i in e:
        e[i]=0
    q_sum = copy.deepcopy(q)
    e_sum = copy.deepcopy(e)
    q_avg = copy.deepcopy(q)
    e_avg = copy.deepcopy(e)

    q_back = copy.deepcopy(q)
    q_back_sum = copy.deepcopy(q)
    q_back_avg = copy.deepcopy(q)

    lab = copy.deepcopy(labels)
    lab.remove('***START***')
    lab.remove('***STOP***')

    ### training ##
    train_file = open("datasets/" + dataset_choice + "/train", 'r', encoding='utf-8')
    Ygold = ['***START***']

    all_Ygold = []
    for obs in train_file:
        try:
            obs, v = obs.split()
            obs = obs.strip()
        #     obs = preprocess(obs)
            v = v.strip()
        #     X.append(obs)
            Ygold.append(v)
            
        except:
            # meaning the end of a sentence: x->STOP
            Ygold.extend(['***STOP***'])
            all_Ygold.append(Ygold)
            #reset
            Ygold = ['***START***']

    print (len(all_Ygold))

    smoothed_sentences = []
    temp = []
    for i in range(len(train)):
        if train[i] != '\n':
            train[i]= train[i].rstrip('\n')
            
    for j in train:
        if j != "\n":
            temp.append(j)
        else:
            smoothed_sentences.append(temp)
            temp = []

    for i in range(iterations):
        for sentence_pair in zip(smoothed_sentences, all_Ygold): 
            
            scores, path = viterbi_log(lab,e,q,sentence_pair[0], q_back) #Predicted path
            
            predicted_Y = path
            goldtruth_Y = sentence_pair[1]
            smoothed_sentence_words = smoothed_sentence_just_words(sentence_pair[0])
            assert len(predicted_Y) == len(goldtruth_Y) == (len(smoothed_sentence_words)+2)
            if predicted_Y != goldtruth_Y:
                perceptropUpdate(goldtruth_Y, predicted_Y, smoothed_sentence_words, e, q, q_back)
                sum_param(e, q, q_back)

    #average the parameters
    denominator = iterations*len(all_Ygold) 
    for i in q_avg:
        q_avg[i] = q_sum[i]/denominator
        q_back_avg[i] = q_back_sum[i]/denominator

    for i in e_avg:
        e_avg[i] = e_sum[i]/denominator

    test_parameters(iterations, results_path)

