import os

README_PATH = "../README.md"
LOG_PATH = "../run_all.sh.log"

START_MARKER = "<!-- LOG_START -->"
END_MARKER = "<!-- LOG_END -->"

def inject():
    if not os.path.exists(LOG_PATH):
        print(f"Log file {LOG_PATH} not found. Skipping injection.")
        return

    if not os.path.exists(README_PATH):
        print(f"README file {README_PATH} not found.")
        return

    with open(LOG_PATH, "r") as f:
        log_content = f.read()

    with open(README_PATH, "r") as f:
        readme_content = f.read()

    if START_MARKER in readme_content and END_MARKER in readme_content:
        before = readme_content.split(START_MARKER)[0]
        after = readme_content.split(END_MARKER)[1]
        
        new_content = (
            before + 
            START_MARKER + 
            "\n\n```text\n" + 
            log_content.strip() + 
            "\n```\n\n" + 
            END_MARKER + 
            after
        )
        
        with open(README_PATH, "w") as f:
            f.write(new_content)
        print("Successfully injected log into README.md")
    else:
        print("Markers not found in README.md")

if __name__ == "__main__":
    inject()
