import numpy as np
from entity.api_info import api_info
from entity.field_info import field_info

#api的information，以list保存 , num为api的number  ,  dir1,2分别为特殊的api存储，表示字段相同含义不同，字段不同含义相同
def get_dep_info(api_info_list,dir1,dir2,num):
    # 定义邻接矩阵matri
    matrix = np.zeros([num, num], dtype=int)
    m=np.ones([num,num],dtype=int)
    matrix-=m
    # 定义一个list，命名weight_info_list，其中index从0~n，填入matrix，其中list[index]=[].append(id,name...)存储请求字段
    weight_info_list = []
    #weight_info_list的index
    index = 0
    #判断依赖关系 (判断条件可扩展)
    def dependency(req_field_info,resp_field_info):
        if req_field_info.field_name == resp_field_info.field_name:
            return 1
        else:
            return 0

    #从request和response中判断是否有依赖关系
    def api_relation(api_info_list,i):
        #基于consumer的依赖图
            for req_field_info in api_info_list[i].req_param :                     #request_list[i][2]是一个req的list,req就是其中的一个field_info,fied_info也是一个list存储
                if req_field_info.require == True and req_field_info.fuzz ==False:       #对应req的字段必填，且不需要模糊处理
                    for j in num:
                        if j==i:
                            j+=1                           #跳过api自身的比较
                            for resp_field_info in api_info_list[j].resp_param:    #resp是一个fiel_info类型
                                #判断依赖关系
                                if dependency(req_field_info,resp_field_info):
                                    return j,req_field_info.field_name
                                else:
                                    return 0

    #定义一个Adjacency Matrix，显示依赖关系。其中[x][y]=m,x为request_path，y为response_path，m为list_dependence的index
    def adj_matrix():
        for i in num:
            global index
            j,req_field_name=api_relation(api_info_list,i)
            if j:
                matrix[i][j]=index
                index+=1
            weight_info_list[index]=[].append(req_field_name)

#####################################################################################################################

    def update_weight(dir1,dir2):        #dir1,2分别为特殊的api存储，表示字段相同含义不同，字段不同含义相同
        for key in dir1.keys():
            value=dir1(key)
            list_key=key.split("+")
            list_value=value.split("+")
            index_key=api_info.list(list_key[0])
            index_value=api_info.list(list_value[0])
            index_=matrix[index_key][index_value]
            weight_info_list[index_]=weight_info_list[index_].remove(list_key[0])           #在weight[index]位置的该name字段remove
            if weight_info_list[index_]=="":             #判断该weight[index]是否为空，若为空，则无依赖关系
                matrix[index_key][index_value]=-1       #matrix无依赖关系时，默认值为-1
        for key in dir2.keys():
            value = dir2(key)
            list_key = key.split("+")
            list_value = value.split("+")
            index_key = api_info.list(list_key[0])
            index_value = api_info.list(list_value[0])
            global index
            index+=1
            matrix[index_key][index_value]=index
            weight_info_list[index] = [].append(list_key[1])
            weight_info_list[index] = [].append(list_value[1])

    update_weight(dir1,dir2)

    return matrix,weight_info_list
