import pandas as pd
from ComplexCondition import ComplexCondition
import numpy as np
pd.set_option('display.max.columns', None)


class Recipient:
    def __init__(self, name, date_frame):
        self.r_name = name
        self.litera = name[0]
        self.private_position = self.litera.lower()
        self.mod_data = date_frame.copy()
        self.cat_data = date_frame.copy()

        self.positions = ['z', 'a', 'h', 'e', 'l']
        self.coefficients = ['KG', 'KGD', 'g', 'd24', 'd8']

    def get_and_collect_r_name_col(self, column, new_column_name=''):
        def extract_by_litera(day):
            day = day.split(', ')
            day = {i[0]: i[1:] if len(i) > 1 else '' for i in day}
            return day[self.litera]

        self.mod_data[new_column_name] = column.map(extract_by_litera)

    def get_r_positions_col(self):
        def extract_positions(children, place):
            positions = [i for i in list(children+place) if i in self.positions]
            positions.append(self.private_position)
            return positions

        self.mod_data['positions'] = list(map(extract_positions, self.mod_data['children'], self.mod_data['place']))

    def get_children_coef(self, KG_col):
        def extract_KG_coefs(r_children, KG_coefs):
            child_coefs_list = False
            if all([r_children, KG_coefs]):
                child_coefs_list = [i[1:] for i in KG_coefs.split(', ') if i[0] in r_children]
            return child_coefs_list

        self.mod_data['KG_coefs'] = list(map(extract_KG_coefs, self.mod_data['children'], KG_col))
        self.mod_data['child_coef'] = self.mod_data['children'].map(len)

    def get_duty_coefficients_col(self):
        def extract_duty_coefs(place):
            if place[0] == 'd':
                duty, severity = tuple(place.replace(')', '').split('('))
                return duty, severity
            else:
                return False

        self.mod_data['duty_coef'] = list(map(extract_duty_coefs, self.mod_data['place']))

    def get_weak_coefficients_col(self, weak_col):
        def count_weak_num(r_children, weak_children):
            r_weak_list = []
            if all([r_children, weak_children]):
                r_weak_list = [i for i in weak_children if i in r_children]
            return len(r_weak_list)

        self.mod_data['weak_coef'] = list(map(count_weak_num, self.mod_data['children'], weak_col))

    def get_coefs_col(self):
        def get_coef_dict(row_of_coefs):
            row_of_coefs = {i[0].upper(): row_of_coefs[i] for i in row_of_coefs}
            return row_of_coefs

        coef_frame = self.mod_data.get([i for i in self.mod_data if 'coef' in i])
        self.mod_data['coefs'] = list(map(get_coef_dict, coef_frame.to_dict('index').values()))
        print(self.r_name)
        print(self.mod_data)


