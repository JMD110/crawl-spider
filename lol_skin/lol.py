import json
import os
import re

import pymongo
import requests

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)" \
             " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"
FEED_URL = "http://lol.qq.com/biz/hero/champion.js"  # 在官网找到的js文件地址对应到所有英雄与英雄ID
FILE_PATH = r"./lol/"  # 将皮肤保存在lol文件夹内
client = pymongo.MongoClient(host='127.0.0.1', port=27017)  # 连接Mongodb
db = client.lol


# 拿到所有英雄的名称以及ID 创建保存的文件夹
def get_heros():
    resp = requests.get(FEED_URL, {'user_agent': USER_AGENT}).content
    resp_js = resp.decode()
    pattern = re.compile('"keys":(.*?),"data"')
    hero_dict = json.loads(pattern.findall(resp_js)[0])
    for key, value in hero_dict.items():
        hero_file = FILE_PATH + value
        try:
            # 为每个英雄建立一个文件夹保存皮肤
            os.mkdir(hero_file)
        except Exception as e:
            print(e)

    return hero_dict


# 拿到对应英雄的全部皮肤
def get_skins(hero_dict):
    for hero_id, hero_name in hero_dict.items():
        hero_skin_list = []
        # 皮肤最多的英雄是安妮查了一下11个皮肤 预计暂时也不会有超过15个皮肤的
        for skin_id in range(15):

            try:
                skin_url = "http://ossweb-img.qq.com/images/lol/web201310/skin/big%s0%02d.jpg" % (hero_id, skin_id)
                skin = requests.get(skin_url, {'user_agent': USER_AGENT})
                file_name = os.path.join(FILE_PATH, hero_name, '%d.jpg' % skin_id)
                if skin.status_code == 200:
                    # 保存图片
                    with open(file_name, 'wb') as f:
                        f.write(skin.content)
                        print('downloading:%s' % file_name)
                        f.close()
                    hero_skin_list.append(skin_url)
            except Exception as e:
                print(e)
        # 保存到数据库
        db['skins'].insert_one({'hero_id': hero_id, 'hero_name': hero_name, 'url': hero_skin_list})


def main():
    hero_dict = get_heros()
    get_skins(hero_dict)
    print('Finish....')


if __name__ == '__main__':
    main()
