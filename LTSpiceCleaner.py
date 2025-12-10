import os
import time

def Clean():
    time.sleep(1)
    suxs=[]
    for path in os.listdir():
        if "circuit" in path:
            sux=path.split("circuit")[1].split(".")[0]
            if not sux in suxs: suxs.append(sux)
    circuits=["circuit"+sux+".asc" for sux in suxs]

    for circuit in circuits:
        circuitName=circuit.split(".")[0]
        sufixes=[".raw",".op.raw",".net",".log",".fail"]
        deletionPaths=[]
        for sufix in sufixes:
            deletionPaths.append(circuitName+sufix)

        for path in deletionPaths:
            if os.path.exists(path):
                os.remove(path)
    time.sleep(1)

if __name__ == "__main__":
    Clean()