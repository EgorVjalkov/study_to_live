import pandas as pd
from statistics import mean
import os
from PriceMarkCalc import PriceMarkCalc
from utils import analytic_utilities as au

pd.set_option('display.max.columns', None)


ff = au.FrameForAnalyse()


class CompCoef:
    def __init__(self, coef_data):
        self.coef_data = coef_data

    def __repr__(self):
        return f'CompCoef(coef_data={self.coef_data})'

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
    def __init__(self, name, date_ser=pd.Series()):
        self.r_name = name
        self.litera = name[0]
        self.private_position = self.litera.lower()
        self.mod_data = pd.DataFrame(date_ser, columns=[date_ser.name], index=date_ser.index)
        self.cat_data = pd.DataFrame(index=date_ser.index)
        self.positions = ['a', 'z', 'h', 'f']
        mini_frame = pd.DataFrame({'DAY': ['done_percent', 'sum']}, index=[0, 1])
        self.result_frame = pd.concat([self.mod_data, mini_frame])

    @property
    def rename_dict(self):
        return {'COM': 'children', 'PLACE': 'place', 'DUTY': 'duty'}

    def create_output_dir(self, path_to_output, month):
        paths = [f'{path_to_output}/{month}', f'{path_to_output}/{month}/{self.r_name}']
        for p in paths:
            try:
                os.mkdir(p)
            except FileExistsError:
                pass

    def get_and_collect_r_name_col(self, column, new_column_name=''):
        def extract_by_litera(day):
            data = ''
            day = day.split(', ')
            for d in day:
                #print(d)
                if self.litera in d:
                    data = [i for i in list(d) if not i.isupper()]
                    #print(data)
                    data = ''.join(data)
            return data

        self.mod_data[new_column_name] = column.map(extract_by_litera)

    def get_with_children_col(self):
        def with_children(r_children):
            return 'f' if r_children else ''
        self.mod_data['w_children'] = self.mod_data['children'].map(with_children)

    def get_full_family_col(self, commands_col: pd.Series):
        #print(commands_col)
        self.mod_data['full_family'] = commands_col.map(lambda i: len(i.split()) < 2)

    def get_children_coef_cols(self, KG_col, weak_col):
        def get_child_coefs(r_children, KG_coefs, weak_children, d8):
            child_coef_dict = {'child_coef': 0, 'KG_coef': 0, 'weak_coef': 0}
            if r_children:
                child_coef_dict['child_coef'] = len(r_children)
                if weak_children: # можно заморочиться здесь
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
        if sleepless_col_name in vedomost:
            self.mod_data['sleep_coef'] = vedomost[sleepless_col_name].map(lambda i: i not in ['can`t', '!'])

    def get_r_positions_col(self):
        def extract_positions(children, place, family):
            positions = [i for i in list(children+place+family) if i in self.positions]
            positions.append(self.private_position)
            return positions

        self.mod_data['positions'] = list(map(extract_positions,
                                              self.mod_data['children'],
                                              self.mod_data['place'],
                                              self.mod_data['w_children']))

    def get_all_coefs_col(self):
        def get_coef_dict(row_of_coefs):
            row_of_coefs = {i.replace('_coef', ''): row_of_coefs[i] for i in row_of_coefs if row_of_coefs[i]}
            return row_of_coefs

        #print(self.mod_data.columns)
        coef_frame = self.mod_data.get([i for i in self.mod_data if 'coef' in i])
        self.mod_data['coefs'] = list(map(get_coef_dict, coef_frame.to_dict('index').values()))

    def extract_data_by_recipient(self, acc_frame: pd.DataFrame):
        columns = list(self.rename_dict.keys())
        for column in acc_frame.get(columns):
            self.get_and_collect_r_name_col(acc_frame[column], self.rename_dict[column])

    def get_mod_frame(
            self,
            acc_frame: pd.DataFrame,
            categories_frame: pd.DataFrame,
            ) -> pd.DataFrame:
        self.extract_data_by_recipient(acc_frame)
        self.get_full_family_col(acc_frame['COM'])
        self.get_with_children_col()
        self.get_duty_coefficients_col()
        self.get_children_coef_cols(acc_frame['KG'], acc_frame['WEAK'])
        self.get_place_coefficients_col()
        self.get_sleepless_coef_col(categories_frame)
        self.get_r_positions_col()
        self.get_all_coefs_col()
        return self.mod_data

    def get_r_vedomost(self, recipients, categories):
        all_private_positions = [i[0].upper() for i in recipients]
        for column in categories:
            position = column[0].upper()
            # здесь можно упростить, т.. к. мы уже сделали пометки где есть личные отметки а где нет
            double_category_flag = [i for i in categories[column] if str(i)[0] in all_private_positions]
            if double_category_flag:
                #print(categories[column])

                column_list = [PriceMarkCalc(result=i).prepare_named_result(self.r_name)
                               for i in categories[column]]
                self.cat_data[column] = column_list
            else:
                if self.litera == position or position not in all_private_positions:
                    self.cat_data[column] = categories[column]
        return self.cat_data

    def collect_to_result_frame(self, result_column, bonus_column: pd.Series):
        self.result_frame = pd.concat([self.result_frame, result_column], axis=1)
        if not bonus_column.empty:
            self.result_frame[bonus_column.name] = bonus_column

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
        return pd.Series(sleeptime_list, name='sleep_in_time', index=self.result_frame.index)

    def get_result_frame_after_filter(self, filtered):
        self.result_frame = filtered
        return self.result_frame

    def get_day_sum_if_sleep_in_time_and_save(self, path, demo_mode):
        def get_day_sum(day_row, sleep_in_time_flag=''):
            percent_row_cell = day_row.pop('DAY')
            day_row = [0 if isinstance(day_row[i], str) else day_row[i]
                       for i in day_row]
            if sleep_in_time_flag:
                if sleep_in_time_flag == 'False':
                    day_row = [i if i < 0 else 0 for i in day_row]
            if percent_row_cell == 'done_percent':
                return round(mean(day_row), 2)
            else:
                return round(sum(day_row), 2)

        ff.items = list(self.result_frame.columns)
        ff.filtration([('part', 'bonus', 'neg'),
                       ('part', 'fire', 'neg')])
        only_categories_frame = ff.present_by_items(self.result_frame)
        default_sum_list = list(map(get_day_sum,
                                    only_categories_frame.to_dict('index').values()))
        self.result_frame['cat_day_sum'] = default_sum_list

        ff.items = list(self.result_frame.columns)
        ff.filtration([('part', 'bonus', 'pos')])
        bonus_frame = pd.concat([self.result_frame['DAY'], ff.present_by_items(self.result_frame)], axis=1)
        self.result_frame['day_bonus'] = list(map(get_day_sum,
                                                  bonus_frame.to_dict('index').values()))

        sleep_in_time_ser = self.get_in_time_sleeptime_ser()
        self.result_frame = pd.concat(
            [self.result_frame, sleep_in_time_ser],
            axis=1)


        sum_after_0_col = pd.Series(
            list(map(get_day_sum,
                     only_categories_frame.to_dict('index').values(),
                     sleep_in_time_ser)),
            index=self.result_frame.index)

        sum_after_0_col = sum_after_0_col[:-2] # статистику пресчитаем отдельно
        day_sum_after_0 = sum_after_0_col.sum()
        if not day_sum_after_0:
            done_percent_after_0 = 0.0
        else:
            done_percent_after_0 = round(day_sum_after_0/default_sum_list[-1], 2)

        sum_after_0_col = pd.concat(
            [sum_after_0_col, pd.Series([done_percent_after_0, day_sum_after_0])],
            axis=0)
        self.result_frame['day_sum_in_time'] = sum_after_0_col
        if not demo_mode:
            self.result_frame.to_excel(path, index=False)


