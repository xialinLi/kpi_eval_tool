side_2d_config = {
    'iou' : 0.5,
    'topcut': 200,
    'proportion':3.75,
    'obstacle_type' : ['car', 'truck', 'bus', 'pedestrian', 'bicycle', 'motorcycle', 'tricycle'],
    'enum_obstacle': {1: 'car', 2: 'truck', 3: 'bus', 4: 'pedestrian', 5: 'bicycle', 6: 'motorcycle',
                      7: 'tricycle',8: 'misc',9:'car_sedan', 10:'car_hatchback', 11:'car_other',
                      12:'truck_big', 13:'truck_small', 14:'truck_other',
                      15:'bus_big', 16:'bus_small', 17:'bus_other', 18:'wheel'},
    'subclass_type' : ['car', 'truck', 'bus'],
    'class_subclass_type' : ['car_sedan', 'car_hatchback', 'car_other', 'truck_big', 'truck_small', 'truck_other', 'bus_big', 'bus_small', 'bus_other'],
    'car' : {0: 'sedan', 1: 'hatchback', 2:'other'},
    'truck': {0: 'big', 1: 'small', 2:'other'},
    'bus': {0: 'big', 1: 'small', 2:'other'}
}

side_3d_config = {
    'iou' : 0.5,
    'topcut': 200,
    'proportion':3.75,
    'obstacle_type' : ['car', 'truck', 'bus', 'pedestrian', 'bicycle', 'motorcycle', 'tricycle'],
    'enum_obstacle': {1: 'car', 2: 'truck', 3: 'bus', 4: 'pedestrian', 5: 'bicycle', 6: 'motorcycle',
                      7: 'tricycle',8: 'misc',9:'car_sedan', 10:'car_hatchback', 11:'car_other',
                      12:'truck_big', 13:'truck_small', 14:'truck_other',
                      15:'bus_big', 16:'bus_small', 17:'bus_other', 18:'wheel'},
    'subclass_type' : ['car', 'truck', 'bus'],
    'class_subclass_type' : ['car_sedan', 'car_hatchback', 'car_other', 'truck_big', 'truck_small', 'truck_other', 'bus_big', 'bus_small', 'bus_other'],
    'car' : {0: 'sedan', 1: 'hatchback', 2:'other'},
    'truck': {0: 'big', 1: 'small', 2:'other'},
    'bus': {0: 'big', 1: 'small', 2:'other'}
}


front_2d_config = {
    'iou' : 0.5,
    # 'topcut': 0,
    'topadd': 160,
    'percecut':160,
    'proportion':3,
    'obstacle_type' : ['car', 'truck', 'bus', 'pedestrian', 'bicycle', 'motorcycle', 'tricycle','misc','cone','barrier','safety-crash-barrels',
                      'tripod', 'traffic_light', 'traffic_sign','parking_lock'],
    'enum_obstacle': {1: 'car', 2: 'truck', 3: 'bus', 4: 'pedestrian', 5: 'bicycle', 6: 'motorcycle',
                      7: 'tricycle',8: 'misc',9:'cone', 10:'barrier', 11:'safety-crash-barrels',
                      12:'tripod', 13:'traffic_light', 14:'traffic_sign',15:'parking_lock',16:'wheel'}
}