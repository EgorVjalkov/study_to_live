import datetime
import pandas as pd
import numpy as np
import os
from PriceMarkCalc import PriceMarkCalc
import analytic_utilities as au
pd.set_option('display.max.columns', None)


ff = au.FrameForAnalyse()


class CompCoef:
    def __init__(self, coef_data):
        self.coef_data = coef_data

    @property
    def severity_dict(self):
        name = self.coef_data[:self.coef_data.find('(')]
        severity = self.coef_data[self.coef_data.find('(')+1:self.coef_data.find(')')]
        #print(severity)
        return {'name': name, 'sev': severity}

    @property
    def have_coef_data(self):
        return True if self.coef_data else False

    def count_a_coef_value(self, coef, mark=''):
        counted_coef = self.coef_data
        if '{' in self.coef_data:
            counted_coef = eval(self.coef_data)[mark]
            #print(counted_coef)
        elif '[' in self.coef_data:
            counted_coef = eval(self.coef_data)[int(coef)]

        #print(counted_coef)
        if type(counted_coef) == str:
            coef_value = PriceMarkCalc(coef).get_price_if_multiply(counted_coef)
            return coef_value
        else:
            return counted_coef


class Recipient:
    def __init__(self, name, date_frame=pd.DataFrame()):
        self.r_name = name
        self.litera = name[0]
        self.private_position = self.litera.lower()
        self.date_frame = date_frame.astype('str')
        self.mod_data = self.date_frame.copy()
        self.cat_data = pd.DataFrame(index=date_frame.index)
        self.positions = ['a', 'z', 'h', 'f']
        self.limit = len(date_frame.index)
        mini_frame = pd.DataFrame({'DATE': ['', ''], 'DAY': ['done_percent', 'sum']}, index=[self.limit, self.limit+1])
        self.result_frame = pd.concat([self.date_frame.copy(), mini_frame])

    def create_output_dir(self, path_to_output, month):
        paths = [f'{path_to_output}/{month}', f'{path_to_output}/{month}/{self.r_name}']
        for p in paths:
            try:
                os.mkdir(p)
            except FileExistsError:
                pass

    def get_and_collect_r_name_col(self, column, new_column_name=''):
        def extract_by_litera(day):
            if day:
                day = day.split(', ')
                day = [i[1:] if len(i) > 1 else '' for i in day if i[0] == self.litera]
                return ''.join(day)
            else:
                return ''

        self.mod_data[new_column_name] = column.map(extract_by_litera)

    def get_family_col(self):
        def is_family(r_children):
            return 'f' if r_children else ''
        self.mod_data['family'] = self.mod_data['children'].map(is_family)

    def get_children_coef_cols(self, KG_col, weak_col):
        def get_child_coefs(r_children, KG_coefs, weak_children, d8):
            child_coef_dict = {'child_coef': 0, 'KG_coef': 0, 'weak_coef': 0}
            if r_children:
                child_coef_dict['child_coef'] = len(r_children)
                if weak_children:
                    r_weak_children_list = [i for i in weak_children if i in r_children]
                    child_coef_dict['weak_coef'] = len(r_weak_children_list)
                if d8:
                    child_coef_dict = {name: child_coef_dict[name] / 2 for name in child_coef_dict}
                else:
                    if KG_coefs:
                        KG_l = KG_coefs.split(', ')
                        KG_coefs_list = [float(CompCoef(i).severity_dict['sev']) for i in KG_l if i[0] in r_children]
                        child_coef_dict['KG_coef'] = sum(KG_coefs_list)

            # print(r_children, weak_children, KG_coefs, d8)
            # print(child_coef_dict)

            return child_coef_dict

        coefs_list = list(map(get_child_coefs, self.mod_data['children'], KG_col, weak_col, self.mod_data['d8_coef']))
        for col_name in ['child_coef', 'KG_coef', 'weak_coef']:
            self.mod_data[col_name] = [i[col_name] for i in coefs_list]

    def get_duty_coefficients_col(self):
        def extract_duty_coefs(duty):
            if duty:
                duty_coef = CompCoef(duty).severity_dict
                return duty_coef['name'], duty_coef['sev']
            else:
                return ''

        duty_coef_list = list(map(extract_duty_coefs, self.mod_data['duty']))
        self.mod_data['d24_coef'] = [i[1] if 'd24' in i else '' for i in duty_coef_list]
        self.mod_data['d8_coef'] = [i[1] if 'd8' in i else '' for i in duty_coef_list]

    def get_place_coefficients_col(self):
        self.mod_data['dacha_coef'] = self.mod_data['place'].map(lambda i: 'd' in i)

    def get_sleepless_coef_col(self, vedomost):
        sleepless_col_name = self.private_position + ':siesta'
        self.mod_data['sleep_coef'] = list(map(lambda i: True if i != 'can`t' else False, vedomost[sleepless_col_name]))

    def get_r_positions_col(self):
        def extract_positions(children, place, family):
            positions = [i for i in list(children+place+family) if i in self.positions]
            positions.append(self.private_position)
            return positions

        self.mod_data['positions'] = list(map(extract_positions,
                                              self.mod_data['children'], self.mod_data['place'], self.mod_data['family']))

    def get_all_coefs_col(self):
        def get_coef_dict(row_of_coefs):
            row_of_coefs = {i.replace('_coef', ''): row_of_coefs[i] for i in row_of_coefs if row_of_coefs[i]}
            return row_of_coefs

        coef_frame = self.mod_data.get([i for i in self.mod_data if 'coef' in i])
        self.mod_data['coefs'] = list(map(get_coef_dict, coef_frame.to_dict('index').values()))

    def get_r_vedomost(self, recipients, categories):
        all_private_positions = [i[0].upper() for i in recipients]
        for column in categories:
            position = column[0].upper()
            double_category_flag = [i for i in categories[column] if type(i) == str and i[0] in all_private_positions]
            if double_category_flag:
                column_list = [PriceMarkCalc(result=i).prepare_named_result(self.r_name) for i in categories[column]]
                self.cat_data[column] = column_list
            else:
                if self.litera == position or position not in all_private_positions:
                    self.cat_data[column] = categories[column]
                    # здесь баги
        return self.cat_data

    def collect_to_result_frame(self, result_column, bonus_column=()):
        self.result_frame = pd.concat([self.result_frame, result_column], axis=1)
        if bonus_column:
            bonus_column = pd.Series(bonus_column, name=result_column.name+'_bonus')
            self.result_frame = pd.concat([self.result_frame, bonus_column], axis=1)

    def get_in_time_sleeptime_ser(self):
        def hour_extraction(time):
            hour = 0
            if time != '!':
                if ':' in time:
                    hour = int(time.split(':')[0])
                else:
                    hour = 21
            return hour

        sleep_time_ser_name = self.private_position + ':sleeptime'
        sleeptime_list = list(map(hour_extraction, self.cat_data[sleep_time_ser_name]))
        sleeptime_list = list(map(lambda i: 'True' if i > 20 else 'False', sleeptime_list))
        percent = len([i for i in sleeptime_list if i == 'True']) / len(sleeptime_list)
        sleeptime_list.extend([round(percent, 2), ''])
        return pd.Series(sleeptime_list, name='sleep_in_time')

    def get_result_frame_after_filter(self, filtered):
        self.result_frame = filtered
        return self.result_frame

    def get_day_sum_if_sleep_in_time_and_save(self, path):
        def get_day_sum(day_row, sleep_in_time_flag=''):
            percent_row_cell = day_row.pop('DAY')
            #print(day_row)
            if sleep_in_time_flag:
                if sleep_in_time_flag == 'False':
                    day_row = {i: day_row[i] if day_row[i] < 0 else 0 for i in day_row}
            if percent_row_cell == 'done_percent':
                return round(np.mean(np.array(list(day_row.values()))), 2)
            else:
                return round(sum(day_row.values()), 2)

        ff.items = list(self.result_frame.columns)
        ff.filtration([('part', 'bonus', 'neg'), ('part', 'DATE', 'neg')])
        only_categories_frame = ff.present_by_items(self.result_frame)
        default_sum_list = list(map(get_day_sum, only_categories_frame.to_dict('index').values()))
        self.result_frame['cat_day_sum'] = default_sum_list

        ff.items = list(self.result_frame.columns)
        ff.filtration([('part', 'bonus', 'pos')])
        bonus_frame = pd.concat([self.result_frame['DAY'], ff.present_by_items(self.result_frame)], axis=1)
        self.result_frame['day_bonus'] = list(map(get_day_sum, bonus_frame.to_dict('index').values()))

        print(self.result_frame)

        sleep_in_time_ser = self.get_in_time_sleeptime_ser()
        self.result_frame = pd.concat([self.result_frame, sleep_in_time_ser], axis=1)

        sum_after_0_list = list(map(get_day_sum, only_categories_frame.to_dict('index').values(), sleep_in_time_ser))
        sum_after_0_list = sum_after_0_list[:-2] # статистику пресчитаем отдельно
        day_sum_after_0 = round(sum(sum_after_0_list), 2)
        if not day_sum_after_0:
            done_percent_after_0 = 0.0
        else:
            done_percent_after_0 = round(day_sum_after_0/default_sum_list[-1], 2)

        sum_after_0_list.extend([done_percent_after_0, day_sum_after_0])
        print(self.result_frame)
        self.result_frame['day_sum_in_time'] = sum_after_0_list
        #self.result_frame.insert(2, 'coefs', self.mod_data['coefs'])
        self.result_frame.to_excel(path, index=False)


