import json
import sys
import collections

# Read input from stdin

items = []
for line in sys.stdin.readlines():
    items.append(json.loads(line))
# Splitting the input data into individual JSON objects

root = {}

for item in items:
    item["children"] = {}
    if "scope" in item:
        item["scope"] = item["scope"].split(".")
    else:
        item["scope"] = []

def find_parent(node, path):
    """Recursively find the parent node based on the given path."""
    if not path:
        return node
    for child in node['children'].values():
        if child['name'] == path[0]:
            return find_parent(child, path[1:])
    return None

# Initialize the root nodes list
tree = []

# Dictionary to quickly find nodes by their name
nodes_dict = {}

# Process each item in the data list
for item in items:
    nodes_dict[item['name']] = item
    if not item['scope']:  # If it's a root node
        tree.append(item)
        item['children'] = {}
    else:  # If it's a child node
        parent = find_parent({'children': nodes_dict}, item['scope'])
        if parent:
            parent['children'][item['name']] = item
            item['children'] = {}

print(json.dumps(tree, indent=4))