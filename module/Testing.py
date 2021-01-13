import random
import requests
import redis
from rest_framework.utils import json
from module.dep_analysis import get_dep_info
from module.parse import parse
import os.path




# 获取依赖测试graph
my_path = os.path.abspath(os.path.dirname(__file__))
api_info_list = parse(os.path.join(my_path, "../openapi/openapi.yaml"), 1.0)
matrix, weight_info_list = get_dep_info(api_info_list)
graph = matrix.tolist()
print(graph)
print(len(graph))

# 连接redis-pool
pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
# req = redis.StrictRedis(connection_pool=pool)
resp = redis.StrictRedis(connection_pool=pool)

post = redis.StrictRedis(connection_pool=pool)
post.lpush('api_id_p', '')
delete = redis.StrictRedis(connection_pool=pool)
delete.lpush('api_id_d', '')


#################################     模糊处理    ####################################
def fuzz(type):
    if 'integer' == type:
        return 1  # 这里是project Id
    elif 'string' == type:
        return "master"

########################   遍历json文件所有的key以及对应的value  ######################

def json_txt(dic_json):
    if isinstance(dic_json, list):
        for dic in dic_json:
            if isinstance(dic, dict):  # 判断是否是字典类型isinstance 返回True false
                for key in dic:
                    if isinstance(dic[key], dict):  # 如果dic_json[key]依旧是字典类型
                        json_txt(dic[key])
                        resp.lpush(str(key), str(dic[key]))
                    else:
                        resp.lpush(str(key), str(dic[key]))
    else:
        if isinstance(dic_json, dict):  # 判断是否是字典类型isinstance 返回True false
            for key in dic_json:
                if isinstance(dic_json[key], dict):  # 如果dic_json[key]依旧是字典类型
                    json_txt(dic_json[key])
                    resp.lpush(str(key), str(dic_json[key]))
                else:
                    resp.lpush(str(key), str(dic_json[key]))

################################    测试    ########################################
# 记录拓扑排序顺序
topology_order = []
# 记录出度为0的点
out_degree_zero = []
# 设计出度为0的点
end = []
# 创建遍历的存储队列
queue = []

