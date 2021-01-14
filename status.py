import json

with open("status.json") as f:
    data = json.load(f)

with open("plants.json") as p:
    plants = json.load(p)
print(plants["plants"][0]["ID"])

print(data["towers"][0]["levels"][3]["pods"][0]["plantName"])

# Iterates the towers presnet in teh configuration

for towers in data:
    print("towers", towers)
    print("Number of towers: ", len(data[towers]))
    for tower in range(0, len(data[towers])):
        # Prints how many levels each tower has
        print(
            "TOWER: ",
            data[towers][tower]["name"],
            "LEVELS: ",
            len(data[towers][tower]["levels"]),
        )
        print("------------------------")
        for pod in data[towers][tower]["levels"]:
            # # Prints all the pods in each level
            print("------------------------")
