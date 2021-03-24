from module.parse import parse
import os
from prance import ResolvingParser


my_path = os.path.abspath(os.path.dirname(__file__))
api_info_list = parse(1.0)



def make():
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../openapi/wordpress.yaml")
    parser = ResolvingParser(path)
    spec = parser.specification
    servers = spec.get("servers")
    url = servers.get('url')
    return url
'''
静态分析：根据路径，匹配路径上相似程度，认为相似程度越高，依赖程度越高
count记录相似程度：
    0 代表不相关
    非0 代表request和response的parameter相同：
        1 代表仅参数相同
        2 代表除参数外，路径上有一个相同
        3 代表除参数外，路径上有两个相同
        ......
        我认为路径相同，依赖程度越高，但是也可根据description进行相似度的检测，3.0版本将加入description进行检测
'''
def dependency2(req_url_path, resp_url_path, req_field_info, resp_field_info):
    count = 0
    if req_field_info.field_name == resp_field_info.field_name:
        count = 1
        url = make()
        req_path = req_url_path.replace(url, '')
        resp_path = resp_url_path.replace(url, '')
        req_li = req_path.split('/')
        resp_li = resp_path.split('/')
        for req in req_li:
            if req in resp_li:
                count += 1
        return count
    else:
        return count