# 直接测试函数,(x,y)为graph中对应api节点
def test(x):
    api_info = api_info_list[x]
    url = api_info.path
    method = api_info.http_method
    data = ''
    # 用redis记录post和delete的id
    if method == 'post':
        for i in range(2):
            url = api_info.path
            data = []
            for field_info in api_info.req_param:
                if field_info.require:
                    flag = '0'
                    location = field_info.location
                    if resp.llen(str(field_info.field_name)) != 0:
                        listl = []
                        for i in range(resp.llen(str(field_info.field_name))): listl.append(i + 1)
                        index = random.choice(listl)
                        valu = resp.lindex(str(field_info.field_name),
                                           random.choice(str(index)))  # 从response的redis中根据name取对应value
                        value = str(valu, encoding="utf-8")
                        if field_info.data_type == str:
                            continue
                        elif field_info.data_type == bytes:
                            pass
                    else:
                        value = None
                    if field_info.field_name == 'user_id':
                        value = 4
                    if field_info.fuzz:
                        # fuzz处理
                        continue
                    # 不同的in对应不同的数据   location：0-path,1-query,2-header,3-body
                    if location == 0:
                        url = url.replace('{' + field_info.field_name + '}', str(value))
                    elif location == 1:
                        # url追加key1=value1&key2=value2到url后,即查询字符串
                        if flag == 0:
                            flag = 1
                            url = url + "?" + str(field_info.field_name) + "=" + str(value)
                        else:
                            url = url + "&" + str(field_info.field_name) + "=" + str(value)
                    elif location == 2:
                        pass
                        # 操作
                    elif location == 3:
                        # 参数组成json字符串 ==> data
                        data.append(value)
                        pass
            post.lpush('api_id_p', api_info.api_id)

            if '?' in url:
                # 配置token
                url = url + "&private_token=Kw2zKrSejzSyDjkHBAFR"
            else:
                url = url + "?private_token=Kw2zKrSejzSyDjkHBAFR"
            # 请求API
            print("exec " + str(api_info.api_id) + " " + method + " " + url)
            response = requests.post(url, data).text
            repon = str(response)
            if len(repon) > 0:
                reponses = json.loads(repon)
                json_txt(reponses)
            else:
                pass
            print(response)
    elif method == 'delete':
        for field_info in api_info.req_param:
            if field_info.require:
                flag = '0'
                location = field_info.location
                if resp.llen(str(field_info.field_name)) != 0:
                    listl = []
                    for i in range(resp.llen(str(field_info.field_name))): listl.append(i + 1)
                    index = random.choice(listl)
                    valu = resp.lindex(str(field_info.field_name),
                                       random.choice(str(index)))  # 从response的redis中根据name取对应value
                    value = str(valu, encoding="utf-8")
                else:
                    value = None
                if field_info.field_name == 'user_id':
                    value = 4
                if field_info.fuzz:
                    # fuzz处理
                    continue
                # 不同的in对应不同的数据   location：0-path,1-query,2-header,3-body
                if location == 0:
                    url = url.replace('{' + field_info.field_name + '}', str(value))
                elif location == 1:
                    # url追加key1=value1&key2=value2到url后,即查询字符串
                    if flag == 0:
                        flag = 1
                        url = url + "?" + str(field_info.field_name) + "=" + str(value)
                    else:
                        url = url + "&" + str(field_info.field_name) + "=" + str(value)
                elif location == 2:
                    # 操作
                    pass
                elif location == 3:
                    # 参数组成json字符串 ==> data
                    data.append(value)
                    pass
        post.lrem('api_id_p', api_info.api_id, 0)

        if '?' in url:
            # 配置token
            url = url + "&private_token=Kw2zKrSejzSyDjkHBAFR"
        else:
            url = url + "?private_token=Kw2zKrSejzSyDjkHBAFR"
        # 请求API
        print("exec " + str(api_info.api_id) + " " + method + " " + url)
        response = requests.delete(url).text
        repon = str(response)
        if len(repon) > 0:
            reponses = json.loads(repon)
            json_txt(reponses)
        else:
            pass
        print(response)
    else:
        for field_info in api_info.req_param:
            if field_info.require:
                flag = '0'
                location = field_info.location
                if resp.llen(str(field_info.field_name)) != 0:
                    listl = []
                    for i in range(resp.llen(str(field_info.field_name))): listl.append(i + 1)
                    index = random.choice(listl)
                    value = resp.lindex(str(field_info.field_name),
                                        random.choice(str(index)))  # 从response的redis中根据name取对应value
                    if type(value) == bytes:
                        value = str(value, encoding="utf-8")
                else:
                    value = None
                if field_info.field_name == 'user_id':
                    value = 4
                if field_info.fuzz:
                    # fuzz处理
                    continue
                # 不同的in对应不同的数据   location：0-path,1-query,2-header,3-body
                if location == 0:
                    url = url.replace('{' + field_info.field_name + '}', str(value))
                elif location == 1:
                    # url追加key1=value1&key2=value2到url后,即查询字符串
                    if flag == 0:
                        flag = 1
                        url = url + "?" + str(field_info.field_name) + "=" + str(value)
                    else:
                        url = url + "&" + str(field_info.field_name) + "=" + str(value)
                elif location == 2:
                    # 操作
                    pass
                elif location == 3:
                    # 参数组成json字符串 ==> data
                    data.append(value)
                    pass

        if '?' in url:
            # 配置token
            url = url + "&private_token=Kw2zKrSejzSyDjkHBAFR"
        else:
            url = url + "?private_token=Kw2zKrSejzSyDjkHBAFR"
        # 请求API
        print("exec " + str(api_info.api_id) + " " + method + " " + url)
        if method == 'get':
            response = requests.get(url, data).text
        elif method == 'put':
            response = requests.put(url).text
        elif method == 'patch':
            response = requests.put(url).text
        repon = str(response)
        if len(repon) > 0:
            reponses = json.loads(repon)
            json_txt(reponses)
        else:
            pass
        print(response)