class MonthData:
    def __init__(self, mother_frame=pd.DataFrame(), prices=pd.DataFrame):
        self.mother_frame = mother_frame
        self.prices = prices
        self.accessory = pd.DataFrame()
        self.categories = pd.DataFrame()
        self.date = pd.DataFrame()

    def get_frames_for_working(self) -> object:
        self.mother_frame = self.mother_frame[self.mother_frame['STATUS'] == 'Y']

        self.accessory = self.mother_frame.get(
            [i for i in self.mother_frame.columns if i == i.upper() and i != 'DAY'])

        self.date = self.mother_frame['DAY']

        self.categories = self.mother_frame.get(
            [i for i in self.mother_frame if i == i.lower()])

        return self

    def fill_na(self) -> object:
        self.accessory = self.accessory.fillna('-')
        self.categories = self.categories.fillna('!')
        self.prices = self.prices.fillna(0)
        return self


class CategoryData:
    def __init__(self, cf, mf, pf, recipient, date_frame=''):
        self.name = cf.name
        self.recipient = recipient
        change_dict = {'T': '+'}
        self.cat_frame = pd.DataFrame(
            [change_dict[i] if i in change_dict else i for i in cf],
            columns=[self.name],
            index=cf.index,
            dtype='str')
        self.position = self.name[0]
        self.price_frame = pf[self.name]
        self.mod_frame = mf

    @property
    def is_not_private_category(self):
        return self.recipient[0].lower() != self.name[0]

    def find_a_price(self, result, positions):
        if self.position not in positions:
            return {'price': 'can`t', 'price_calc': 'not in positions'}

        price_calc = {
            'price': self.price_frame.at['PRICE'],
            'can`t': 0,
            'wishn`t': 0,
            '!': -50}
        if result in price_calc:
            if result in ['can`t', 'wishn`t']:
                price = result
            else:
                price = price_calc[result]
        else:
            price = PriceMarkCalc(result, price_calc['price']).get_price()

        return {'price': price, 'price_calc': price_calc['price']}

    def add_price_column(self, show_calculation=False):
        #print(self.name)
        price_list = list(map(self.find_a_price,
                              self.cat_frame[self.name],
                              self.mod_frame['positions']))
        self.cat_frame['price'] = [i.pop('price') for i in price_list]
        price_list = [i.pop('price_calc') for i in price_list]
        if show_calculation:
            self.cat_frame.insert(self.cat_frame.columns.get_loc('price'),
                                  'price_calc',
                                  pd.Series(price_list))

    def get_a_mark(self, price):
        if not isinstance(price, str):
            true_condition = str(price)+self.price_frame.at["True"]
            mark = str(eval(true_condition))[0]
            mark_calc = true_condition
        else:
            mark_calc = price
            if price == 'wish`t':
                mark = 'F'
            else:
                mark = price
        return {'mark': mark, 'mark_calc': mark_calc}

    def add_mark_column(self, show_calculation=False):
        mark_list = list(map(self.get_a_mark,
                             self.cat_frame['price']))
        self.cat_frame['mark'] = [i.pop('mark') for i in mark_list]
        mark_list = [i.pop('mark_calc') for i in mark_list]
        if show_calculation:
            self.cat_frame.insert(self.cat_frame.columns.get_loc('mark'),
                                  'mark_calc',
                                  pd.Series(mark_list))

    def count_a_modification(self, coefs, mark):
        coef_dict = {'coef': 0}
        if mark not in ('T', 'F'):
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

    def total_count(self, price, coef, full_family_flag):
        if price in ['can`t', 'wishn`t']:
            return coef, price
        else:
            coef = abs(price) * coef
            if full_family_flag and price > 0 and self.is_not_private_category:
                reduced_price = 0.5 * price
                coefed_price = reduced_price + coef
                print(f'{price} --> {reduced_price}')
            else:
                coefed_price = price + coef
            return round(coef, 2), round(coefed_price, 2)

    def add_coef_and_result_column(self, show_calculation=False):
        coefs_list = list(map(self.count_a_modification,
                              self.mod_frame['coefs'].copy(),
                              self.cat_frame['mark']))
        self.cat_frame['coef'] = [i.pop('coef') for i in coefs_list]

        result_list = list(map(self.total_count,
                               self.cat_frame['price'],
                               self.cat_frame['coef'],
                               self.mod_frame['full_family']))
        self.cat_frame['mod'] = [i[0] for i in result_list]
        self.cat_frame['result'] = [i[1] for i in result_list]
        # self.cat_frame['reduced'] = [i[2] for i in result_list] #
        # self.cat_frame['full'] = self.mod_frame['full_family'] #

        if show_calculation:
            self.cat_frame.insert(self.cat_frame.columns.get_loc('coef'),
                                  'coef_count',
                                  pd.Series(coefs_list))

    def get_ready_and_save_to_excel(self, date_frame, path, demo_mode):
        self.cat_frame = pd.concat([date_frame, self.cat_frame], axis='columns')
        if not demo_mode:
            self.cat_frame.to_excel(path)

    def get_result_col_with_statistic(self):
        def count_true_percent(mark_column):
            not_cant_mark_list = [i for i in mark_column if i != 'can`t']
            true_list = [i for i in mark_column if i == 'T']
            percent = len(true_list) / len(not_cant_mark_list)
            return round(percent, 2)

        true_percent = count_true_percent(self.cat_frame['mark'])
        result_ser = self.cat_frame['result'].map(lambda i: 0 if isinstance(i, str) else i)
        result = round(result_ser.sum(), 2)
        statistic_app = pd.Series([true_percent, result])
        result_column = pd.concat([self.cat_frame['result'], statistic_app], axis=0)
        result_column.name = self.name
        return result_column

