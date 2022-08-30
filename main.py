#!/usr/bin/python
import argparse
import eval_3d_front
import eval_2d_front

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('lablepath', type=str, help='标注文件路径')
    parser.add_argument('percepath', type=str, help='感知文件路径')
    parser.add_argument('evaltype', type=str, help='评测类别，比如side2d,sidesubclass,side3d...')
    parser.add_argument('--picpath', type=str, help='标注原图的图片路径')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    lable_path = args.lablepath
    perce_path = args.percepath
    eval_type = args.evaltype
    pic_path = args.picpath
        
    if eval_type == 'front2d':
        eval_2d_front = eval_2d_front.Eval2DFront(lable_path,perce_path,pic_path)
        eval_2d_front.proc_json_data()
        eval_2d_front.match_lable_perce()
        eval_2d_front.eval_2d_front_recall_precision()
        if pic_path:
            eval_2d_front.get_oripic_depend_errorjson()
            eval_2d_front.draw_pic()

    if eval_type == 'front3d':
        eval_3d_front = eval_3d_front.Eval3DFront(lable_path,perce_path)
        eval_3d_front.proc_json_data()


