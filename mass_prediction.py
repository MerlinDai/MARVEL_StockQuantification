import numpy as np
import pandas as pd
import os
import random


class BuildingMassEstimator:
    def __init__(self, age, archetype, wall_height, wall_perimeter, wall_width, wall_depth, inner_wall_length,
                 window_num, window_h_avg, window_w_avg):
        """archytype: full_stone, facade_stone, cavity wall, solid brick
           all dimension input: in unit m """
        self.age = age
        self.archetype = archetype
        self.wall_h = wall_height
        self.wall_p = wall_perimeter
        self.wall_w = wall_width
        self.wall_d = wall_depth
        self.wall_inn = inner_wall_length
        self.window_w = window_w_avg
        self.window_h = window_h_avg
        self.window_n = window_num

    def glazing_estimator(self, mode='c'):
        if mode == 'c': # c for conservative
            if self.age != 'modern':
                return 1
            else:
                return 2
        elif mode == 'r': # r for retrofit:
            return 2
        else:
            print('Key Error')

    def glass_estimator(self, glazing_mode, frame_width=70, thickness=4, glass_density=2500):
        # width should be in unit m, density is with dimension kg/m3
        glass_w = self.window_w - 2 * frame_width / 1000
        glass_h = self.window_h - 2 * frame_width / 1000
        glass_a = glass_w * glass_h * self.window_n  # m2
        glazing_type = self.glazing_estimator(glazing_mode)
        glass_v = glass_a * glazing_type * thickness / 1000  # m3
        glass_m = glass_v * glass_density  # kg
        return glass_a, glass_v, glass_m

    def double_skin_brick_estimator(self, max_span):

        if self.archetype == 'cavity wall':
            double_skin_length = self.wall_p
        elif self.archetype == 'solid brick':
            double_skin_length = self.wall_p
        elif self.archetype == 'facade_stone':
            double_skin_length = self.wall_p - self.wall_w
        else:
            double_skin_length = 0

        if double_skin_length != 0:
            # structure_length = 0
            # if self.wall_w > max_span:
            #     f = int(self.wall_w / max_span)
            #     structure_length += f * self.wall_w
            #
            # if self.wall_d > max_span:
            #     f = int(self.wall_d / max_span)
            #     structure_length += f * self.wall_d
            #
            # if structure_length > self.wall_inn:
            #     double_skin_length += self.wall_inn
            # else:
            #     double_skin_length += structure_length
            if self.wall_d > max_span:
                f = int(self.wall_d / max_span)
                structural_len = f * self.wall_w
                double_skin_length += structural_len

        return double_skin_length

    def one_skin_brick_estimator(self, double_skin_length):
        # if self.archetype == 'cavity wall':
        #     one_skin_length = self.wall_p + self.wall_inn - double_skin_length
        # elif self.archetype == 'solid brick':
        #     one_skin_length = self.wall_p + self.wall_inn - double_skin_length
        # elif self.archetype == 'facade_stone':
        #     one_skin_length = self.wall_p + self.wall_inn - self.wall_w - double_skin_length
        # else:
        #     one_skin_length = 0
        if self.archetype != 'full_stone':
            one_skin_length = self.wall_p + self.wall_inn - double_skin_length
        else:
            one_skin_length = 0
        return one_skin_length

    def one_skin_stone_estimator(self, max_span):
        if self.archetype == 'full_stone':
            one_skin_length = self.wall_inn
            # if self.wall_w > max_span:
            #     f = int(self.wall_w / max_span)
            #     one_skin_length -= f * max_span
            #
            # if self.wall_d > max_span:
            #     f = int(self.wall_d / max_span)
            #     one_skin_length -= f * self.wall_d

            if self.wall_d > max_span:
                f = int(self.wall_d / max_span)
                one_skin_length -= f * self.wall_w

        else:
            one_skin_length = 0
        return one_skin_length

    def double_skin_stone_estimator(self, one_skin_len):
        if self.archetype == 'full_stone':
            double_skin_length = self.wall_p + self.wall_inn - one_skin_len
        elif self.archetype == 'facade_stone':
            double_skin_length = self.wall_w
        else:
            double_skin_length = 0
        return double_skin_length

    def wall_material_estimator(self, brick_density=2000, stone_density=2600, mortar_density=2300, max_span=6):
        brick_double_skin_len = self.double_skin_brick_estimator(max_span)
        brick_one_skin_len = self.one_skin_brick_estimator(brick_double_skin_len)

        stone_one_skin_len = self.one_skin_stone_estimator(max_span)
        stone_double_skin_len = self.double_skin_stone_estimator(stone_one_skin_len)
        # print('the house has height %s m ' % self.wall_h)
        print('the house has %s m double skin wall and %s m one skin wall of brick,'
              % (brick_one_skin_len, brick_double_skin_len))
        print('and has %s m double skin wall and %s m one skin wall of stone'
              % (stone_one_skin_len, stone_double_skin_len))

        brick_mass = self.wall_h * 59 * (brick_one_skin_len + 2 * brick_double_skin_len) \
                     * brick_density / (1000 * 1000 * 1000 / (215 * 102.5 * 65))

        stone_mass = self.wall_h * 59 * (stone_one_skin_len + 2 * stone_double_skin_len) \
                     * stone_density / (1000 * 1000 * 1000 / (215 * 102.5 * 65))

        mortar_mass = self.wall_h * 0.017712 * (1 * (brick_one_skin_len + stone_one_skin_len)
                                     + 2 * (brick_double_skin_len + stone_double_skin_len)) * mortar_density
        return brick_mass / 1000, stone_mass / 1000, mortar_mass / 1000


