import json

programFile = "programs.json"
def getProg():
    with open(programFile) as f:
      data = json.load(f)
    return data


def saveProgr(programs):
    with open(programFile, 'w') as f:
        json.dump(programs, f)

programs = getProg()

#print(programs[1])

R = 98
newP = {
"progName": "default3",
"pumpFreq": 60,
"pumpTime": 5,
"lightBrightness": 80,
"R": R,
"G": 100,
"B": 210
}


newP2 = {
"progName": "default3",
"pumpFreq": 60,
"pumpTime": 5,
"lightBrightness": 80,
"R": 10,
"G": 100,
"B": 210
}
newProgram = json.dumps(newP)
#print(newProgram)
print(len(programs))

programs.append(newP)
# list(newP2).append(programs)

print("-----------------------------")
print(programs)

# print("-----------------------------")
# print(programs[1])
# del programs[1]
# print("-----------------------------")
# print(programs)

saveProgr(programs)
