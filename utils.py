import json
import os
import config
import json
import re
import glob
from pathlib import Path

def get_json_data(json_file):
    with open(json_file) as f:
        try:
            json_data = json.load(f)
        except:
            print('json文件加载失败：{}'.format(json_file))
            return None
        return json_data


def get_json_list(json_path):
    json_list = []
    for root, _, files in os.walk(json_path):
        for file_ in files:
            if file_.endswith('.json'):
                file = root + '/' + file_
                json_list.append(file)
    if json_list==[]:
        print("目录下没有符合条件的json标注文件，请检查！")
    return(json_list)

#遍历文件下所有文件，返回函数walks： for root,files in walks(src):  files返回绝对路径+文件，且已从小到大排序
imgtypes = ['.jpg', '.bmp', '.png', '.yuv']
def usort(fnames):
    if isinstance(fnames, dict):
        fnames = dict(sorted(fnames.items(), key=lambda k: int(re.sub(r'[^0-9]', '', k[0]))))
    elif isinstance(fnames, list):
        if len(fnames) and re.sub(r'[^0-9]', '', fnames[0]) != '':
            if isinstance(fnames[0], list):
                fnames = sorted(fnames, key=lambda k:int(re.sub(r'[^0-9]', '', k[0])))
            elif isinstance(fnames[0], dict):
                fnames = dict(sorted(fnames.items(), key=lambda k:int(re.sub(r'[^0-9]', '', k))))
            else:
                # if 'Side' in fnames[0]:
                #     print(int(fnames[0].split('/')[-1].split('-')[1] + fnames[0].split('/')[-1].split('-')[1]))
                #     fnames = sorted(fnames, key=lambda fname:int(fname.split('/')[-1].split('-')[1] + fname.split('/')[-1].split('-')[0]))
                # else:
                fnames = sorted(fnames, key=lambda fname:int(re.sub(r'[^0-9]', '', fname)))
            return fnames
    else:
        pass
    return fnames
def walk(p, regex='**/*'):
    regex = '**/*' if regex == '*' else regex
    fpaths = glob.glob('{}/{}'.format(p, regex), recursive=True)
    fpaths = [fpath for fpath in fpaths if fpath[-4:] in imgtypes]
    # print('==> Number: {:<6d}, Path: {}'.format(len(fpaths), '{}/{}'.format(osp.abspath(p), regex)))
    assert(len(fpaths)), 'No images in p: {}'.format(p)
    if fpaths:
        walks = {}
        for fpath in fpaths:
            dirpath = Path(fpath).parent.as_posix()
            if dirpath not in walks:
                walks[dirpath] = [fpath]
            else:
                walks[dirpath].append(fpath)

        for dirpath, fpaths in walks.items():
            try:
                walks[dirpath] = usort(fpaths)
            except:
                walks[dirpath] = fpaths
        try:
            walks = usort(walks).items()
        except:
            print('    !!!Sort error!!!')
            walks = walks.items()
    return walks


def judge_is_in_attentionArea(x,y, attention_area):
    is_in = False  
    point = [x, y]
    xn = [float(x) for x in attention_area["xn"].replace('"', '').split(';')]
    yn = [float(y) for y in attention_area["yn"].replace('"', '').split(';')]
    polygon_temp = zip(xn, yn)
    polygon = []
    for temp in polygon_temp:
        temp1 = list(temp)
        polygon.append(temp1)
    if is_in_poly(point, polygon):
        is_in = True
    return is_in

def is_in_poly(p, poly):
    """
    判断点是否在任意多边形内部
    :param p: [x, y]
    :param poly: [[], [], [], [], ...]
    :return:
    """
    px, py = p
    poly = list(poly)
    is_in = False
    for i, corner in enumerate(poly):
        next_i = i + 1 if i + 1 < len(poly) else 0
        x1, y1 = corner
        x2, y2 = poly[next_i]
        if (x1 == px and y1 == py) or (x2 == px and y2 == py):  # if point is on vertex
            is_in = True
            break
        if min(y1, y2) < py <= max(y1, y2):  # find horizontal edges of polygon
            x = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if x == px:  # if point is on edge
                is_in = True
                break
            elif x > px:  # if point is on left-side of line
                is_in = not is_in
    return is_in

# iou
def bb_intersection_over_union_front(boxA, boxB):
    '''
    iou计算
    boxA 是lablebox，boxB 是percebox
    lable和perce都是左上角点
    '''
    top_cut = config.front_config["top_cut"]
    multiple = config.front_config["multiple"]
    top_black_edge = config.front_config["top_black_edge"]
    A11 = boxA["x"]
    A12 = boxA["x"] + boxA["w"]
    A21 = boxA["y"] 
    A22 = boxA["y"] + boxA["h"]

    B11 = boxB["x"] * multiple
    B12 = (boxB["x"] + boxB["w"]) * multiple
    B21 = boxB["y"] * multiple - (top_black_edge - top_cut)
    B22 = (boxB["y"] + boxB["h"])* multiple - top_cut

    areaA = boxA["h"] * boxA["w"]
    areaB = boxB["h"] * multiple * boxB["w"] * multiple

    interW = max(0, min(A12, B12) - max(A11, B11))
    interH = max(0, min(A22, B22) - max(A21, B21))

    interArea = interH * interW
    iou = interArea / (areaA + areaB - interArea)
    return iou

def get_lable_2d_boxs(lable_json_data):
    lable_json_boxs_list = lable_json_data["task_vehicle"]
    return lable_json_boxs_list

def get_perce_2d_boxs(perce_json_data):
    perce_json_boxs_list = perce_json_data["tracks"]
    return perce_json_boxs_list

def get_box_point(box):
    w = int(box["w"])
    h = int(box["h"])
    x = int(box["x"])
    y = int(box["y"])
    return x,y,w,h

def get_dist_from_type_front(type):
    max_dist = config.front_config["range_x_max_3d"][type]
    min_dist = int(max_dist/3)
    mid_dist = min_dist*2
    return min_dist,mid_dist,max_dist