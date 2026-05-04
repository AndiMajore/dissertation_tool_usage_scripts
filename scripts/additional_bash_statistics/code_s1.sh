#!/usr/bin/env bash
grep "/standalone" ../logs/drugstone/website-access.log | awk '{print $1}' | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" | sort -u > ../results/all_standalone.ips
grep "drugstone.js" ../logs/drugstone/cdn-access.log | grep -viE '^-$|facebook|google|bing|yahoo|baidu|chatgpt|petal|perplexity|bit\.ly|:8080|bot|spider|crawl|scraper|headless|curl|wget|python|urllib|http-client|facebookexternalhit|turnitin|yandex|archive|Semrush|Ahrefs|DotBot|MJ12bot|SiteExploration' | awk '{print $1}' | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" | sort -u > ../results/all_plugin_loads.ips
comm -23 ../results/all_standalone.ips ../results/all_plugin_loads.ips > ../results/fake_bot.ips
