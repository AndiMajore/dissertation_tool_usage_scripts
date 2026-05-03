import os, sys

BASE_DIR = "../logs/"
exclusion_command = "grep -viE '^-$|facebook|google|bing|yahoo|baidu|chatgpt|petal|perplexity|bit\\.ly|:8080|bot|spider|crawl|scraper|headless|curl|wget|python|urllib|http-client|facebookexternalhit|turnitin|yandex|archive|Semrush|Ahrefs|DotBot|MJ12bot|SiteExploration'"

print("create fake_bot.ips")
os.system("bash ./additional_bash_statistics/code_s1.sh")


ip_filter_command = "grep -v -F -f ../results/fake_bot.ips"

toolnames = set()
for file in os.listdir(BASE_DIR):
    for app in os.listdir(BASE_DIR+file):
        app_name = app.replace("-access.log","")
        toolnames.add(f"{file}/{app_name}")

for toolname in toolnames:
    file_path = BASE_DIR+toolname+"-access.log"
    out_file = BASE_DIR+toolname+"-access-filtered.log"
    print(f"Processing {file_path}")
    os.system(f"{exclusion_command} {file_path} | {ip_filter_command}> {out_file}")