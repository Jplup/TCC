import json

def copy(thing):
    if type(thing)==type({}):
        dictCopy={}
        for key in thing.keys():
            dictCopy[key]=copy(thing[key])
        return dictCopy
    elif type(thing)==type([]):
        return [copy(item) for item in thing]
    else: return thing

numThousends=3

for N in [1,2,3]:
    pathPrefix="LTSpiceSimResults/fullN"+str(N)+"_3_"

    datas=[]
    for i in range(numThousends):
        with open(pathPrefix+str(i+2)+".json") as fs: data=json.load(fs)
        datas.append(data)

    soma=copy(datas[0])

    for key in datas[0].keys():
        vals=datas[0][key]
        #print(vals)
        for resultKey in datas[0][key][0].keys():
            if "V(" in resultKey:
                val=0
                for n in range(numThousends):
                    val+=datas[n][key][0][resultKey]
                soma[key][0][resultKey]=val/numThousends

    for key in datas[0].keys():
        vals=datas[0][key]
        #print(vals)
        for resultKey in datas[0][key][0].keys():
            if resultKey=="SNR":
                for SNRkey in datas[0][key][0][resultKey].keys():
                    val=0
                    for n in range(numThousends):
                        val+=datas[n][key][0][resultKey][SNRkey]
                    soma[key][0][resultKey][SNRkey]=val/numThousends


    with open("LTSpiceSimResults/fullN3_"+str(N)+"000.json",'w') as fs: json.dump(soma,fs)




