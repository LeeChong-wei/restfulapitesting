from entity.node import node
from entity.link import link
from common.common_utils import comutil
import webbrowser
import os
from entity.graph import g

def write_graph_js(json_content):
    filename = os.getcwd() + '/resource/graph.js'
    file = open(filename, "w")
    file.write("function load_data(){return ")
    file.write(json_content)
    file.write("}")
    file.close()

def dep_info_display(api_info_list,dep_matrix,weight_info_list):

    l = len(list(list(dep_matrix)[0]))
    #生成node_list
    nodes = []
    i = 0
    while i < l:
        #计算weight
        weight = 0
        for k in range(l):
            if i == k:
                continue
            if dep_matrix[k][i] != -1:
                weight += 1
        n = node(i,'GitLab','API' + str(i),weight)
        nodes.append(n)
        i += 1
    #生成link_list
    links = []
    i = 0
    while i < l:
        j = 0
        while j < l:
            if i == j:
                j += 1
                continue
            if dep_matrix[i][j] != -1:
                lin = link(i,j,'')
                links.append(lin)
            j += 1
        i += 1

    graph = g(nodes,links)
    write_graph_js(comutil.toJson(graph))
    file_path = os.getcwd() + '/resource/display.html';
    webbrowser.open(file_path)