class MonthData:
    def __init__(self, path, recipients):
        vedomost = pd.read_excel(path, sheet_name='vedomost', dtype='object').fillna(False)
        self.prices = pd.read_excel(path, sheet_name='price', index_col=0).fillna(0)
        self.limit = len([i for i in vedomost['DONE'].to_list() if i])
        self.vedomost = vedomost[0:self.limit]
        del self.vedomost['DONE']

        date_keys = ['DATE', 'DAY']
        self.accessory = self.vedomost.get([i for i in self.vedomost.columns if i == i.upper() and i not in date_keys])
        self.date = self.vedomost.get(date_keys)
        self.categories = self.vedomost.get([i for i in self.vedomost if i == i.lower()])

        self.recipients_mod = {k: self.date.copy() for k in recipients}
        self.recipients_cat = self.recipients_mod.copy()

        date_frame_for_result_frame = self.date.copy().astype('str')
        mini_frame = pd.DataFrame({'DATE': ['', ''], 'DAY': ['done_percent', 'sum']}, index=[self.limit, self.limit+1])
        self.date_frame = pd.concat([date_frame_for_result_frame, mini_frame])
        self.result_frame = {k: self.date_frame for k in recipients}



    def get_result_column(self, column_name, mark_column=pd.Series(), result_column=pd.Series()):
        def count_true_percent(mark_column):
            not_cant_mark_list = [i for i in mark_column if i != 'can`t']
            true_list = [i for i in mark_column if i == 'True']
            percent = len(true_list) / len(not_cant_mark_list)
            return int(percent * 100)

        true_percent = count_true_percent(mark_column)
        if result_column.empty:
            mark_column = pd.concat([mark_column, pd.Series({self.limit: true_percent, self.limit+1: ''})], axis=0)
            mark_column.name = column_name
            return mark_column
        else:
            result = round(result_column.sum(), 2)
            total_ser = pd.Series({self.limit: true_percent, self.limit+1: result})
            result_column = pd.concat([result_column, total_ser], axis=0)
            result_column.name = column_name
            return result_column

    def collect_to_result_frame(self, name, column_name, result_column, mark_column, bonus_column=()):
        #print(self.result_frame[name])
        new_column = self.get_result_column(column_name, mark_column, result_column)
        self.result_frame[name] = pd.concat([self.result_frame[name], new_column], axis=1)
        if bonus_column:
            bonus_column = pd.Series(bonus_column, name=column_name+'_bonus')
            self.result_frame[name] = pd.concat([self.result_frame[name], bonus_column], axis=1)
        #print(self.result_frame[name])
        return self.result_frame

    def get_day_sum_if_sleep_in_time(self, name, sleep_in_time_ser):
        def get_day_sum(day_row, sleep_in_time_flag=''):
            percent_row_cell = day_row.pop('DAY')
            #print(day_row)
            if sleep_in_time_flag:
                if sleep_in_time_flag == 'False':
                    day_row = {i: day_row[i] if day_row[i] < 0 else 0 for i in day_row if 'bonus' not in i}
                    day_bonus = {i: day_row[i] for i in day_row if 'bonus' in i}
                    day_row.update(day_bonus)
            if percent_row_cell == 'done_percent':
                return np.mean(np.array(list(day_row.values())))
            else:
                return round(sum(day_row.values()), 2)

        categories = [i for i in self.result_frame[name].columns if i.islower() or i == 'DAY']
        only_categories_frame = self.result_frame[name][categories].copy()

        default_sum = pd.Series(list(map(get_day_sum, only_categories_frame.to_dict('index').values())), name='day_sum')
        self.result_frame[name] = pd.concat([self.result_frame[name], default_sum], axis=1)

        sleep_in_time_ser = self.get_result_column(sleep_in_time_ser.name, sleep_in_time_ser)
        self.result_frame[name] = pd.concat([self.result_frame[name], sleep_in_time_ser], axis=1)

        day_sum_after_0_ser = list(map(get_day_sum, only_categories_frame.to_dict('index').values(), sleep_in_time_ser))
        day_sum_after_0_ser = pd.Series(day_sum_after_0_ser[:-2]) # статистику пресчитаем отдельно
        sum_after_0 = round(day_sum_after_0_ser.sum(), 2)
        done_percent_after_0 = round(sum_after_0/default_sum[self.limit+1], 2) * 100
        total_statistic = pd.Series({self.limit: done_percent_after_0, self.limit+1: sum_after_0})
        day_sum_after_0_ser = pd.concat([day_sum_after_0_ser, total_statistic], axis=0)
        day_sum_after_0_ser.name = 'day_sum_in_time'
        self.result_frame[name] = pd.concat([self.result_frame[name], day_sum_after_0_ser], axis=1)


