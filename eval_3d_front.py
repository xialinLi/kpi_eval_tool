import utils
import config
import pandas as pd
from datetime import datetime
import os
import openpyxl

class Eval3DFront:
    def __init__(self, lable_path, perce_path):
        '''初始化参数'''
        self.lable_path = lable_path
        self.perce_path = perce_path
        self.iou = config.front_config["iou"]
        self.obstacle_type_3d = config.front_config["obstacle_type_3d"]
        self.enum_obstacle = config.front_config["enum_obstacle"]
        self.topcut = config.front_config["top_cut"]
        self.top_black_edge = config.front_config["top_black_edge"]
        self.bottomcut = config.front_config["bottom_cut"]
        self.multiple = config.front_config["multiple"]
        self.range_y = config.front_config["range_y"]
        self.range_x_max_3d = config.front_config["range_x_max_3d"]
        self.current_path = os.getcwd()
        self.str_time = (datetime.now()).strftime("%Y-%m-%d-%H-%M-%S")
        self.excel_path = os.path.join(self.current_path,self.str_time)
        os.makedirs(self.excel_path, exist_ok=True)

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


    
    def record_detection_result(self):
        df = pd.DataFrame(columns=['frame_id','gt_type','gt_dist_x','gt_dist_y','gt_vel_x','perce_dist_x','perce_dist_y','perce_vel_x'])
        m = 0 
        for i in range(len(self.lable_jsons_list)):
            frameid = os.path.basename(self.lable_jsons_list[i]).split('.')[0]
            lable_json_data = utils.get_json_data(self.lable_jsons_list[i])
            perce_json_data = utils.get_json_data(self.perce_jsons_list[i])
            lable_boxs_list = []
            lable_other_info_list = []
            perce_boxs_list = []
            perce_other_info_list = []
            if lable_json_data==[]:
                continue
            else:
                for lable_temp in lable_json_data:
                    lable_box = {"x" : lable_temp["box_2d"]["x"],
                                "y" : lable_temp["box_2d"]["y"],
                                "w" : lable_temp["box_2d"]["w"],
                                "h" : lable_temp["box_2d"]["h"]}
                    lable_type = lable_temp["type"]
                    lable_dist_x = lable_temp["position"]["x"]
                    lable_dist_y = lable_temp["position"]["y"]
                    lable_vel_x = lable_temp["velocity"]["x"]
                    lable_boxs_list.append(lable_box)
                    lable_other_info_list.append([lable_type,lable_dist_x,lable_dist_y,lable_vel_x])
            if perce_json_data==[] or perce_json_data[2]["camera_fusion"]["tracks"]==[]:
                continue
            else:
                for perce_temp in perce_json_data[2]["camera_fusion"]["tracks"]:
                    perce_box = {"x" : perce_temp["uv_bbox2d"]["obstacle_bbox.x"],
                                "y" : perce_temp["uv_bbox2d"]["obstacle_bbox.y"],
                                "w" : perce_temp["uv_bbox2d"]["obstacle_bbox.width"],
                                "h" : perce_temp["uv_bbox2d"]["obstacle_bbox.height"]}
                    perce_dist_x = perce_temp["bbox3d"]["obstacle_pos_x"]
                    perce_dist_y = perce_temp["bbox3d"]["obstacle_pos_y"]
                    perce_vel_x = perce_temp["velocity"]["obstacle_rel_vel_x_filter"]
                    perce_boxs_list.append(perce_box)
                    perce_other_info_list.append([perce_dist_x,perce_dist_y,perce_vel_x])
            iou_result = {}
            for j in range(len(lable_boxs_list)):
                for k in range(len(perce_boxs_list)):
                    iou_result[k] = utils.bb_intersection_over_union_front(lable_boxs_list[j],perce_boxs_list[k])
                if iou_result=={}:
                    continue
                iou_max_item = max(iou_result.items(), key=lambda x: x[1])
                iou_max_value = iou_max_item[1]
                iou_max_id = iou_max_item[0]
                if iou_max_value >= self.iou:
                    df.loc[m,] = [frameid] + lable_other_info_list[j] + perce_other_info_list[iou_max_id]
                    m +=1
                    del perce_boxs_list[iou_max_id]
                    del perce_other_info_list[iou_max_id]
        df.to_excel(os.path.join(self.excel_path,'record_detection_result.xlsx'))

    def eval_distance(self):
        df = pd.read_excel(os.path.join(self.excel_path,'record_detection_result.xlsx'))
        for i in range(len(self.obstacle_type_3d)):
            obstacle_type = self.obstacle_type_3d[i]
            min_dis,mid_dis,max_dis = self.get_dis_by_type(obstacle_type)
            
            print(df[df['gt_type']==obstacle_type])


    def eval_vel(self):
        pass

    

    def get_dis_by_type(self, ob_type):
        max_dis = self.range_x_max_3d[ob_type]
        min_dis = int(max_dis/3)
        mid_dis = int(max_dis / 3 *2)
        return min_dis,mid_dis,max_dis
    
