import os, sys

BASE_DIR = "../logs/"
exclusion_command = "grep -viE '^-$|facebook|google|bing|yahoo|baidu|chatgpt|petal|perplexity|bit\\.ly|:8080|bot|spider|crawl|scraper|headless|curl|wget|python|urllib|http-client|facebookexternalhit|turnitin|yandex|archive|Semrush|Ahrefs|DotBot|MJ12bot|SiteExploration'"

print("Cleaning logs from some false positive hits...")

print("\tCreating fake_bot.ips list from Drugst.One Standalone access not loading drugstone.js plugin...")
os.system("bash ./additional_bash_statistics/code_s1.sh")
print(f"\tCreated fake_bot.ips list containing {sum(1 for _ in open('../results/fake_bot.ips'))} IPs!")


ip_filter_command = "grep -v -F -f ../results/fake_bot.ips"

toolnames = set()

for file in os.listdir(BASE_DIR):
    for app in os.listdir(BASE_DIR+file):
        app_name = app.replace("-access.log","")
        toolnames.add(f"{file}/{app_name}")

print("\tApply general scraper filter and fake_bot.ips list filter to...")
for toolname in toolnames:
    file_path = BASE_DIR+toolname+"-access.log"
    out_file = BASE_DIR+toolname+"-access-filtered.log"
    print(f"\t\t{file_path}")
    os.system(f"{exclusion_command} {file_path} | {ip_filter_command}> {out_file}")
print("...Done")