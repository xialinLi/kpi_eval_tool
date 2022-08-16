side_config = {
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


front_config = {
    'iou' : 0.5,
    'top_cut': 40,
    'bottom_cut': 88,
    'proportion':3,
    'obstacle_type' : ['car', 'truck', 'bus', 'pedestrian', 'bicycle', 'motorcycle', 'tricycle','misc','cone','barrier','safety-crash-barrels',
                      'tripod', 'traffic_light', 'traffic_sign','parking_lock'],
    'enum_obstacle': {1: 'car', 2: 'truck', 3: 'bus', 4: 'pedestrian', 5: 'bicycle', 6: 'motorcycle',
                      7: 'tricycle',8: 'misc',9:'cone', 10:'barrier', 11:'safety-crash-barrels',
                      12:'tripod', 13:'traffic_light', 14:'traffic_sign',15:'parking_lock',16:'wheel'},
    'ranging_y': {'ego':(0, 1.8),'first': (1.8, 5.3), 'second': (5.3, 8.8), 'third': (8.8, 12.3)},
    'max_range': {'car':200, 'truck':240, 'bus':240, 'motorcycle':112, 'bicycle':112, 'ped_adult':94, 'ped_kid':77, 'tricycle':126, 
                  'cone':56, 'barrier':63, 'safety-crash-barrels':63, 'traffic_light':60,
                  'traffic_sign_0.6x0.6':60, 'traffic_sign_0.8x0.8':78, 'traffic_sign_1x1':98}
}
