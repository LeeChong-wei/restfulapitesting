from prance import ResolvingParser
from entity.api_info import api_info
from entity.field_info import field_info


def parse(path,version):
    parser = ResolvingParser(path)
    spec = parser.specification
    servers = spec.get("servers")
    api_id = 0
    api_list = []
    for server in servers:
        url = server.get("url")
        paths = spec.get("paths")
        for api_path in paths:
            methods = paths.get(api_path)
            for method in methods:
                api_id = api_id + 1
                complete_api_path = url + api_path
                params = methods.get(method).get("parameters")
                req_param_list = []
                if params:
                    for param in params:
                        field_name = param.get("name")
                        require = param.get("required")
                        req_param = field_info(field_name, require, "No", False, "No")
                        req_param_list.append(req_param)
                responses = methods.get(method).get("responses")
                resp_param_list = []
                for respond in responses:
                    headers = responses.get(respond).get("headers")
                    if headers:
                        for head in headers:
                            resp_param = field_info(head, "No", "No", False, "No")
                            resp_param_list.append(resp_param)
                api = api_info(api_id, complete_api_path, req_param_list, resp_param_list, method)
                api_list.append(api)

    return api_list
    pass


parse("C:\\Users\\Admin\\Desktop\\openapi1.yaml", 1.0)