class AccessoryData:
    def __init__(self, af, vedomost, recipients):
        self.af = af
        self.vedomost = vedomost
        self.mods_frame = {}
        self.positions_logic = {
            'duty24': {'Lera': ['A', 'Z', 'H', 'L'], 'Egr': ['E']},
            'duty24, M': {'Lera': ['A', 'Z', 'L'], 'Egr': ['E']},
            'V': {'Lera': ['A', 'Z', 'L'], 'Egr': ['A', 'Z', 'E']},
            'M': {'Lera': ['A', 'Z', 'L'], 'Egr': ['E', 'H']},
            '': {'Lera': ['A', 'Z', 'H', 'L'], 'Egr': ['A', 'Z', 'H', 'E']}
        }
        self.children_positions = ('A', 'Z')
        self.named_coefficients = {'Egr': ['DIF_DUTY', 'Egr_sleepless'], 'Lera': ['Lera_sleepless']}
        self.recipients = recipients

    def get_mods_frame(self):
        self.mods_frame = pd.DataFrame(index=self.af.index)
        self.mods_frame['duty'] = ['duty' + str(int(i)) if i else i for i in self.af['DUTY']]
        self.mods_frame['zlata_mod'] = self.af['MOD']
        self.mods_frame['weak_mod'] = ['WEAK' + str(int(i)) if i else i for i in self.af['WEAK']]
        self.mods_frame['DIF_DUTY'] = [{'DIF_DUTY': str(int(i))} if i else i for i in self.af['DIF_DUTY']]

        def get_sleepless_col(recipient, vedomost):
            sleepless_ser_name = recipient[0].lower() + ':siesta'
            sleepless_ser = list(map(lambda i: 'SLEEP' if i else False, vedomost[sleepless_ser_name]))
            return pd.Series(sleepless_ser, name=f'{recipient}_sleepless')

        def get_in_time_sleeptime_col(recipient, vedomost):
            def hour_extraction(time):
                hour = 0
                if time:
                    if ':' in time:
                        hour = int(time.split(':')[0])
                    else:
                        hour = 21
                return hour

            sleep_time_ser_name = recipient[0].lower() + ':sleeptime'
            sleeptime_ser = list(map(hour_extraction, vedomost[sleep_time_ser_name]))
            before_0 = lambda i: 'True' if i > 20 else 'False'
            sleeptime_ser = list(map(before_0, sleeptime_ser))
            return pd.Series(sleeptime_ser, name=recipient + '_sleep_in_time')

        for name in self.recipients:
            self.mods_frame = pd.concat([self.mods_frame, get_sleepless_col(name, self.vedomost)], axis=1)
            self.mods_frame = pd.concat([self.mods_frame, get_in_time_sleeptime_col(name, self.vedomost)], axis=1)

        def f_for_positions(*mods):
            #print(mods)
            mods = ['' if i == 'duty8' else i for i in mods]
            mods_key = ', '.join([i for i in mods if i])
            if mods_key not in self.positions_logic:
                if 'duty24' in mods_key:
                    mods_key = 'duty24'
                else:
                    mods_key = ''
            #print(mods_key)
            return self.positions_logic[mods_key]
        self.mods_frame['positions'] = list(map(f_for_positions,
                                                self.mods_frame['duty'],
                                                self.mods_frame['zlata_mod']))

        def with_children(positions):
            recipient_list = []
            for r in positions:
                pos = [i for i in positions[r] if i in self.children_positions]
                if pos:
                    recipient_list.append(r)
            return recipient_list
        self.mods_frame['with_children'] = list(map(with_children, self.mods_frame['positions']))

        mods_for_coef = self.mods_frame.get([i for i in self.mods_frame.columns if 'mod' in i])
        mods_for_coef = mods_for_coef.to_dict('index')
        #print(mods_for_coef)
        all_named_mods = []
        x = [all_named_mods.extend(i) for i in self.named_coefficients.values()]
        named_mods = self.mods_frame.get(all_named_mods).to_dict('index')
        #print(named_mods)
        # print(mods_for_coef)
        # print(named_mods)
# замуть в этой функции
        def named_coefs(positions, duty, with_children, coef_dict, named_coefs):
            new_coef_dict = {k: coef_dict.copy() for k in list(positions.keys())}
            #print(new_coef_dict)
            for r in new_coef_dict:
                if r not in with_children:
                    if duty == 'duty24':
                        new_coef_dict[r].clear()
                    else:
                        del new_coef_dict[r]['weak_mod']
                if duty == 'duty8':
                    new_coef_dict[r].update({'duty': duty})
                r_coefs = {k: named_coefs[k] for k in named_coefs if k in self.named_coefficients[r] if named_coefs[k]}
                new_coef_dict[r].update(r_coefs)
                new_coef_dict[r] = [i for i in list(new_coef_dict[r].values()) if i]

            #print(new_coef_dict)
            return new_coef_dict
        self.mods_frame['named_coefs'] = list(map(named_coefs,
                                                  self.mods_frame['positions'],
                                                  self.mods_frame['duty'],
                                                  self.mods_frame['with_children'],
                                                  mods_for_coef.values(),
                                                  named_mods.values()))


