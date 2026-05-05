import os, sys
import tomli as tomllib

# Load configuration
with open("../config.toml", "rb") as f:
    config = tomllib.load(f)

BASE_DIR = config.get("archive_source_dir", "../log_archives/")

order=["old", "middle", "current"]

print("Combining Log archives and current log...")
if not os.path.exists(BASE_DIR):
    print(f"Error: Archive source directory '{BASE_DIR}' does not exist.")
    sys.exit(1)

for log_dir in os.listdir(os.path.join(BASE_DIR, "old")):
    new_dir = os.path.join("..", "logs", log_dir)
    os.makedirs(new_dir, exist_ok=True)
    log_dir_path = os.path.join(BASE_DIR, "old", log_dir)
    for file in os.listdir(log_dir_path):
        if "error" in file:
            continue
        if file.endswith(".log"):
            files = [os.path.join(log_dir_path, file)]
            middle_file = os.path.join(BASE_DIR, "middle", log_dir, file)
            current_file = os.path.join(BASE_DIR, "current", log_dir, file)
            if os.path.exists(middle_file):
                files.append(middle_file)
            if os.path.exists(current_file):
                files.append(current_file)
            command = "cat " + " ".join(files) + " > " + os.path.join(new_dir, file)
            os.system(command)

