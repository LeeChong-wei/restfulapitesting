import random

import requests
import redis
from rest_framework.utils import json

from module.traversal import traversal
from module.dep_analysis import get_dep_info
from module.parse import parse
import os.path

# 连接redis-pool
pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
# req = redis.StrictRedis(connection_pool=pool)
resp = redis.StrictRedis(connection_pool=pool)

post = redis.StrictRedis(connection_pool=pool)
api_id_p = []
post.set('api_id_p', api_id_p)
delete = redis.StrictRedis(connection_pool=pool)
api_id_d = []
delete.set('api_id_d', api_id_d)

# 模糊处理
def fuzz(type):
    if 'integer' == type:
        return 1  # 这里是project Id
    elif 'string' == type:
        return "master"


# 测试单元
class testUnit:
    # 初始化数据
    def __init__(self, method, url, data):
        self.method = method
        self.url = url
        self.data = data

    # 执行测试
    def exec(self):
        if '?' in self.url:
            # 配置token
            self.url = self.url + "&private_token=FqJEUnz_MyspF6CrRqaM"
        else:
            self.url = self.url + "?private_token=FqJEUnz_MyspF6CrRqaM"
        # 请求API
        print("exec " + method + " " + self.url)
        if method == 'get':
            return requests.get(self.url, data)
        elif method == 'post':
            return requests.post(self.url, data)
        elif method == 'delete':
            return requests.delete(self.url)
        elif method == 'put':
            return requests.put(self.url, data)
        else:
            print("NOT SUPPORTED " + method)
            return None
        # 错误处理
        # 依赖处理
        pass

# 获取依赖测试顺序
my_path = os.path.abspath(os.path.dirname(__file__))
api_info_list = parse(os.path.join(my_path, "../openapi/project.yaml"), 1.0)
matrix, weight_info_list = get_dep_info(api_info_list)
graph = matrix.tolist()
test_seq = traversal(graph)

######################## 依照测试顺序进行测试 ######################################

# 遍历获得测试api在api_info_list中的index,从而得到api_info
for i in range(0, len(test_seq)):
    test_api_id = test_seq[i]
    api_info = api_info_list[test_api_id]
    url = api_info.path
    method = api_info.http_method
    # 用redis记录post和delete的id
    if method == 'post':
        post.set('api_id_p', api_id_p.append(api_info.api_id))
    elif method == 'delete':
        post.delete('api_id_p', api_id_p.remove(api_info.api_id))
        delete.set('api_id_d', api_id_d.append(api_info.api_id))
    for field_info in api_info.req_param:
        if field_info.require:
            location = field_info.location
            value = resp.get(field_info.field_name)  # 从response的redis中根据name取对应value
            if field_info.fuzz:
                # fuzz处理
                continue
            # 不同的in对应不同的数据   location：0-in,1-query,2-header,3-body
            elif location == '0':
                url = url.replace('{' + field_info.field_name + '}', str(value))
            elif location == '0' and field_info.field_name == 'id' and method == 'delete':
                value_random = random.choice(resp.get(field_info.field_name))  # 注意存储response为id时，以<'id','[01,02,...]'>存储
                url = url.replace('{' + field_info.field_name + '}', str(value_random))
            elif location == '0' and field_info.field_name == 'id' and method == 'get':
                url = url.replace('{' + field_info.field_name + '}',
                                  str(random.choice(resp.get(field_info.field_name))))
            elif location == '1':
                # url追加key1=value1&key2=value2到url后,即查询字符串
                if flag == 0:
                    flag = 1
                    url = url + "?" + str(field_info.field_name) + "=" + str(value)
                else:
                    url = url + "&" + str(field_info.field_name) + "=" + str(value)
            elif location == '2':
                # 操作
                pass
            elif location == '3':
                # 参数组成json字符串 ==> data
                data = [].append(field_info.field_name)
                pass
    unit = testUnit(method, url, data)
    response = unit.exec().text
    reponses = json.loads(response)
    for key in reponses:
        resp.set(key, reponses.get(key))
