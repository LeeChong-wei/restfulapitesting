from prance import ResolvingParser
from entity.api_info import api_info
from entity.field_info import field_info
import os.path


# my_path = os.path.abspath(os.path.dirname(__file__))
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
                requestBody = methods.get(method).get("requestBody")
                req_param_list = []
                if params:
                    for param in params:
                        field_name = param.get("name")
                        require = param.get("required")
                        in_ = param.get("in")
                        if in_ == 'path':
                            in_ = 0
                        elif in_ == 'query':
                            in_ = 1
                        req_param = field_info(field_name, require, "No", False, in_)
                        req_param_list.append(req_param)
                if requestBody:
                    properties = requestBody['content']['application/json']['schema']['properties']
                    for property_ in properties:
                        req_param = field_info(property_, 'false', "No", False, 3)
                        req_param_list.append(req_param)
                responses = methods.get(method).get("responses")
                resp_param_list = []
                for respond in responses:
                    if "content" in responses.get(respond):
                        schema = responses.get(respond).get("content").get("application/json").get("schema")
                        if schema['type'] == 'array':
                            array = schema['items']
                            if array['type'] == 'object':
                                for object_ in array['properties']:
                                    resp_param = field_info(object_, "No", "No", False, "No")
                                    resp_param_list.append(resp_param)
                        elif schema['type'] == 'object':
                            for object_ in schema['properties']:
                                resp_param = field_info(object_, "No", "No", False, "No")
                                resp_param_list.append(resp_param)
                api = api_info(api_id, complete_api_path, req_param_list, resp_param_list, method)
                api_list.append(api)
    return api_list
    pass


# parse(os.path.join(my_path, "../openapi/group-and-project-access-requests-api.yaml"), 1.0)