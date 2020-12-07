# import requests
#
# re = requests.get('http://10.177.74.168/api/v4/projects?private_token=Kw2zKrSejzSyDjkHBAFR')
# print(re.text)
# import random
#
# s = [1,2,3,4,5,6]
# n=random.randint(0, len(s))
# print(type(n))
import redis
import json

pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
# req = redis.StrictRedis(connection_pool=pool)
wahaha = redis.StrictRedis(connection_pool=pool)


# json文件发送形式
Sendjson_txt ='''
{
  "header":{
    "funcNo": "IF010002",
    "opStation": "11.11.1.1",
    "appId": "aaaaaa",
    "deviceId": "kk",
    "ver":"wx-1.0",
    "channel": "4"
  },
  "payload": {
    "mobileTel": "13817120001"
  }
}
'''

print(type((Sendjson_txt)))
date_json = json.loads(Sendjson_txt)
print(type(date_json))
print(date_json)
print("*" * 10)

# 遍历json文件所有的key对应的value
dic = {}


def json_txt(dic_json):
    if isinstance(dic_json, dict):  # 判断是否是字典类型isinstance 返回True false
        for key in dic_json:
            if isinstance(dic_json[key], dict):  # 如果dic_json[key]依旧是字典类型
                print("****key--：%s value--: %s" % (key, dic_json[key]))
                wahaha.set(str(key), str(dic_json[key]))
                json_txt(dic_json[key])
            else:
                print("****key--：%s value--: %s" % (key, dic_json[key]))
                wahaha.set(str(key), str(dic_json[key]))


json_txt(date_json)
print("dic ---: " + str(dic))
for key in wahaha.keys():
    print(key)
    print(wahaha.get(key))

