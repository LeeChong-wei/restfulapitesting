from entity.node import node
from entity.link import link
from common.common_utils import comutil
import webbrowser
import os
from entity.graph import g


def dep_info_display(api_info_list,dep_matrix,weight_info_list):

    l = len(list(list(dep_matrix)[0]))
    #生成node_list
    nodes = []
    i = 0
    while i < l:
        n = node(i,'GitLab','API' + str(i))
        nodes.append(n)
        i += 1

    #生成link_list
    links = []
    i = 0
    while i < l:
        j = 0
        while j < l:
            if dep_matrix[i][j] != -1:
                lin = link(i,j,'')
                links.append(lin)
            j += 1
        i += 1
    graph = g(nodes,links)
    print(comutil.toJson(graph))
    #webbrowser.open_new_tab(os.getcwd() + '\\restful\\resource\\display.html')