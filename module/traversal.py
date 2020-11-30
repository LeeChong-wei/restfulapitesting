from module.dep_analysis import get_dep_info
from module.parse import parse
import os.path

my_path = os.path.abspath(os.path.dirname(__file__))
api_info_list = parse(os.path.join(my_path, "../openapi/project.yaml"), 1.0)
matrix, weight_info_list = get_dep_info(api_info_list)
graph = matrix

# 记录拓扑排序顺序
topology_order = []
# 记录出度为0的点
out_degree_zero = []
# 记录已经访问的点
visited = []
# 设计出度为0的点
end = []
for i in range(1,len(graph)):
    end.append(0)

# 收集出度为0的点的集合
for i in range(1,len(graph)):
    if graph[i].__eq__(end):
        out_degree_zero.append(i)

# 拓扑，通过回溯insert到l中
def topology_visit(g, n):
    if n not in visited:
        visited.append(n)
    for m in range(1,len(g)):
        if g[m][n] and m not in visited:
            topology_visit(g, m)
    topology_order.insert(0,n)


for n in out_degree_zero:
    topology_visit(graph, n)