class CategoryData:
    def __init__(self, active_recipient, cf, mf, pf, date_frame=''):
        self.active_recipient = active_recipient
        self.name = cf.name
        self.cat_frame = pd.DataFrame([True if i == 'T' else i for i in cf], columns=[self.name], dtype='str')
        self.position = self.name[0].upper()
        self.price_frame = pf[self.name]
        self.mod_frame = mf
        self.bonus_logic = self.price_frame['bonus']

    def find_a_price(self, duty, result, positions):
        #print(positions)
        done_mark = 'can`t'
        if self.position not in positions:
            return {'price': 0, 'mark': done_mark, 'price_calc': 'not in positions'}

        price_calc = {'True': self.price_frame['True'], 'False': self.price_frame['False'], 'can`t': 0, 'wishn`t': 0}
        # can`t - невозможно сделать по уважительной причине, wishn`t - сделал другой, при совместных категориях
        if duty:
            price_calc['duty'] = duty
            price_calc['False'] = self.price_frame['dutyFalse']
            price_calc['True'] = self.price_frame['dutyTrue']
        #print(self.name)
        #print(result, type(result), price_calc[True])
        if result not in price_calc:
            price = ComplexCondition(result, price_calc['True']).get_price()
            done_mark = 'True' if price >= 0 else 'False'
        else:
            price = price_calc[result]
            done_mark = result
        #print(price)
        price_calc = {k: price_calc[k] for k in price_calc if k not in ('can`t', 'wishn`t')}

        return {'price': price, 'mark': str(done_mark), 'price_calc': list(price_calc.values())}

    def add_price_column(self, show_calculation=False):
        self.cat_frame['positions'] = self.mod_frame['positions'].map(lambda e: e[self.active_recipient])
        price_list = list(map(self.find_a_price,
                              self.mod_frame['duty'],
                              self.cat_frame[self.name],
                              self.cat_frame['positions']))
        self.cat_frame['price'] = [i.pop('price') for i in price_list]
        self.cat_frame['mark'] = [i.pop('mark') for i in price_list]
        if show_calculation:
            price_list = [list(i.values())[0] for i in price_list]
            self.cat_frame.insert(self.cat_frame.columns.get_loc('price'), 'price_calc', price_list)
            #print(self.cat_frame)
            #print(self.mod_frame[['zlata_mod', 'duty_mod', 'positions']])
        return self.cat_frame

    def count_a_modification(self, coefs):
        recipient_coefs = coefs[self.active_recipient]
        #print(recipient_coefs)
        coefficient_list = recipient_coefs.copy()
        coefficient_dict = {}
        for coef in coefficient_list:
            if type(coef) == dict:
                named_coef = coef
                key, value = list(named_coef)[0], coef[list(named_coef)[0]]
                price_data = self.price_frame[key]
                named_coef = eval(price_data)[value] if type(price_data) == str else price_data
                coefficient_dict[key] = named_coef
                del coefficient_list[coefficient_list.index(coef)]
        coefficient_dict.update({i: self.price_frame[i] if i in self.price_frame else 1 for i in coefficient_list})
        coefficient_dict['coef'] = np.array(list(coefficient_dict.values())).prod()
        #print(coefficient_dict)
        return coefficient_dict

    def total_count(self, price, coef):
        if price > 0:
            price *= coef
        return round(price, 2)

    def add_coef_and_result_column(self, show_calculation=False):
        coefs_list = list(map(self.count_a_modification, self.mod_frame['named_coefs'].copy()))
        self.cat_frame['coef'] = [i.pop('coef') for i in coefs_list]
        self.cat_frame['result'] = list(map(self.total_count, self.cat_frame['price'], self.cat_frame['coef']))
        if show_calculation:
            self.cat_frame.insert(self.cat_frame.columns.get_loc('coef'), 'with_children', self.mod_frame['with_children'])
            self.cat_frame.insert(self.cat_frame.columns.get_loc('coef'), 'coef_count', coefs_list)
        return self.price_frame


class BonusFrame:
    def __init__(self, cat_frame, price_frame):
        self.name = price_frame.name
        self.logic = price_frame['logic']
        self.interval = price_frame['N']
        self.bonus = price_frame['bonus']
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
            if mark_dict[k] == 'True':
                if counter != self.interval:
                    counter += 1
                else:
                    bonus_list[k] = self.bonus
                    counter = 1
                    # print(bonus)
                # print(counter, interval,)

            elif mark_dict[k] == 'False':
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

    def get_bonus_list_with_sum(self):
        self.bonus_list = self.count_a_bonus()
        max_bonus_list = self.count_a_bonus(self.max_bonus_ser)
        bonus_count = len([i for i in self.bonus_list if i])
        max_bonus_count = len([i for i in max_bonus_list if i])
        true_percent = bonus_count / max_bonus_count

        self.bonus_list.append(sum(self.bonus_list))
        self.bonus_list.insert(-1, int(true_percent * 100))
#        print('finish:', 'logic', self.bonus_logic, self.bonus_list)
        return self.bonus_list


