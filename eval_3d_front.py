import utils
import config
import pandas as pd
from datetime import datetime
import os
import json

class Eval3DFront:
    def __init__(self, lable_path, perce_path):
        '''初始化参数'''
        self.lable_path = lable_path
        self.perce_path = perce_path
        self.iou = config.front_config["iou"]
        self.obstacle_type_3d = config.front_config["obstacle_type_3d"]
        self.enum_obstacle = config.front_config["enum_obstacle"]
        self.topcut = config.front_config["top_cut"]
        self.bottomcut = config.front_config["bottom_cut"]
        self.multiple = config.front_config["multiple"]
        self.range_y = config.front_config["range_y"]
        self.range_x_max_3d = config.front_config["range_x_max_3d"]

    def proc_json_data(self):
        '''将lable列表中的json数据和perce列表中一一对应'''
        self.lable_jsons_list = utils.get_json_list(self.lable_path)
        self.perce_jsons_list_old = utils.get_json_list(self.perce_path)
        self.perce_jsons_list = []
        for lable_json in  self.lable_jsons_list:
            lable_num = int(os.path.basename(lable_json).split('_')[-1].split('.')[0])
            for perce_json in self.perce_jsons_list_old:
                perce_num = int(os.path.basename(perce_json).split('.')[0])
                if lable_num==perce_num:
                    self.perce_jsons_list.append(perce_json)
        if len(self.lable_jsons_list)!=len(self.perce_jsons_list):
            print('感知json数量和标注json数量不一致，请检查！')
    
    def eval_2d_front_range(self):
        '''
        测距评测指标：横向距离平均误差、纵向距离平均误差
        '''
        pass
        # for obstacle_type in self.obstacle_type_3d:
        #     dist_max_x = 
        # 新建表格
    #     columns = ['range_x\range_y','items'] + list((self.range_y).keys())
        
        # for i in range(len(self.lable_jsons_list)):
        #     # 获取同一张图片的lable_json和perce_json的内容
        #     columns = ['range_x','items'] + list((self.range_y).keys())
        #     lable_json_data = utils.get_json_data(self.lable_jsons_list[i])
        #     perce_json_data = utils.get_json_data(self.perce_jsons_list_new[i])
        #     lable_boxs_list = []
        #     perce_boxs_list = []
        #     perce_position_list=[]
        #     dis_x_list = []
        #     dis_y_list = []
        #     if not lable_json_data or lable_json_data["3d"]==[] or not perce_json_data or perce_json_data["tracks"]==[]:
        #         continue
        #     else:
        #         for lable_temp in lable_json_data["3d"]:
        #             type = lable_temp["type"]
        #             position = lable_temp["position"]
        #             lable_box_2d = lable_temp["box_2d"]
        #             lable_boxs_list.append(lable_box_2d)
        #         for perce_temp in perce_json_data["tracks"]:
        #             perce_box_2d = {"x" : perce_temp["uv_bbox2d"]["obstacle_bbox.x"],
        #                             "y" : perce_temp["uv_bbox2d"]["obstacle_bbox.y"],
        #                             "w" : perce_temp["uv_bbox2d"]["obstacle_bbox.width"],
        #                             "h" : perce_temp["uv_bbox2d"]["obstacle_bbox.height"]}
        #             perce_position = {
        #                 'x':perce_temp["bbox3d"]["obstacle_pos_x"],
        #                 'y':perce_temp["bbox3d"]["obstacle_pos_y"],
        #                 'z':perce_temp["bbox3d"]["obstacle_pos_z"]
        #             }
        #             perce_position_list.append(perce_position)
        #             perce_boxs_list.append(perce_box_2d)
        #         for m in range(len(lable_boxs_list)):
        #             iou_result = {}
        #             for n in range(len(perce_boxs_list)):
        #                 iou_result[n] = utils.bb_intersection_over_union_front(lable_boxs_list[m],perce_boxs_list[n])
        #             if iou_result=={}:
        #                 continue
        #             iou_max_item = max(iou_result.items(), key=lambda x: x[1])
        #             iou_max_value = iou_max_item[1]
        #             iou_max_id = iou_max_item[0]
        #             if iou_max_value < self.iou:
        #                 continue
        #             else:
        #                 dis_x = abs(lable_boxs_list[m]["position"]["x"]-perce_boxs_list[iou_max_id]["perce_position"]["x"])
        #                 dis_y = abs(lable_boxs_list[m]["position"]["y"]-perce_boxs_list[iou_max_id]["perce_position"]["y"])
        #                 dis_rate_x = abs(lable_boxs_list[m]["position"]["x"]-perce_boxs_list[iou_max_id]["perce_position"]["x"])/max(1,abs(lable_boxs_list[m]["position"]["x"]))
        #                 dis_rate_y = abs(lable_boxs_list[m]["position"]["x"]-perce_boxs_list[iou_max_id]["perce_position"]["x"])/max(1,abs(lable_boxs_list[m]["position"]["x"]))
        #                 dis_x_list.append(dis_x)
        #                 dis_y_list.append(dis_y)
        #                 del perce_boxs_list[iou_max_id]