class MonthData:
    def __init__(self, path=''):
        self.path = path
        self.mother_frame = pd.DataFrame()
        self.prices = pd.DataFrame()
        self.accessory = pd.DataFrame()
        self.categories = pd.DataFrame()
        self.date = pd.DataFrame()

    def get_vedomost(self):
        self.mother_frame = pd.read_excel(self.path, sheet_name='vedomost', dtype='object')
        self.mother_frame = self.mother_frame.replace('CAN`T', 'can`t')
        self.mother_frame['DATE'] = [i.date() for i in self.mother_frame['DATE']]
        return self.mother_frame

    @property
    def vedomost(self):
        return self.mother_frame

    @vedomost.setter
    def vedomost(self, df):
        self.mother_frame = df

    def get_price_frame(self, path=''):
        if not path:
            self.prices = pd.read_excel(self.path, sheet_name='price', index_col=0).fillna(0)
        else:
            self.prices = pd.read_excel(path, sheet_name='price', index_col=0).fillna(0)

    def get_frames_for_working(self, limiting=''):
        if limiting:
            if limiting == 'for count':
                ff.items = self.mother_frame['DONE'].to_list()
                ff.filtration([('=', 'Y', 'pos')], behavior='index_values')
                self.mother_frame = ff.present_by_items(self.mother_frame)
                del self.mother_frame['DONE']
            elif limiting == 'for filling':
                ff.items = self.mother_frame['DONE'].to_list()
                ff.filtration([('=', 'Y', 'neg')], behavior='index_values')
                self.mother_frame = ff.present_by_items(self.mother_frame)

        date_keys = ['DATE', 'DAY']
        self.accessory = self.mother_frame.get([i for i in self.mother_frame.columns if i == i.upper() and i not in date_keys])
        self.date = self.mother_frame.get(date_keys)
        self.categories = self.mother_frame.get([i for i in self.mother_frame if i == i.lower()])

    def fill_na(self):
        self.accessory.fillna('-')
        self.categories.fillna('!')


