import os, sys

def count_lines(file):
    return sum(1 for _ in open(file))

def run_s2(in_file, out_file):
    os.system(f"bash ./additional_bash_statistics/code_s2.sh {in_file} {out_file}")

def run_s3(in_file, out_file):
    os.system(f"bash ./additional_bash_statistics/code_s3.sh {in_file} {out_file}")

def run_s4(in_file, out_file):
    os.system(f"bash ./additional_bash_statistics/code_s4.sh {in_file} {out_file}")

def run_s5(in_file, out_file):
    os.system(f"bash ./additional_bash_statistics/code_s5.sh {in_file} {out_file}")

def run_s6(in_file, without_file, out_file):
    os.system(f"bash ./additional_bash_statistics/code_s6.sh {in_file} {without_file} {out_file}")

def run_s7(in_file, out_file):
    os.system(f"bash ./additional_bash_statistics/code_s7.sh {in_file} {out_file}")

def run_s8(in_file, out_file):
    os.system(f"bash ./additional_bash_statistics/code_s8.sh {in_file} {out_file}")

def run_s9(toolname):
    if toolname == "drugstone":
        os.system(f"bash ./additional_bash_statistics/code_s9_drugstone.sh {toolname}")
    elif toolname == "drugstone-stable":
        os.system(f"bash ./additional_bash_statistics/code_s9_drugstone_stable.sh {toolname}")
    else:
        os.system(f"bash ./additional_bash_statistics/code_s9.sh {toolname}")

print("Creating additional statistics for dissertation...")

run_s2("../logs/nedrex-web/website-access-filtered.log", "../results/nedrex-web_website_unique.ips")
print(f"\tNeDRex-Web - Website - Unique IPs: {count_lines('../results/nedrex-web_website_unique.ips')}")

run_s9("nedrex-web")
print(f"\tNeDRex-Web - All - Unique IPs: {count_lines('../results/nedrex-web_unique.ips')}")

run_s2("../logs/drugstone/website-access-filtered.log", "../results/drugstone_website_unique.ips")
print(f"\tDrugst.One - Website - Unique IPs: {count_lines('../results/drugstone_website_unique.ips')}")

run_s8("../logs/drugstone/cdn-access-filtered.log", "../results/drugstone_plugin_unique.ips")
run_s6("../results/drugstone_plugin_unique.ips", "../results/drugstone_website_unique.ips", "../results/drugstone_plugin_no_website.ips")
print(f"\tDrugst.One - Plugin only (not through website): {count_lines('../results/drugstone_plugin_no_website.ips')}")

os.system("cat ../results/drugstone_website_unique.ips ../results/drugstone_plugin_unique.ips | sort -u > ../results/drugstone_website_plus_plugin_unique.ips")
print(f"\tDrugst.One - Website+Plugin - Unique IPs: {count_lines('../results/drugstone_website_plus_plugin_unique.ips')}")

run_s9("drugstone-stable")
print(f"\tDrugst.One-Stable - All - Unique IPs: {count_lines('../results/drugstone-stable_unique.ips')}")

run_s9("drugstone")
print(f"\tDrugst.One - All (no stable) - Unique IPs: {count_lines('../results/drugstone_unique.ips')}")

os.system("cat ../results/drugstone_unique.ips ../results/drugstone-stable_unique.ips | sort -u > ../results/drugstone_all_unique.ips")
print(f"\tDrugst.One - All - Unique IPs: {count_lines('../results/drugstone_all_unique.ips')}")

run_s3("../logs/drugstone/website-access-filtered.log", "../results/drugstone_standalone_referrers.urls")
print(f"\tDrugst.One - Standalone - Unique Referrers: {count_lines('../results/drugstone_standalone_referrers.urls')}")

run_s5("../logs/drugstone/website-access-filtered.log","../results/drugstone_standalone_referrals.urls")
print(f"\tDrugst.One - Standalone - Uniquely Referred IPs: {count_lines('../results/drugstone_standalone_referrals.urls')}")

run_s4("../logs/drugstone/website-access-filtered.log", "../results/drugstone_standalone_referrals_total.ips")
print(f"\tDrugst.One - Standalone - Referrals: {count_lines('../results/drugstone_standalone_referrals_total.ips')}")

run_s7("../logs/drugstone/cdn-access-filtered.log", '../results/drugstone_plugin_unique_integrator.urls')
print(f"\tDrugst.One - Plugin - Unique Integrator URLs: {count_lines('../results/drugstone_plugin_unique_integrator.urls')}")


print(f"\tDrugst.One - Plugin - Unique IPs: {count_lines('../results/drugstone_plugin_unique.ips')}")

run_s2("../logs/epistasis-disease-atlas/website-access-filtered.log", "../results/epistasis-disease-atlas_website_unique.ips")
print(f"\tEpistasis-Disease-Atlas - Website - Unique IPs: {count_lines('../results/epistasis-disease-atlas_website_unique.ips')}")

run_s9("epistasis-disease-atlas")
print(f"\tEpistasis-Disease-Atlas - All - Unique IPs: {count_lines('../results/epistasis-disease-atlas_unique.ips')}")

run_s2("../logs/digest/website-access-filtered.log", "../results/digest_website_unique.ips")
print(f"\tDIGEST - Website - Unique IPs: {count_lines('../results/digest_website_unique.ips')}")

run_s9("digest")
print(f"\tDIGEST - All - Unique IPs: {count_lines('../results/digest_unique.ips')}")

run_s2("../logs/digest/api-access-filtered.log", "../results/digest_api_unique.ips")
run_s6("../results/digest_api_unique.ips", "../results/digest_website_unique.ips", '../results/digest_api_without_website.ips')
print(f"\tDIGEST - API only (not through website): {count_lines('../results/digest_api_without_website.ips')}")

print(f"\tDIGEST - API - Unique IPs: {count_lines('../results/digest_api_unique.ips')}")

os.system("cat ../results/drugstone_all_unique.ips ../results/epistasis-disease-atlas_unique.ips ../results/digest_unique.ips ../results/nedrex-web_unique.ips | sort -u > ../results/tools_all_unique.ips")
print(f"\tTools - All - Unique IPs: {count_lines('../results/tools_all_unique.ips')}")















