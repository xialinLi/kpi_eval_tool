from contextlib import nullcontext
from distutils import command
from genericpath import exists
from ntpath import join
from re import S
import utils
import os
import config
import json
import pandas as pd
from datetime import datetime
import cv2
import shutil
from pathlib import Path as path

class Eval2DFront:
    def __init__(self, lable_path, perce_path, ori_pic_path):
        self.lable_path = lable_path
        self.perce_path = perce_path
        self.ori_pic_path = ori_pic_path
        self.iou = config.front_config["iou"]
        self.obstacle_type = config.front_config["obstacle_type_3d"]
        self.enum_obstacle = config.front_config["enum_obstacle"]
        self.top_cut = config.front_config["top_cut"]
        self.multiple = config.front_config["multiple"]
        self.top_black_edge = config.front_config["top_black_edge"]
        self.str_time = (datetime.now()).strftime("%Y-%m-%d-%H-%M-%S")
        self.current_path = os.getcwd()
        self.excel_path = os.path.join(self.current_path,self.str_time,'result')
        self.err_json = os.path.join(self.current_path,self.str_time,'err_json')
        self.err_pic = os.path.join(self.current_path,self.str_time,'err_pic')
        os.makedirs(self.excel_path, exist_ok=True)
        os.makedirs(self.err_json, exist_ok=True)
        os.makedirs(self.err_pic, exist_ok=True)

    def proc_json_data(self):
        '''
        标注json：所有的图片的标注结果都存放在一整个json文件中
        感知检测结果json：单张图片对应一个同名的json
        本方法主要是：将标注的整个json分成多个json,类似感知结果json
        '''
        self.perce_jsons_list = utils.get_json_list(self.perce_path)
        self.lable_jsons_old_list = utils.get_json_list(self.lable_path)
        self.lable_new_path = os.path.join(os.path.dirname(self.lable_path),(os.path.basename(self.lable_path)+'_new'))
        if os.path.exists(self.lable_new_path):
            shutil.rmtree(self.lable_new_path)
        os.makedirs(self.lable_new_path)
        lable_json_data = utils.get_json_data(self.lable_jsons_old_list[0])
        for lable_result in lable_json_data:
            if lable_result["task_vehicle"]==[]:
                continue
            lable_json_name = (lable_result["filename"]).split('_')[-1].split('.')[0].zfill(4) + '.json'
            lable_new_json_path = self.lable_new_path + '/' + lable_json_name
            for perce_json in self.perce_jsons_list:
                perce_json_name = os.path.basename(perce_json).split('.')[0].zfill(4) + '.json'
                if lable_json_name == perce_json_name: 
                    with open(lable_new_json_path,'w') as f:
                        json.dump(lable_result,f,indent=4)
                    break
        self.lable_jsons_list = utils.get_json_list(self.lable_new_path)
    
    def match_lable_perce(self):
        '''
        根据所有的标注json文件，找到对应的感知结果json。在list中，同名的文件是一一对应的。
        '''
        self.perce_jsons_list_new = []
        for lable_json in  self.lable_jsons_list:
            lable_json_name = os.path.basename(lable_json) 
            for perce_json in self.perce_jsons_list:
                perce_json_name = os.path.basename(perce_json).split('.')[0].zfill(4) + '.json'
                # print('perce json:%s',perce_json_name)
                if lable_json_name==perce_json_name:
                    self.perce_jsons_list_new.append(perce_json)
        print(len(self.lable_jsons_list))
        print(len(self.perce_jsons_list_new))
        if len(self.lable_jsons_list)!=len(self.perce_jsons_list_new):
            print('感知json数量和标注json数量不一致，请检查！')

    def eval_2d_front_recall_precision(self):
        df = pd.DataFrame(columns=['KPI'] + self.obstacle_type)
        df.loc[0, 'KPI'] = '检测出类别正确数量'
        df.loc[1, 'KPI'] = '检测出类别错误数量'
        df.loc[2, 'KPI'] = '未检测出数量'
        df.loc[3, 'KPI'] = '误检数量'
        df.loc[4, 'KPI'] = '标注数量'
        df.loc[5, 'KPI'] = '检测数量'
        df.loc[6, 'KPI'] = 'recall'
        df.loc[7, 'KPI'] = 'precision'
        df.fillna(0, inplace=True)
        typeerr_json = os.path.join(self.err_json,'typeerr')
        missdet_json = os.path.join(self.err_json,'missdet')
        errdet_json = os.path.join(self.err_json,'errdet')
        os.makedirs(typeerr_json, exist_ok=True)
        os.makedirs(missdet_json, exist_ok=True)
        os.makedirs(errdet_json, exist_ok=True)
        for i in range(len(self.lable_jsons_list)):
            # 获取同一张图片的lable_json和perce_json的内容
            lable_json_name = os.path.basename(self.lable_jsons_list[i])
            lable_json_data = utils.get_json_data(self.lable_jsons_list[i])
            perce_json_data = utils.get_json_data(self.perce_jsons_list_new[i])
            attention_area = [] if lable_json_data["task_attention_area"]==[] else lable_json_data["task_attention_area"][0]["tags"]
            lable_occluded_list = []
            lable_type_list = []
            lable_boxs_list = []
            perce_type_list = []
            perce_boxs_list = []
            print_typeerr = []
            print_missdet = []
            print_errdet = []
            if not lable_json_data or lable_json_data["task_vehicle"]==[]:
                continue
            else:
                for lable_temp in lable_json_data["task_vehicle"]:
                    lable_occluded_list.append(lable_temp["tags"]["occluded"])
                    lable_type_list.append(lable_temp["tags"]["class"])
                    lable_box = {"x" : lable_temp["tags"]["x"],
                                "y" : lable_temp["tags"]["y"],
                                "w" : lable_temp["tags"]["width"],
                                "h" : lable_temp["tags"]["height"]}
                    lable_boxs_list.append(lable_box)
            if perce_json_data[1]["FOV30"]["tracks"]==[] or perce_json_data[1]["FOV30"]["tracks"]==None:
                perce_type_list=[]
                perce_boxs_list = []
            else:
                for perce_temp in perce_json_data[1]["FOV30"]["tracks"]:
                    perce_type_list.append(self.enum_obstacle[(perce_temp["obstacle_type"])])
                    perce_box = {"x" : perce_temp["uv_bbox2d"]["obstacle_bbox.x"],
                                        "y" : perce_temp["uv_bbox2d"]["obstacle_bbox.y"],
                                        "w" : perce_temp["uv_bbox2d"]["obstacle_bbox.width"],
                                        "h" : perce_temp["uv_bbox2d"]["obstacle_bbox.height"]}
                    perce_boxs_list.append(perce_box)

            if perce_type_list==[] and lable_type_list!=[]:
                for h in range(len(lable_boxs_list)):
                    center_x = lable_boxs_list[h]["x"] + lable_boxs_list[h]["w"]/2
                    center_y = lable_boxs_list[h]["y"] + lable_boxs_list[h]["h"]/2
                    is_in_attentionArea = utils.judge_is_in_attentionArea(center_x,center_y, attention_area)
                    if lable_type_list[h] not in self.obstacle_type or int(lable_occluded_list[h])!=0 or (is_in_attentionArea==False):
                        continue
                    df.iloc[4, df.columns.get_loc(lable_type_list[h])] += 1
                    df.iloc[2, df.columns.get_loc(lable_type_list[h])] += 1
                    print_missdet_json ={}
                    print_missdet_json["lable_type"] = lable_type_list[h]
                    print_missdet_json["perce_type"] = None
                    print_missdet_json["lable_box"] = lable_boxs_list[h]
                    print_missdet_json["perce_box"] = None
                    print_missdet.append(print_missdet_json)
                if print_missdet!=[]:                    
                    with open(os.path.join(missdet_json,lable_json_name),'a') as pf2:
                        json.dump(print_missdet,pf2,indent=4)
            elif perce_type_list!=[] and lable_type_list!=[]:
                for j in range(len(lable_type_list)):
                    center_x2 = lable_boxs_list[j]["x"] + lable_boxs_list[j]["w"]/2
                    center_y2 = lable_boxs_list[j]["y"] + lable_boxs_list[j]["h"]/2
                    is_in_attentionArea = utils.judge_is_in_attentionArea(center_x2,center_y2, attention_area)
                    if int(lable_occluded_list[j])!=0 or (lable_type_list[j] not in self.obstacle_type) or (is_in_attentionArea==False):
                        continue
                    df.iloc[4, df.columns.get_loc(lable_type_list[j])] += 1
                    iou_result = {}
                    for k in range(len(perce_type_list)):
                        iou_result[k] = utils.bb_intersection_over_union_front(lable_boxs_list[j],perce_boxs_list[k])
                    if iou_result=={}:
                        continue
                    iou_max_item = max(iou_result.items(), key=lambda x: x[1])
                    iou_max_value = iou_max_item[1]
                    iou_max_id = iou_max_item[0]
                    if iou_max_value >= self.iou:
                        perce_type = perce_type_list[iou_max_id]
                        if lable_type_list[j]==perce_type:
                            df.iloc[0, df.columns.get_loc(lable_type_list[j])] += 1
                            del perce_boxs_list[iou_max_id]
                            del perce_type_list[iou_max_id]
                        else:
                            df.iloc[1, df.columns.get_loc(lable_type_list[j])] += 1
                            print_typeerr_json ={}
                            print_typeerr_json["lable_type"] = lable_type_list[j]
                            print_typeerr_json["perce_type"] = perce_type
                            print_typeerr_json["lable_box"] = lable_boxs_list[j]
                            print_typeerr_json["perce_box"] = perce_boxs_list[iou_max_id]
                            print_typeerr.append(print_typeerr_json)
                    else:
                        df.iloc[2, df.columns.get_loc(lable_type_list[j])] += 1
                        print_missdet_json ={}
                        print_missdet_json["lable_type"] = lable_type_list[j]
                        print_missdet_json["perce_type"] = None
                        print_missdet_json["lable_box"] = lable_boxs_list[j]
                        print_missdet_json["perce_box"] = None
                        print_missdet.append(print_missdet_json)
                for t in range(len(perce_type_list)):
                    perce_x = (perce_boxs_list[t]["x"]) * self.multiple
                    perce_y = (perce_boxs_list[t]["y"]) * self.multiple - (self.top_black_edge - self.top_cut)
                    perce_w = (perce_boxs_list[t]["w"]) * self.multiple
                    perce_h = (perce_boxs_list[t]["h"]) * self.multiple 
                    center_x3 = perce_x + perce_w/2
                    center_y3 = perce_y + perce_h/2
                    is_in_attentionArea = utils.judge_is_in_attentionArea(center_x3, center_y3, attention_area)
                    if (is_in_attentionArea==False) or (perce_type_list[t] not in self.obstacle_type):
                        continue
                    iou_result={}
                    for r in range(len(lable_type_list)):
                        iou_result[r] = utils.bb_intersection_over_union_front(lable_boxs_list[r],perce_boxs_list[t])
                    iou_max_item = max(iou_result.items(), key=lambda x: x[1])
                    iou_max_value = iou_max_item[1]
                    iou_max_id = iou_max_item[0]
                    if iou_max_value >= self.iou:
                        del lable_boxs_list[iou_max_id]
                        del lable_type_list[iou_max_id]
                    else:
                        df.iloc[3, df.columns.get_loc(perce_type_list[t])] += 1
                        print_errdet_json ={}
                        print_errdet_json["lable_type"] = None
                        print_errdet_json["perce_type"] = perce_type_list[t]
                        print_errdet_json["lable_box"] = None
                        print_errdet_json["perce_box"] = perce_boxs_list[t]
                        print_errdet.append(print_errdet_json)
                if print_typeerr!=[]:
                    with open(os.path.join(typeerr_json,lable_json_name),'w') as pf1:
                        json.dump(print_typeerr,pf1,indent=4)
                if print_missdet!=[]:
                    with open(os.path.join(missdet_json,lable_json_name),'w') as pf2:
                        json.dump(print_missdet,pf2,indent=4)
                if print_errdet!=[]:
                    with open(os.path.join(errdet_json,lable_json_name),'w') as pf3:
                        json.dump(print_errdet,pf3,indent=4)
        
        for type in self.obstacle_type:
            # df.iloc[4,df.columns.get_loc(type)] = df.iloc[0,df.columns.get_loc(type)] + df.iloc[1,df.columns.get_loc(type)] + df.iloc[2,df.columns.get_loc(type)]
            df.iloc[5,df.columns.get_loc(type)] = df.iloc[0,df.columns.get_loc(type)] + df.iloc[1,df.columns.get_loc(type)] + df.iloc[3,df.columns.get_loc(type)]
            df.iloc[6,df.columns.get_loc(type)] = 0 if df.iloc[4,df.columns.get_loc(type)]==0 else round((df.iloc[0,df.columns.get_loc(type)] + df.iloc[1,df.columns.get_loc(type)])*100/df.iloc[4,df.columns.get_loc(type)],1)
            df.iloc[7,df.columns.get_loc(type)] = 0 if df.iloc[5,df.columns.get_loc(type)]==0 else round((df.iloc[0,df.columns.get_loc(type)])*100/df.iloc[5,df.columns.get_loc(type)],1)
        df.to_excel(self.excel_path + '/' + self.str_time + '.xlsx')
        print(df)

    def get_oripic_depend_errorjson(self):
        '''根据已有报错的json文件名，找到对应的原始图片'''
        for root,_,files in os.walk(self.err_json):
            for file_ in files:
                if '0000' in file_:
                    filename = 'frame_vc2_0.png'
                else:
                    filename = 'frame_vc2_' + file_.replace('.json','.png').lstrip("0")
                new_filename = file_.replace('.json','.png')
                dstpic_path = root.replace('err_json','err_pic')
                os.makedirs(dstpic_path, exist_ok=True)
                command = 'cp {} {}'.format(os.path.join(self.ori_pic_path,filename),os.path.join(dstpic_path,new_filename))
                os.system(command)

    def draw_pic(self):
        '''标注是绿色，检测推理结果是红色'''
        for root,_,files in os.walk(self.err_json):
            for file_ in files:
                json_path = os.path.join(root,file_)
                json_data = utils.get_json_data(json_path)
                img_path = os.path.join(root.replace('err_json','err_pic'),file_.replace('.json','.png'))
                img_data = cv2.imread(img_path)
                for json_data_ in json_data:
                    lable_type = json_data_["lable_type"]
                    perce_type = json_data_["perce_type"]
                    lable_box = json_data_["lable_box"]
                    perce_box = json_data_["perce_box"]
                    if lable_type!=None or lable_box!=None:
                        x,y,w,h = utils.get_box_point(lable_box)
                        cv2.rectangle(img_data,(x,y),(x+w,y+h),(0,255,0),1)
                        cv2.putText(img_data,(lable_type[:3]),(x,y),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),1)
                    if perce_type!=None or perce_box!=None:    
                        x2,y2,w,h = utils.get_box_point(perce_box)
                        x2 = x2 * self.multiple
                        y2 = y2 * self.multiple - (self.top_black_edge - self.top_cut)
                        x3 = w * self.multiple + x2
                        y3 = h * self.multiple + y2 
                        cv2.rectangle(img_data,(x2,y2),(x3,y3),(0,0,255),1)                    
                        cv2.putText(img_data,(perce_type[:3]),(x2,y3),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),1)
                cv2.imwrite(img_path,img_data)
        '''误检：打印所有的标注的type和box'''
        for root,_,files in os.walk(os.path.join(self.err_pic,'errdet')):
            for file_ in files:
                pngfile = os.path.join(root,file_)
                jsonfile = os.path.join(self.lable_new_path,file_.replace('.png','.json'))
                imgdata4 = cv2.imread(pngfile)
                for temp in (utils.get_json_data(jsonfile))["task_vehicle"]:
                    lable_type4 = temp["tags"]["class"][:3]
                    x4 = int(temp["tags"]["x"])
                    y4 = int(temp["tags"]["y"])
                    w4 = int(temp["tags"]["width"])
                    h4 = int(temp["tags"]["height"])
                    cv2.rectangle(imgdata4,(x4,y4),(x4+w4,y4+h4),(0,255,0),1)
                    cv2.putText(imgdata4,lable_type4,(x4,y4),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),1)
                cv2.imwrite(pngfile, imgdata4) 
        '''漏检：打印所有的检测的type和box'''
        for root,_,files in os.walk(os.path.join(self.err_pic,'missdet')):
            for file_ in files:
                pngfile = os.path.join(root,file_)
                new_jsonname = str(int(file_.split('.')[0])) + '.json'
                jsonfile = os.path.join(self.perce_path,new_jsonname)
                imgdata5 = cv2.imread(pngfile)
                json_data_tracks = utils.get_json_data(jsonfile)[1]["FOV30"]["tracks"]
                if json_data_tracks!=[] and not json_data_tracks and json_data_tracks!=None:
                    for temp in json_data_tracks:
                        perce_type5 = self.enum_obstacle[temp["obstacle_type"]]
                        x5 = int(temp["uv_bbox2d"]["obstacle_bbox.x"]) * self.multiple
                        y5 = int(temp["uv_bbox2d"]["obstacle_bbox.y"]) * self.multiple - (self.top_black_edge - self.top_cut)
                        w5 = int(temp["uv_bbox2d"]["obstacle_bbox.width"]) * self.multiple
                        h5 = int(temp["uv_bbox2d"]["obstacle_bbox.height"]) * self.multiple
                        cv2.rectangle(imgdata5,(x5,y5),(x5+w5,y5+h5),(0,0,255),1)
                        cv2.putText(imgdata5,perce_type5[:3],(x5,y5),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),1)
                    cv2.imwrite(pngfile, imgdata5) 