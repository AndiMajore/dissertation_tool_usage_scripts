import os, sys
BASE_DIR="../logs/apps/"

import tomli as tomllib  # Built-in for Python 3.11+. If using < 3.11, `pip install tomli` and `import tomli as tomllib`

# Note: tomllib requires reading the file in binary mode ("rb")
with open("../config.toml", "rb") as f:
    config = tomllib.load(f)

# Recreate your exact dictionaries
toolname_map = config["toolname_map"]
toolnames = config["toolnames"]
exclude = config["exclude"]


fhs = {}

def get_fh(t):
    if t in fhs:
        return fhs[t]
    else:
        file_name = BASE_DIR+t+"-access.log"
        fh = open(file_name, "w")
        fhs[t] = fh
        return fh

def close_all_fhs():
    for t in fhs:
        fhs[t].close()

with open(f"{BASE_DIR}access.log") as f:
    for line in f.readlines():
        l= line.split(" ")
        tool_name = l[6]
        if tool_name == "/":
            continue
        if tool_name[0] == "/":
            tool_name = tool_name[1:]
        if "/" in tool_name:
            idx = tool_name.index("/")
            if idx > -1:
                tool_name = tool_name[:idx]
        if "?" in tool_name:
            idx = tool_name.index("?")
            if idx > -1:
                tool_name = tool_name[:idx]
        if tool_name not in toolname_map:
            continue
        toolname = toolname_map[tool_name]
        fh = get_fh(toolname)
        fh.write(line)
    close_all_fhs()


for tool in toolnames:
    os.system(f"mv ../logs/{tool} ../logs/{toolnames[tool]}")

for tool in exclude:
    os.system(f"rm -rf ../logs/{tool}")