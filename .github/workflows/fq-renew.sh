#!/bin/bash

url="https://www.dabai.in/link/2DDql9XsQEAdWpB8?sub=3"
fq_list="fq.list"

# 使用curl获取网页内容并进行BASE64解码
decoded_content=$(curl -s "$url" | base64 -d)

# 添加新内容
new_content1="vless://0b6b461b-11cb-4aac-d7f6-bd267cc04bca@cloudflare.yuki.ren:443?encryption=none&security=tls&sni=de.yuki.ren&fp=safari&type=ws&host=de.yuki.ren&path=%2Fbilibili%3Fed%3D2048#DE-FSN-kvm"
new_content2="vless://a281f067-af59-4184-e4f9-e9a0f6d7c9fb@cloudflare.yuki.ren:443?encryption=none&security=tls&sni=us.yuki.ren&fp=safari&type=ws&host=us.yuki.ren&path=%2Fbilibili%3Fed%3D2048#US-CHI-kvm"

# 合并内容
merged_content="$decoded_content\n$new_content1\n$new_content2"

# 对合并后的内容进行BASE64编码
encoded_merged_content=$(echo -n "$merged_content" | base64)

# 将编码后的内容保存到fq.list文件中
echo -e "$encoded_merged_content" > "$fq_list"