class CategoryData:
    def __init__(self, cf, mf, pf, date_frame=''):
        self.name = cf.name
        change_dict = {'T': '+'}
        self.cat_frame = pd.DataFrame([change_dict[i] if i in change_dict else i for i in cf], columns=[self.name], dtype='str')
        self.position = self.name[0]
        self.price_frame = pf[self.name]
        self.mod_frame = mf

    def find_a_price(self, result, positions):
        mark = 'can`t'
        if self.position not in positions:
            return {'price': 0, 'mark': mark, 'price_calc': 'not in positions'}

        price_calc = {'price': self.price_frame['PRICE'], 'can`t': 0, 'wishn`t': 0, '!': -50}
        if result not in price_calc:
            price = PriceMarkCalc(result, price_calc['price']).get_price()
        else:
            price = price_calc[result]

        true_condition = eval(str(price)+self.price_frame["True"])
        #print(true_condition)
        mark = 'True' if true_condition else 'False'

        #print(result, price, mark, '\n end \n')
        price_calc = {k: price_calc[k] for k in price_calc if k not in ('can`t', 'wishn`t')}
        return {'price': price, 'mark': mark, 'price_calc': list(price_calc.values())}


    def add_price_column(self, show_calculation=False):
        #print(self.name)
        price_list = list(map(self.find_a_price,
                              self.cat_frame[self.name],
                              self.mod_frame['positions']))
        self.cat_frame['price'] = [i.pop('price') for i in price_list]
        self.cat_frame['mark'] = [i.pop('mark') for i in price_list]

        if show_calculation:
            self.cat_frame.insert(self.cat_frame.columns.get_loc('price'), 'price_calc', self.price_frame['PRICE'])
        #print(self.cat_frame)
        return self.cat_frame

    def count_a_modification(self, coefs, mark): # сюда нужно интегрировать марки
        coef_dict = {'coef': 0}
        if mark not in ('True', 'False'):
            return coef_dict

        for coef_name in coefs:
            coef = CompCoef(self.price_frame[coef_name])
            if coef.have_coef_data:
                coef_value = coef.count_a_coef_value(coefs[coef_name], mark)
                coef_dict[coef_name] = coef_value
            else:
                coef_dict[coef_name] = 0
        coef_dict['coef'] = sum(coef_dict.values())
        return coef_dict

    def total_count(self, price, coef, mark):
        # if mark == 'True' and coef > 0.5 and price == 0:
        #     coef = abs(50) * coef
        # else:
        coef = abs(price) * coef
        price += coef
        return round(coef, 2), round(price, 2)

    def add_coef_and_result_column(self, show_calculation=False):
        coefs_list = list(map(self.count_a_modification, self.mod_frame['coefs'].copy(), self.cat_frame['mark']))
        self.cat_frame['coef'] = [i.pop('coef') for i in coefs_list]
        #print(self.cat_frame)
        result_list = list(map(self.total_count, self.cat_frame['price'], self.cat_frame['coef'], self.cat_frame['mark']))
        self.cat_frame['mod'] = [i[0] for i in result_list]
        self.cat_frame['result'] = [i[1] for i in result_list]
        if show_calculation:
            self.cat_frame.insert(self.cat_frame.columns.get_loc('coef'), 'coef_count', coefs_list)

        return self.price_frame

    def get_ready_and_save_to_excel(self, date_frame, path):
        self.cat_frame = pd.concat([date_frame, self.cat_frame], axis='columns')
        self.cat_frame.set_index('DATE').to_excel(path)

    def get_result_col_with_statistic(self):
        def count_true_percent(mark_column):
            not_cant_mark_list = [i for i in mark_column if i != 'can`t']
            true_list = [i for i in mark_column if i == 'True']
            percent = len(true_list) / len(not_cant_mark_list)
            return round(percent, 2)

        true_percent = count_true_percent(self.cat_frame['mark'])
        index_limit = len(self.cat_frame.index)
        result = round(self.cat_frame['result'].sum(), 2)
        statistic_app = pd.Series({index_limit: true_percent, index_limit+1: result})
        result_column = pd.concat([self.cat_frame['result'], statistic_app], axis=0)
        result_column.name = self.name
        return result_column


