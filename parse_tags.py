import json
import sys
import collections

# Read input from stdin

items = []
for line in sys.stdin.readlines():
    items.append(json.loads(line))
# Splitting the input data into individual JSON objects

for item in items:
    item["children"] = []
    if "scope" in item:
        item["scope"] = item["scope"].split(".")
    else:
        item["scope"] = []

for i, item in enumerate(items):
    if item["scope"]:
        last_item = item["scope"][-1]
        last_item_index = i - 1
        while last_item_index >= 0:
            last = items[last_item_index]
            if last["name"] == last_item and len(last["scope"]) != len(item["scope"]):
                break
            last_item_index -= 1
        
        items[last_item_index]["children"].append(item)

print(json.dumps([ item for item in items if not item["scope"] ]))
