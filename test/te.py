import random

from prance import ResolvingParser
import requests
import re
import json

f_p = open("D://pool.txt", "w+")
f_d = open("D://delete.txt", "w+")

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
            return requests.get(self.url)
        elif method == 'post':
            return requests.post(self.url)
        elif method == 'delete':
            return requests.delete(self.url)
        elif method == 'put':
            return requests.put(self.url,'l')
        else:
            print("NOT SUPPORTED " + method)
            return None
        # 错误处理
        # 依赖处理
        pass

project_ids=[]
f = open("D://pool.txt", "w+")

# 解析规范
parser = ResolvingParser("C://Users//litianyu//Desktop//project.yaml")
spec = parser.specification

servers = spec.get("servers")
for server in servers:
    # 获取根路径
    url = server.get("url")
    # 解析API路径的其他部分和参数
    paths = spec.get("paths")
    project_id=''
    for path in paths:
        # completeUrl:根目录加资源路径，但是需要进一步处理
        completeUrl = url[0:len(url)] + path
        methods = paths.get(path)
        for method in methods:
            params = methods.get(method).get("parameters")
            data = ''
            flag = 0
            if params:
                for param in params:
                    # 标识是不是第一次循环,query用来判断是否要加'?'
                    inType = param.get('in')
                    type = param.get('schema').get('type')
                    name = param.get('name')
                    value = fuzz(type)
                    # 不同的in对应不同的数据
                    if inType == 'path' and name == 'user_id':
                        completeUrl = completeUrl.replace('{' + name + '}', str('lty'))
                    elif inType == 'path' and name == 'id' and method == 'delete':
                        delete_id=random.choice(project_ids)
                        completeUrl = completeUrl.replace('{' + name + '}', str(delete_id))
                        f_d.write("%d\n"%float(delete_id))
                        lines = [l for l in open("D://pool.txt", "r") if l.find(delete_id) != 0]
                        fd = open("D://pool.txt", "w")
                        fd.writelines(lines)
                        fd.close()
                    elif inType == 'path' and name == 'id':
                        completeUrl = completeUrl.replace('{' + name + '}', str(random.choice(project_ids)))
                    elif inType == 'path':
                        completeUrl = completeUrl.replace('{' + name + '}', str(value))
                    elif inType == 'query':
                        # url追加key1=value1&key2=value2到url后,即查询字符串
                        if flag == 0:
                            flag = 1
                            completeUrl = completeUrl + "?" + str(name) + "=" + str(value)
                        else:
                            completeUrl = completeUrl + "&" + str(name) + "=" + str(value)
                    elif inType == 'body':
                        # 参数组成json字符串 ==> data
                        pass

            if method == 'post':
                for i in range(5):
                    values = str(value)+str(i)
                    completeUrl = completeUrl.replace(str(value), str(values))
                    unit = testUnit(method, completeUrl, i)
                    response = unit.exec()
                    if response.text != '[]':
                        if response.text.replace('[', '').replace(']', '').split(':')[0].split('{')[1] == "\"id\"":
                            project_id = response.text.replace('[', '').replace(']', '').split(':')[1].split(',')[0]
                            f_p.write("%d\n"%float(project_id))
                            project_ids.append(project_id)
                            print(project_id)
                    print(response.content)
                f_p.close()
                print(project_ids)

            else:
                unit = testUnit(method, completeUrl, data)
                response = unit.exec()
                print(response.content)