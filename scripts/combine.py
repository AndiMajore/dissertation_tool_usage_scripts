import os, sys

BASE_DIR="/home/andim/Downloads/apache_log_archives/"

order=["old", "middle", "current"]

print("Combining Log archives and current log...")
for log_dir in os.listdir(BASE_DIR+"old/"):
    new_dir = "../logs/"+log_dir
    os.system(f"mkdir -p {new_dir}")
    log_dir_path = BASE_DIR+"old/"+log_dir
    for file in os.listdir(log_dir_path):
        if "error" in file:
            continue
        if file.endswith(".log"):
            files = [log_dir_path+"/"+file]
            middle_file=BASE_DIR+"middle/"+log_dir+"/"+file
            current_file = BASE_DIR + "current/" + log_dir + "/" + file
            if os.path.exists(middle_file):
                files.append(middle_file)
            if os.path.exists(current_file):
                files.append(current_file)
            command = "cat "
            for f in files:
                command = command + f+" "
            os.system(command+">"+new_dir+"/"+file)