class BonusFrame:
    def __init__(self, cat_frame, price_frame):
        self.name = price_frame.name
        self.logic = price_frame['logic']
        self.interval = int(price_frame['N'])
        self.bonus = float(price_frame['bonus'])
        self.mark_ser = pd.Series(cat_frame['mark'])
        all_True_exept_cant = lambda i: 'True' if i != 'can`t' else i
        self.max_bonus_ser = self.mark_ser.map(all_True_exept_cant)
        # self.max_bonus_ser = pd.Series(['can`t' if i == 'can`t' else 'True' for i in self.mark_ser])
        self.bonus_list = [0] * len(self.mark_ser)

    @property
    def tools(self):
        return {'every N': self.every_n_give_a_bonus}

    def has_bonus_logic(self):
        flag = True if self.logic else False
        return flag

    def every_n_give_a_bonus(self, mark_dict, bonus_list):
        counter = 1
        for k in mark_dict:
            k_index = list(mark_dict.keys()).index(k)
            if mark_dict[k] == 'True':
                if counter < self.interval:
                    if k_index + (self.interval-counter+1) > len(mark_dict):
                        bonus_list[k] = round(self.bonus / self.interval * counter)
                        counter = 1
                    else:
                        bonus_list[k] = mark_dict[k]
                        counter += 1
                else:
                    bonus_list[k] = self.bonus
                    counter = 1

            elif mark_dict[k] == 'False':
                bonus_list[k] = mark_dict[k]
                counter = 1

        return bonus_list

    def count_a_bonus(self, mark_ser=pd.Series()):
        if not mark_ser.empty:
            mark_dict = mark_ser.to_dict()
        else:
            mark_dict = self.mark_ser.to_dict()

        mark_dict = {k: mark_dict[k] for k in mark_dict if mark_dict[k] not in ('can`t', 'wishn`t')}
        bonus_list = self.tools[self.logic](mark_dict, self.bonus_list.copy())

        return bonus_list

    def get_bonus_list_with_statistic(self):
        self.bonus_list = [0 if type(i) == str else i for i in self.count_a_bonus()]
        max_bonus_list = [0 if type(i) == str else i for i in self.count_a_bonus(self.max_bonus_ser)]
        bonus_count = len([i for i in self.bonus_list if i])
        max_bonus_count = len([i for i in max_bonus_list if i])
        try:
            true_percent = round(bonus_count / max_bonus_count, 2)
        except ZeroDivisionError:
            true_percent = 0

        self.bonus_list.append(sum(self.bonus_list))
        self.bonus_list.insert(-1, true_percent)
        return self.bonus_list
