from icecream import ic
from engine import RPGCardEngine


engine = RPGCardEngine(config_source="./data/scenario.json")

command = ""

while command != "bye":
    command = input()
    #ic("You entered",command)
    result = engine.do_action_by_text(command)
    print(result.result_to_text())