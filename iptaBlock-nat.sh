#!/bin/sh

red='\033[0;31m'
plain='\033[0m'

# check root
[[ $EUID -ne 0 ]] && echo -e "${red}错误：${plain} 必须使用root用户运行此脚本！\n" && exit 1



# 清空配置
iptables -P INPUT ACCEPT
iptables -F
iptables -A INPUT -m ttl --ttl-gt 80 -j ACCEPT
iptables -A INPUT -p icmp -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -P INPUT ACCEPT
# 轮子、Fake News
iptables -A OUTPUT -m string --algo kmp --string "falundafa" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "minghui" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "epochtimes" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "ntdtv" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "voachinese" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "appledaily" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "nextdigital" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "dalailama" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "nytimes" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "bloomberg" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "independent" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "freetibet" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "citizenpowerfor" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "rfa.org" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "bbc.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "theinitium.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "tibet.net" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "jw.org" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "bannedbook.org" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "dw.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "storm.mg" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "yam.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "chinadigitaltimes" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "ltn.com.tw" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "mpweekly.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "cup.com.hk" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "thenewslens.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "inside.com.tw" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "everylittled.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "cool3c.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "taketla.zaiko.io" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "news.agentm.tw" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "sportsv.net" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "research.tnlmedia.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "ad2iction.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "viad.com.tw" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "tnlmedia.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "becomingaces.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "pincong.rocks" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "flipboard.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "soundofhope.org" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "wenxuecity.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "aboluowang.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "2047.name" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "shu.best" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "shenyunperformingarts.org" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "bbc.co.uk" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "cirosantilli" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "wsj.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "rfi.fr" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "chinapress.com.my" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "hancel.org" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "miraheze.org" -j DROP
# 容易被利用于欺诈
iptables -A OUTPUT -m string --algo kmp --string "beanfun.com" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "gashpoint.com" -j DROP
# 政府、学校、金融机构
iptables -A OUTPUT -m string --algo kmp --string "gov.cn" -j DROP
iptables -A OUTPUT -m string --algo kmp --string "edu.cn" -j DROP

apt update
apt-get install iptables ipset
echo "----------VmShell提供的服务器审计系统脚本执行完毕----------"
