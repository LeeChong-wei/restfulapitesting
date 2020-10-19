from module.dep_analysis import get_dep_info
from module.display import dep_info_display
from module.parse import parse

if __name__ == '__main__':
    # #规范解析
    # api_info_list = parse('branch.yaml','1.0.0')
    # #生成依赖矩阵
    # res = get_dep_info(api_info_list)
    # #展示依赖关系
    # dep_matrix = res['dep_matrix']
    # weight_info_list = res['weight_info_list']
    dep_matrix = matrix = [[-1, 0, 1,2,-1],
                           [-1, -1, -1,-1,-1],
                           [-1, -1, -1,-1,-1],
                           [-1, -1, -1,-1,-1],
                           [-1, -1, -1,-1,-1]
                           ]
    weight_info_list = []
    dep_info_display(None,dep_matrix,weight_info_list)