def set_stone_wall_type(wall_list, prob=0.0):
    new_list = []
    for wall in wall_list:
        if wall == 'stone':
            if random.random() < prob:
                new_list.append('facade_stone')
            else:
                new_list.append('full_stone')
        else:
            new_list.append(wall)
    return new_list


if __name__ == '__main__':
    building_data_df = pd.read_csv(r'E:\BuildingStockQuantification\results\validation_work\results_for_submission\results - v1.1.csv')
    mass_save_csv = r'E:\BuildingStockQuantification\results\validation_work\results_for_submission\mass - v1.1.csv'
    stone_facade_prob = 0

    # sharable_variables
    address = building_data_df['address'].tolist()
    wall_height = building_data_df['relh2'].tolist()

    window_height = building_data_df['avg_window_height_prediction'].tolist()
    window_num = building_data_df['num_of_windows'].tolist()

    # Ground truth data
    gt_age = building_data_df['age_cohort_epc'].tolist()
    gt_inner_wall_len = building_data_df['sum_inner_wall_verified'].tolist()
    gt_wall_p = building_data_df['perimeter_verified'].tolist()
    gt_wall_w = building_data_df['width_verified'].tolist()
    gt_wall_d = building_data_df['depth_verified'].tolist()
    gt_window_width = building_data_df['avg_window_width_verified'].tolist()
    gt_archetype_raw = building_data_df['wall_type_epc'].tolist()

    gt_archetype = [wall.lower() for wall in gt_archetype_raw]
    gt_archetype = [item.replace('granite or whinstone', 'stone') for item in gt_archetype]
    gt_archetype = [item.replace('sandstone or limestone', 'stone') for item in gt_archetype]
    gt_archetype = [item.replace('sandstone', 'stone') for item in gt_archetype]
    gt_archetype = [item.replace('granite or whin', 'stone') for item in gt_archetype]
    gt_archetype = set_stone_wall_type(gt_archetype, stone_facade_prob)
    print(set(gt_archetype))

    # Prediction data
    pred_age = building_data_df['age_cohort_prediction'].tolist()
    pred_inner_wall_len = building_data_df['sum_inner_wall_prediction'].tolist()
    pred_wall_p = building_data_df['perimeter_prediction'].tolist()
    pred_wall_w = building_data_df['width_prediction'].tolist()
    pred_wall_d = building_data_df['depth_prediction'].tolist()
    pred_window_width = building_data_df['avg_window_width_prediction'].tolist()
    pred_archetype_raw = building_data_df['wall_type_prediction'].tolist()

    pred_archetype = [item.replace('cavity_brick', 'cavity wall') for item in pred_archetype_raw]

    pred_archetype = [item.replace('solid_brick', 'solid brick') for item in pred_archetype]
    pred_archetype = set_stone_wall_type(pred_archetype, stone_facade_prob)
    print(set(pred_archetype))
    # pred_archetype = gt_archetype

    gt_brick_mass_list = []
    gt_stone_mass_list = []
    gt_mortar_mass_list = []
    gt_glass_mass_c_list = []
    gt_glass_mass_r_list = []

    pred_brick_mass_list = []
    pred_stone_mass_list = []
    pred_mortar_mass_list = []
    pred_glass_mass_c_list = []
    pred_glass_mass_r_list = []

    for i, _address in enumerate(address):
        gt_house_mass = BuildingMassEstimator(gt_age[i], gt_archetype[i], wall_height[i], gt_wall_p[i],
                                              gt_wall_w[i], gt_wall_d[i], gt_inner_wall_len[i], window_num[i],
                                              window_height[i], gt_window_width[i])

        gt_brick_mass, gt_stone_mass, gt_mortar_mass = gt_house_mass.wall_material_estimator()
        # print('the house has verified %s T brick, %s T stone and %s T mortar ' % (gt_brick_mass, gt_stone_mass, gt_mortar_mass))

        gt_glass_mass_conservative = gt_house_mass.glass_estimator('c')
        gt_glass_mass_retrofit = gt_house_mass.glass_estimator('r')

        pred_house_mass = BuildingMassEstimator(pred_age[i], pred_archetype[i], wall_height[i], pred_wall_p[i],
                                                pred_wall_w[i], pred_wall_d[i], pred_inner_wall_len[i], window_num[i],
                                                window_height[i], pred_window_width[i])
        pred_brick_mass, pred_stone_mass, pred_mortar_mass = pred_house_mass.wall_material_estimator()
        # print('the house has predicted %s T brick, %s T stone and %s T mortar ' % (pred_brick_mass, pred_stone_mass, pred_mortar_mass))

        pred_glass_mass_conservative = pred_house_mass.glass_estimator('c')
        pred_glass_mass_retrofit = pred_house_mass.glass_estimator('r')

        gt_brick_mass_list.append(gt_brick_mass)
        gt_stone_mass_list.append(gt_stone_mass)
        gt_mortar_mass_list.append(gt_mortar_mass)
        gt_glass_mass_c_list.append(gt_glass_mass_conservative[2])
        gt_glass_mass_r_list.append(gt_glass_mass_retrofit[2])

        pred_brick_mass_list.append(pred_brick_mass)
        pred_stone_mass_list.append(pred_stone_mass)
        pred_mortar_mass_list.append(pred_mortar_mass)
        pred_glass_mass_c_list.append(pred_glass_mass_conservative[2])
        pred_glass_mass_r_list.append(pred_glass_mass_retrofit[2])

    mass_df = pd.DataFrame({'address': address, 'brick_mass_verified': gt_brick_mass_list,
                            'stone_mass_verified': gt_stone_mass_list,
                            'mortar_mass_verified': gt_mortar_mass_list,
                            'glass_mass_conservative_verified': gt_glass_mass_c_list,
                            'glass_mass_retrofit_verified': gt_glass_mass_r_list,

                            'brick_mass_prediction': pred_brick_mass_list,
                            'stone_mass_prediction': pred_stone_mass_list,
                            'mortar_mass_prediction': pred_mortar_mass_list,
                            'glass_mass_conservative_prediction': pred_glass_mass_c_list,
                            'glass_mass_retrofit_prediction': pred_glass_mass_r_list})

    mass_df.to_csv(mass_save_csv)
