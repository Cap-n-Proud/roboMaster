import json

with open("status.json") as f:
    data = json.load(f)

a = [2, 3, 4]
print(len(a))
# print(data["tower01"][2]["pods"][1])
# print(data["tower01"][2]["level"])
print("Number of towers: ", len(data))
# ["level"][0]["pods"][2])
# Iterates the towers presnet in teh configuration
for tower in data:
    # Prints how many levels each tower has
    print("TOWER: ", tower, "LEVELS: ", len(data[tower]))
    print("------------------------")

    # Prints all the pods in each level
    for level in data[tower]:
        print("------------------------")
        print("LEVEL: ", level["level"])
        # print(level)
        for pod in level["pods"]:
            print("PLANTS:", pod["plantName"], pod["podID"])
            # print(pod)
            # print(pod[0]["plantName"])
