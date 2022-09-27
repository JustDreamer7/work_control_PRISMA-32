# import datetime

from collections import defaultdict

import pandas as pd


class ProccessingPrismaCl:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def day_proccessing(self, n_file, p_file):
        """Функция, в которую помещается полная дневная обработка"""
        worktime_dict = defaultdict(list)
        n_vs_zero_tr_dict = defaultdict(list)
        event_counter_fr_4 = defaultdict(list)
        breaks_dict = defaultdict(list)
        count_rate_amp_5_fr_2 = defaultdict(list)
        count_rate_amp_10_fr_1 = defaultdict(list)
        amp_5_fr_2_frame = pd.DataFrame(columns=[f'amp{i}' for i in range(1, 17)])
        amp_10_fr_1_frame = pd.DataFrame(columns=[f'amp{i}' for i in range(1, 17)])
        for single_date in pd.date_range(self.start_date, self.end_date):
            worktime_dict['Date'].append(single_date)
            n_vs_zero_tr_dict['Date'].append(single_date)
            count_rate_amp_5_fr_2['Date'].append(single_date)
            count_rate_amp_10_fr_1['Date'].append(single_date)
            event_counter_fr_4['Date'].append(single_date)
            if type(p_file) != str:
                worktime_dict['Worktime'].append(round(len(p_file.index) * 5 / 60, 2))
                break_time_dict = self.counting_break_time(p_file)
                if break_time_dict:
                    breaks_dict['Date'].append(single_date)
                    breaks_dict['StartMinutes'].extend(break_time_dict['StartMinutes'])
                    breaks_dict['EndMinutes'].extend(break_time_dict['EndMinutes'])

            else:
                worktime_dict['Worktime'].append(0.00)
            if type(n_file) != str:
                neutron_to_zero_trigger = self.neutron_to_zero_trigger(n_file['Date'])
                for i in range(16):
                    n_vs_zero_tr_dict[f'n{i + 1}'].append(neutron_to_zero_trigger[i])
                    count_rate_amp_5_fr_2[f'amp{i + 1}'].append(
                        self.set_event_counter(n_file, a_crit=6, freq=2)['count_rate'][i + 1])
                    count_rate_amp_10_fr_1[f'amp{i + 1}'].append(
                        self.set_event_counter(n_file, a_crit=11, freq=1)['count_rate'][i + 1])

                event_counter_fr_4['Events'].append(self.set_event_counter(n_file, a_crit=6, freq=4)['sum_events'])

                set_event_counter_frame_1 = self.set_event_counter(n_file, a_crit=6, freq=2)['DataFrame']
                set_event_counter_frame_2 = self.set_event_counter(n_file, a_crit=11, freq=1)['DataFrame']

                amp_5_fr_2_frame = pd.concat(
                    [amp_5_fr_2_frame, set_event_counter_frame_1],
                    ignore_index=True)
                amp_10_fr_1_frame = pd.concat(
                    [amp_10_fr_1_frame, set_event_counter_frame_2],
                    ignore_index=True)
            else:
                for i in range(16):
                    n_vs_zero_tr_dict[f'n{i + 1}'].append(0.00)
                    count_rate_amp_5_fr_2[f'amp{i + 1}'].append(0.00)
                    count_rate_amp_10_fr_1[f'amp{i + 1}'].append(0.00)
                event_counter_fr_4['Events'].append(0.00)

        worktime_frame = pd.DataFrame(worktime_dict)
        n_vs_zero_tr_frame = pd.DataFrame(n_vs_zero_tr_dict)
        breaks_frame = pd.DataFrame(breaks_dict)
        event_counter_fr_4 = pd.DataFrame(event_counter_fr_4)
        count_rate_amp_5_fr_2 = pd.DataFrame(count_rate_amp_5_fr_2)
        count_rate_amp_10_fr_1 = pd.DataFrame(count_rate_amp_10_fr_1)

        for column in [f'amp{i}' for i in range(1,17)]:
            count_rate_amp_5_fr_2[column] = count_rate_amp_5_fr_2[column]/worktime_frame['Worktime']
            count_rate_amp_10_fr_1[column] = count_rate_amp_10_fr_1[column]/worktime_frame['Worktime']

        return worktime_frame, breaks_frame, n_vs_zero_tr_frame, event_counter_fr_4, amp_5_fr_2_frame, amp_10_fr_1_frame, count_rate_amp_5_fr_2, count_rate_amp_10_fr_1


    @staticmethod
    def counting_break_time(p_file):
        """Метод, выявляющий в p-file 5-минутки, когда кластер не работал, возвращает начальное время остановки и
        конечное время остановки"""
        index = p_file['time'].tolist()
        daily_breaks_dict = defaultdict(list)
        if max(index) < 287:
            start_minutes = max(index) * 5
            end_minutes = 1435
            daily_breaks_dict['StartMinutes'].append(start_minutes)
            daily_breaks_dict['EndMinutes'].append(end_minutes)
        if min(index) != 0:
            start_minutes = 0
            end_minutes = min(index) * 5
            daily_breaks_dict['StartMinutes'].append(start_minutes)
            daily_breaks_dict['EndMinutes'].append(end_minutes)
        for i in range(1, len(index)):
            if index[i] - index[i - 1] > 1:
                start_minutes = index[i - 1] * 5
                end_minutes = index[i] * 5
                daily_breaks_dict['StartMinutes'].append(start_minutes)
                daily_breaks_dict['EndMinutes'].append(end_minutes)
        if daily_breaks_dict:
            return daily_breaks_dict
        else:
            return None

    @staticmethod
    def neutron_to_zero_trigger(n_file):
        """Метод, обрабатывающий данные n-файлов ПРИЗМА-32, дающий на выходе нормированное число в событии,
        отобранных как нейтрон, при самозапуске"""
        counter_zero_tr = len(n_file[n_file['tr'] == 0].index)
        zero_tr_frame = n_file[n_file['tr'] == 0]
        return [round(zero_tr_frame[f'n{i}'].sum() / counter_zero_tr, 3) for i in range(1, 17)]

    # except ZeroDivisionError: Нужно дописать, если допустим нет нулевых триггеров

    @staticmethod
    def set_event_counter(n_file, a_crit, freq):
        """Метод, обрабатывающий данные n-файлов ПРИЗМА-32, на вход подаются определенная амплитуда и количество
        детекторов, на которых амплитуда превышает заданную, на выходе метод возвращает словарь с параметрами:
        1) суммарное число событий на кластере, подходящих под заданные условия;
        2) датафрейм с амплитудами детекторов для каждого события, подходящего под заданные условия;
        3) количество превышений заданной амплитуды у детектора в событиях, подходящих под заданные условия; """
        cluster_count_rate = {}
        amp_frame = n_file[[f'amp{i}' for i in range(1, 17)]]
        amp_frame['fr_sum'] = amp_frame.isin(range(a_crit, 520)).sum(axis=1, skipna=True)  # noqa
        amp_frame = amp_frame[amp_frame['fr_sum'] >= freq].reset_index(drop=True)
        for i in range(1, 17):
            cluster_count_rate[i] = len(amp_frame[amp_frame[f'amp{i}'] >= a_crit])
        return {'sum_events': len(amp_frame.index),
                'DataFrame': amp_frame[[f'amp{i}' for i in range(1, 17)]],
                'count_rate': cluster_count_rate}







