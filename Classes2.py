import pandas as pd
from random import choice, randint
import datetime
import numpy as np


class MonthData:
    def __init__(self, path):
        vedomost = pd.read_excel(path, sheet_name='vedomost').fillna(False)
        self.days = len([i for i in vedomost['DATE'].to_list() if i])
        self.vedomost = vedomost[0:self.days].fillna(0)
        self.prices = pd.read_excel(path, sheet_name='price', index_col=0).fillna(0)
        accessory_keys = ['MOD', 'WEAK', 'DUTY']
        category_keys = [i for i in self.vedomost if i not in accessory_keys]
        self.accessory = self.vedomost[accessory_keys]
        self.categories = self.vedomost[category_keys]


class AccessoryData:
    def __init__(self, af):
        self.af = af
        self.mods_frame = {}
        self.recipients = ['Egr', 'Lera']
        self.recipients_keys = ['coef_flag', 'positions']

    def get_mods_frame(self):
        self.mods_frame = pd.DataFrame(index=self.af.index)
        self.mods_frame['zlata'] = self.af['MOD']
        self.mods_frame['weak'] = ['WEAK' + str(int(i)) if i else i for i in self.af['WEAK'].to_list()]
        self.mods_frame['duty'] = ['duty' + str(int(i)) if i else i for i in self.af['DUTY'].to_list()]
        only_lera_mod_f = lambda i, e: i == 'duty24' or e == 'M'
        only_lera_mod = list(map(only_lera_mod_f, self.mods_frame['duty'], self.mods_frame['zlata']))
        self.mods_frame['only lera mod'] = only_lera_mod
        self.mods_frame['Egr_positions'] = #stopped
        # self.mods_frame['only lera mod'] = self.mods_frame['duty'] != False or self.mods_frame['zlata'] == 'M'
        print(self.mods_frame)
        for i in self.recipients:
            for e in self.recipients_keys:
                pass

        # if self.duty24: self.af['MOD'] == 'M' or
        #     self.positions = {'Lera': ['A', 'L', 'Z', 'F'], 'Egr': ['E']}
        #     self.only_lera_mod = True
        # else:
        #     self.positions = {'Lera': ['L'], 'Egr': ['E'], 'All': ['A', 'Z', 'F']}
        #     self.only_lera_mod = False
        # for k in self.positions:
        #     if self.first_char in self.positions[k]:
        #         self.recipient = k
        #
        # return self.mods_frame





        # for i in self.af:
        #     mods_dict[i] = self.accessory[i].to_dict()[result_key]
        #
        # self.zlata_mod = mods_dict['MOD']
        # self.weak_child_mod = mods_dict['WEAK']
        # self.volkhov_alone_mod = True if mods_dict['MOD'] == 'M' else False
        # self.on_duty = True if mods_dict['DUTY'] or self.volkhov_alone_mod else False
        # self.duty24 = True if mods_dict['DUTY'] == 24 or self.volkhov_alone_mod else False
        # self.duty_day = True if mods_dict['DUTY'] == 8 else False
        # collections
dec22 = MonthData('months/dec22test/dec22.xlsx')
ad = AccessoryData(dec22.accessory)
# print(dec22.accessory)
ad.get_mods_frame()
