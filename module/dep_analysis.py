import numpy as np

def get_dep_info(api_info_list,num):
    #api的information，以list保存 , num为api的number

    # 定义邻接矩阵matri
    matrix = np.zeros((num, num), dtype=int)
    # 定义一个list，命名weight_info_list，其中index从0~n，填入matrix，其中list[index]=[].append(id,name...)存储请求字段
    weight_info_list = []

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

        index=0
        for i in num:
            j,req_field_name=api_relation(api_info_list,i)
            if j:
                matrix[i][j]=index
                index+=1
            weight_info_list[index]=[].append(req_field_name)
    return matrix,weight_info_list
