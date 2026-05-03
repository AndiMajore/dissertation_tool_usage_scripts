import os, sys

def count_lines(file):
    return sum(1 for _ in open(file))

def run_s2(in_file, out_file):
    os.system(f"bash ./additional_bash_statistics/code_s2.sh {in_file} {out_file}")

def run_s3(in_file):
    os.system(f"bash ./additional_bash_statistics/code_s3.sh {in_file}")

def run_s4(in_file):
    os.system(f"bash ./additional_bash_statistics/code_s4.sh {in_file}")

def run_s5(in_file):
    os.system(f"bash ./additional_bash_statistics/code_s5.sh {in_file}")

def run_s6(in_file, without_file):
    os.system(f"bash ./additional_bash_statistics/code_s6.sh {in_file} {without_file}")

def run_s7(in_file):
    os.system(f"bash ./additional_bash_statistics/code_s7.sh {in_file}")

def run_s8(in_file, out_file):
    os.system(f"bash ./additional_bash_statistics/code_s8.sh {in_file} {out_file}")


run_s2("../logs/nedrex-web/website-access-filtered.log", "../results/nedrex-web_website_unique.ips")
print(f"NeDRex-Web - Website - Unique IPs: \n{count_lines('../results/nedrex-web_website_unique.ips')}")

run_s2("../logs/drugstone/website-access-filtered.log", "../results/drugstone_website_unique.ips")
print(f"Drugst.One - Website - Unique IPs: \n{count_lines('../results/drugstone_website_unique.ips')}")

run_s8("../logs/drugstone/cdn-access-filtered.log", "../results/drugstone_plugin_unique.ips")
print(f"Drugst.One - Plugin - Unique IPs: \n{count_lines('../results/drugstone_plugin_unique.ips')}")

os.system("cat ../results/drugstone_website_unique.ips ../results/drugstone_plugin_unique.ips | sort -u > ../results/drugstone_website_plus_plugin_unique.ips")
print(f"Drugst.One - Website+Plugin - Unique IPs: \n{count_lines('../results/drugstone_website_plus_plugin_unique.ips')}")

print(f"Drugst.One - Standalone - Referrals:")
run_s4("../logs/drugstone/website-access-filtered.log")

print(f"Drugst.One - Standalone - Unique Referrers:")
run_s5("../logs/drugstone/website-access-filtered.log")

print(f"Drugst.One - Plugin only (not through website):")
run_s6("../results/drugstone_plugin_unique.ips", "../results/drugstone_website_unique.ips")

print(f"Drugst.One - Plugin - Unique Integrator URLs:")
run_s7("../logs/drugstone/cdn-access-filtered.log")

run_s2("../logs/digest/website-access-filtered.log", "../results/digest_website_unique.ips")
print(f"DIGEST - Website - Unique IPs: \n{count_lines('../results/digest_website_unique.ips')}")

run_s2("../logs/digest/api-access-filtered.log", "../results/digest_api_unique.ips")
print(f"DIGEST - API - Unique IPs: \n{count_lines('../results/digest_api_unique.ips')}")

print(f"DIGEST - API only (not through website):")
run_s6("../results/digest_api_unique.ips", "../results/digest_website_unique.ips")

run_s2("../logs/epistasis-disease-atlas/website-access-filtered.log", "../results/epistasis-disease-atlas_website_unique.ips")
print(f"Epistasis-Disease-Atlas - Website - Unique IPs: \n{count_lines('../results/epistasis-disease-atlas_website_unique.ips')}")
