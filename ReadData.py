import matplotlib.pyplot as plt

def readFile(path,isInput=False):
    with open(path) as fs: lines=fs.readlines()
    if isInput:
        time=[]
        amp=[]
        for line in lines:
            #print("Line:",line)
            #print("lineSplit",line.split("\t"))
            splitedLine=line.split("\t")
            #input()
            
            '''print("Splited 1:",float(splitedLine[0]))
            print("Splited 2 str:",(splitedLine[1].split("\n")[0]))
            print("Splited 2:",float(splitedLine[1].split("\n")[0]))
            input()'''
            time.append(float(splitedLine[0]))
            amp.append(float(splitedLine[1].split("\n")[0]))
        for i in range(len(amp)-2):
            previous=amp[i]
            current=amp[i+1]
            next=amp[i+2]
            if previous==next and not current==previous:
                amp[i+1]=previous
        maxVal=max(amp)
        return time,[val/maxVal for val in amp]
    else:
        keys=lines[0].split("\n")[0].split("\t")
        data={}
        for line in lines[1:]:
            values=line.split("\n")[0].split("\t")
            for key,item in zip(keys,values):
                try:
                    data[key].append(float(item))
                except:
                    data[key]=[float(item)]
        else: return data

def vppm_to_bits(ts,amps,freq=8000):
    T=1/freq
    readIndexes=[]
    readTimes=[]
    gotPoint=False
    periodTimes=[]
    gotPeriodPoint=False

    for i in range(len(ts)):
        if ts[i]%T>0.05*T and ts[i]%T<0.1*T and gotPoint==False:
            gotPoint=True
            readIndexes.append(i)
            readTimes.append(ts[i])
        if ts[i]%T>0.2*T and gotPoint==True:
            gotPoint=False
        if ts[i]%T>0 and ts[i]%T<0.05*T and gotPeriodPoint==False:
            gotPeriodPoint=True
            periodTimes.append(ts[i])
        if ts[i]%T>0.2*T and gotPeriodPoint==True:
            gotPeriodPoint=False

    readAmps=[amps[i] for i in readIndexes]
    amp=max(amps)
    bits=[]
    for a in readAmps:
        if a>amp/2: bits.append(0)
        else: bits.append(1)
    
    return bits