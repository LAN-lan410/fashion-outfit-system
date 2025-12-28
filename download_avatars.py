import requests
import os

# 创建images目录
os.makedirs('static/images', exist_ok=True)

# 一些免费的默认头像URL（请确保符合版权要求）
avatar_urls = [
    'https://img.icons8.com/color/96/000000/circled-user-female-skin-type-1-2.png',
    'https://img.icons8.com/color/96/000000/circled-user-male-skin-type-1-2.png',
    'https://img.icons8.com/color/96/000000/circled-user-female-skin-type-3.png',
    'https://img.icons8.com/color/96/000000/circled-user-male-skin-type-3.png'
]

for i, url in enumerate(avatar_urls, 1):
    try:
        response = requests.get(url)
        with open(f'static/images/avatar{i}.jpg', 'wb') as f:
            f.write(response.content)
        print(f'已下载头像 {i}')
    except Exception as e:
        print(f'下载头像 {i} 失败: {e}')