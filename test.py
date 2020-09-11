options = {
    "1": "mine",
    "2": "gaia",
    "3": "upgrade",
    "4": "federation",
    "5": "research",
    "6": "pq",
    "7": "special",
    "8": "pass_",
    "9": "free"
}

picking_action = True
while picking_action:
    action = input("--> ")
    if action in options.keys():
        picking_action = False
    else:
        print("Please type the action's corresponding number.")
else:
    print(action)


# if __name__ == "__main__":
#     print(distance(12, 11, 4, 11))