# fuzz处理graph（x，y）位置的api
def fuzzgraph(x):
    api_info = api_info_list[x]
    url = api_info.path
    method = api_info.http_method
    data = ''
    # 用redis记录post和delete的id
    if method == 'post':
        for i in range(2):
            url = api_info.path
            for field_info in api_info.req_param:
                if field_info.require:
                    flag = '0'
                    location = field_info.location
                    field_type = field_info.field_type
                    value = fuzz(field_type)
                    # 不同的in对应不同的数据   location：0-path,1-query,2-header,3-body
                    if location == 0:
                        url = url.replace('{' + field_info.field_name + '}', str(value))
                    elif location == 1:
                        # url追加key1=value1&key2=value2到url后,即查询字符串
                        if flag == 0:
                            flag = 1
                            url = url + "?" + str(field_info.field_name) + "=" + str(value)
                        else:
                            url = url + "&" + str(field_info.field_name) + "=" + str(value)
                    elif location == 2:
                        # 操作
                        pass
                    elif location == 3:
                        # 参数组成json字符串 ==> data
                        data = [].append(value)
                        pass
            post.lpush('api_id_p', api_info.api_id)

            if '?' in url:
                # 配置token
                url = url + "&private_token=Kw2zKrSejzSyDjkHBAFR"
            else:
                url = url + "?private_token=Kw2zKrSejzSyDjkHBAFR"
            # 请求API
            print("exec " + str(api_info.api_id) + " " + method + " " + url)
            response = requests.post(url, data).text
            repon = str(response)
            if len(repon) > 0:
                reponses = json.loads(repon)
                json_txt(reponses)
            else:
                pass
            print(response)
    elif method == 'delete':
        for field_info in api_info.req_param:
            if field_info.require:
                flag = '0'
                location = field_info.location
                field_type = field_info.field_type
                value = fuzz(field_type)
                # 不同的in对应不同的数据   location：0-path,1-query,2-header,3-body
                if location == 0:
                    url = url.replace('{' + field_info.field_name + '}', str(value))
                elif location == 1:
                    # url追加key1=value1&key2=value2到url后,即查询字符串
                    if flag == 0:
                        flag = 1
                        url = url + "?" + str(field_info.field_name) + "=" + str(value)
                    else:
                        url = url + "&" + str(field_info.field_name) + "=" + str(value)
                elif location == 2:
                    # 操作
                    pass
                elif location == 3:
                    # 参数组成json字符串 ==> data
                    data = [].append(value)
                    pass
        post.lrem('api_id_p', api_info.api_id, 0)

        if '?' in url:
            # 配置token
            url = url + "&private_token=Kw2zKrSejzSyDjkHBAFR"
        else:
            url = url + "?private_token=Kw2zKrSejzSyDjkHBAFR"
        # 请求API
        print("exec " + str(api_info.api_id) + " " + method + " " + url)
        response = requests.delete(url).text
        repon = str(response)
        if len(repon) > 0:
            reponses = json.loads(repon)
            json_txt(reponses)
        else:
            pass
        print(response)
    else:
        for field_info in api_info.req_param:
            if field_info.require:
                flag = '0'
                location = field_info.location
                field_type = field_info.field_type
                value = fuzz(field_type)
                # 不同的in对应不同的数据   location：0-path,1-query,2-header,3-body
                if location == 0:
                    url = url.replace('{' + field_info.field_name + '}', str(value))
                elif location == 1:
                    # url追加key1=value1&key2=value2到url后,即查询字符串
                    if flag == 0:
                        flag = 1
                        url = url + "?" + str(field_info.field_name) + "=" + str(value)
                    else:
                        url = url + "&" + str(field_info.field_name) + "=" + str(value)
                elif location == 2:
                    # 操作
                    pass
                elif location == 3:
                    # 参数组成json字符串 ==> data
                    data = [].append(value)
                    pass

        if '?' in url:
            # 配置token
            url = url + "&private_token=Kw2zKrSejzSyDjkHBAFR"
        else:
            url = url + "?private_token=Kw2zKrSejzSyDjkHBAFR"
        # 请求API
        print("exec " + str(api_info.api_id) + " " + method + " " + url)
        if method == 'get':
            response = requests.get(url, data).text
        elif method == 'put':
            response = requests.put(url).text
        elif method == 'patch':
            response = requests.put(url).text
        repon = str(response)
        if len(repon) > 0:
            reponses = json.loads(repon)
            json_txt(reponses)
        else:
            pass
        print(response)

def topology_visit(g, n):
    for i in range(len(g)):
        if g[i][n] != -1:
            queue.append(i)
    for j in queue:
        g[j][n] = -1
        if g[j] == end:
            i = queue.index(j)
            i = i+1
            for k in range(i,len(queue)):   # 将可测试的api节点后面所有已存储在queue里面的节点在对应graph上的值变为-1
                z = queue[k]
                g[z][n] = -1
            test(j)
            queue.clear()
            topology_visit(g, j)

    if len(queue) !=0: # 说明queue里面所有api都无法test,并且资源池中也没有资源
        k = random.choice(queue)
        fuzzgraph(k)
        topology_visit(g, k)



def traversal(graph):
    for i in range(len(graph)):
        end.append(-1)
    # 收集出度为0的点的集合,即无依赖节点的集合
    for j in range(len(graph)):
        if graph[j] == end:
            out_degree_zero.append(j)

    for m in range(len(out_degree_zero)):
        k = random.choice(out_degree_zero)
        out_degree_zero.remove(k)
        topology_visit(graph, k)

    return topology_order


traversal(graph)
