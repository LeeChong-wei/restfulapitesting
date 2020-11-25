graph=[]
# 记录拓扑排序顺序
l = []
# 记录出度为0的点
s = []
# 记录已经访问的点
v = []
# 设计出度为0的点
end = []
for i in range(1,len(graph)):
    end.append(0)
# 收集出度为0的点的集合
for i in range(1,len(graph)):
    if graph[i].__eq__(end):
        s.append(i)

# 拓扑，通过回溯insert到l中
def visit(g, n):
    if n not in v:
        v.append(n)
    for m in range(1,len(g)):
        if g[m][n] and m not in v:
            visit(g, m)
    l.insert(0,n)


for n in s:
    visit(graph, n)