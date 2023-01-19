import datetime

import cycler
from matplotlib import pyplot as plt


class GraphsDrawing:
    def __init__(self, start_date, end_date, path_to_pic):
        self.start_date = start_date
        self.end_date = end_date
        self.path_to_pic = path_to_pic
        self.box = {'facecolor': 'white',  # цвет области
                    'edgecolor': 'red',  # цвет крайней линии
                    'boxstyle': 'round'}
        if end_date - start_date > datetime.timedelta(weeks=25):
            self.figsize = (100, 20)
            self.label_fontsize = 100
            self.title_fontsize, self.tick_fontsize,self.legend_fontsize = 50, 50, 50
            self.leg_linewidth, self.linewidth = 8, 2
            self.marker_size, self.xticks_spaces = 5, 25
            self.major_tick_params = {'width': 6,
                                      'length': 40,
                                      'pad': 15}
        else:
            self.figsize = (18, 10)
            self.label_fontsize = 40
            self.title_fontsize, self.tick_fontsize, self.legend_fontsize = 18, 18, 18
            self.leg_linewidth, self.linewidth = 3, 6
            self.marker_size, self.xticks_spaces = 15, 4
            self.major_tick_params = {'width': 4,
                                      'length': 20,
                                      'pad': 10}

    def __del__(self):
        """Деструктор, закрывающий все объекты Figure, созданные в процессе работы класса."""
        plt.close('all')

    def change_design(self):
        """Метод, который должен применяться вначале, для изменения размера и веса шрифта. А также для изменения,
        цвета линий на графиках. Без него цвета, когда количество линий > 10 начнут повторяться"""
        font = {'weight': 'bold',
                'size': self.tick_fontsize}
        plt.rc('font', **font)
        plt.rc('axes',
               prop_cycle=(
                   cycler.cycler('color', ['r', 'g', 'b', 'darkblue', 'lawngreen', 'hotpink', 'c', 'y', 'm', 'orange',
                                           'burlywood', 'darkmagenta', 'grey', 'darkslategray', 'saddlebrown',
                                           'lightsalmon'])))
        return None

    def graph_format(self, y_lim, x_label, y_label):
        """Метод, прописывающий неизменный формат для графиков, желательно добавить смену figsize и fontsize"""
        plt.figure(figsize=self.figsize)
        plt.xlabel(x_label, fontsize=self.label_fontsize)
        plt.ylabel(y_label, fontsize=self.label_fontsize)
        plt.grid()
        plt.minorticks_on()
        plt.tick_params(axis='both', which='minor', direction='out', length=self.major_tick_params['length'] / 2,
                        width=self.major_tick_params['width'] / 2, pad=self.major_tick_params['pad'])
        plt.tick_params(axis='both', which='major', direction='out', length=self.major_tick_params['length'],
                        width=self.major_tick_params['width'], pad=self.major_tick_params['pad'])
        plt.grid(which='minor',
                 color='k',
                 linestyle=':')
        plt.ylim(y_lim)
        plt.xlim([self.start_date, self.end_date])

    def legend_design(self):
        leg = plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left", fontsize = self.legend_fontsize)
        for line in leg.get_lines():
            line.set_linewidth(self.leg_linewidth)

    def worktime_graph(self, worktime_frame, cluster):
        """Метод, рисующий график продолжительности работы установки ПРИЗМА-32 для заданного кластера, дает на выходе
        путь к месту, где в системе лежит график"""
        self.graph_format(y_lim=[0, 25], x_label='Дата', y_label='Время работы, ч')
        plt.xticks([i.date() for i in list(worktime_frame['Date'])[::self.xticks_spaces]],
                   [i.date() for i in list(worktime_frame['Date'])[::self.xticks_spaces]])
        plt.plot(worktime_frame['Date'], worktime_frame['Worktime'], marker='s', markersize=self.marker_size,
                 color='darkblue', linewidth=self.linewidth)
        plt.title(f"{cluster}-кластер", bbox=self.box, fontsize=self.title_fontsize, loc='center')
        path_pic = f'{self.path_to_pic}\\{cluster}worktime{self.start_date.day}-{self.start_date.month}-' \
                   f'{self.end_date.day}-{self.end_date.month}.png'
        plt.savefig(path_pic, bbox_inches='tight')
        return path_pic

    def amp_5_fr_4_graph(self, amp_5_fr_4_frame, amp_5_fr_4_frame_2, worktime_frame, worktime_frame_2):
        """Метод, рисующий график количества событий с A>5, Fr>=4 на 1-м и 2-м кластере, дает на выходе путь к месту,
        где в системе лежит график"""
        self.graph_format(y_lim=[0, 5], x_label='Дата', y_label='N, соб/час')
        plt.xticks([i.date() for i in list(amp_5_fr_4_frame['Date'])[::self.xticks_spaces]],
                   [i.date() for i in list(amp_5_fr_4_frame['Date'])[::self.xticks_spaces]])
        plt.plot(amp_5_fr_4_frame['Date'], amp_5_fr_4_frame['Events'] / worktime_frame['Worktime'], label='1 Кл.',
                 marker='s', markersize=self.marker_size, color='darkblue', linewidth=self.linewidth)
        plt.plot(amp_5_fr_4_frame_2['Date'], amp_5_fr_4_frame_2['Events'] / worktime_frame_2['Worktime'], label='2 Кл.',
                 marker='s', markersize=self.marker_size, color='crimson', linewidth=self.linewidth)
        self.legend_design()
        path_pic = f'{self.path_to_pic}\\amp_5_fr_4{self.start_date.day}-{self.start_date.month}-' \
                   f'{self.end_date.day}-{self.end_date.month}.png'
        plt.savefig(path_pic, bbox_inches='tight')
        return path_pic

    def neutron_to_0_tr_graph(self, neutron_num_0_tr_frame, cluster):
        """Метод, рисующий для заданного кластера график нормированного числа импульсов, отобранных установкой
        ПРИЗМА-32, как нейтрон при самозапуске, происходящем раз в 5 минут. Нормировка произведена на количество
        самозапусков. Метод дает на выходе путь к месту, где в системе лежит график"""
        self.graph_format(y_lim=[0, 0.5], x_label='Дата', y_label=r'$(coб)^{-1}$')
        plt.xticks([i.date() for i in list(neutron_num_0_tr_frame['Date'])[::self.xticks_spaces]],
                   [i.date() for i in list(neutron_num_0_tr_frame['Date'])[::self.xticks_spaces]])
        plt.title(f"{cluster}-кластер", bbox=self.box, fontsize=self.title_fontsize, loc='center')
        for i in range(1, 17):
            plt.plot(neutron_num_0_tr_frame['Date'], neutron_num_0_tr_frame[f'n{i}'], label=f'{i}',
                     linewidth=self.linewidth)
        self.legend_design()
        path_pic = f'{self.path_to_pic}\\{cluster}n_to_0_tr{self.start_date.day}-{self.start_date.month}-' \
                   f'{self.end_date.day}-{self.end_date.month}.png'
        plt.savefig(path_pic, bbox_inches='tight')
        return path_pic

    def amp_distribution_graph(self, amp_distribution_frame, cluster, a_crit, freq):
        """Метод, рисующий график амплитудного распределений событий с A>5, Fr>=2 для заданного кластера, дает на выходе
        путь к месту где в системе лежит график"""
        plt.figure(figsize=(18,10))
        plt.xlabel('Амплитуда, код АЦП', fontsize=40)
        plt.yscale('log')
        plt.xscale('log')
        plt.ylabel('N_соб(Fr≥2, A>5)', fontsize=40)
        plt.minorticks_on()
        plt.tick_params(axis='both', which='minor', direction='out', length=self.major_tick_params['length'] / 2,
                        width=self.major_tick_params['width'] / 2, pad=self.major_tick_params['pad'])
        plt.tick_params(axis='both', which='major', direction='out', length=self.major_tick_params['length'],
                        width=self.major_tick_params['width'], pad=self.major_tick_params['pad'])
        plt.xlim([a_crit - 1, 1000])
        plt.ylim([1, 1000])
        plt.text(500, 500, "1-кластер", bbox=self.box, fontsize=18)
        for i in range(1, 17):
            plt.plot(amp_distribution_frame[amp_distribution_frame[f'amp{i}'] >= a_crit][
                         f'amp{i}'].value_counts().sort_index().keys().tolist(),
                     amp_distribution_frame[amp_distribution_frame[f'amp{i}'] >= a_crit][
                         f'amp{i}'].value_counts().sort_index(), label=f'{i}', linewidth=6)

        path_pic = f'{self.path_to_pic}\\{cluster}amp_distr_{a_crit}_fr_{freq}{self.start_date.day}-' \
                   f'{self.start_date.month}-{self.end_date.day}-{self.end_date.month}.png'
        plt.savefig(path_pic, bbox_inches='tight')
        return path_pic

    def count_rate_graph(self, count_rate_frame, working_frame, cluster, a_crit, freq):
        """Метод, рисующий скорость счета детекторов для событий с A>5, Fr>=2 для заданного кластера, дает на выходе
        путь к месту где в системе лежит график"""
        self.graph_format(y_lim=[0, 8], x_label='Дата', y_label='N, соб/час')
        plt.title("1-кластер", bbox=self.box, fontsize=self.title_fontsize, loc='center')
        for i in range(1, 17):
            plt.xticks([i.date() for i in list(count_rate_frame['Date'])[::self.xticks_spaces]],
                       [i.date() for i in list(count_rate_frame['Date'])[::self.xticks_spaces]])
            plt.plot(count_rate_frame['Date'], count_rate_frame[f'amp{i}'], label=f'{i}',
                     linewidth=self.linewidth)
        self.legend_design()
        path_pic = f'{self.path_to_pic}\\{cluster}count_rate_{a_crit}_fr_{freq}{self.start_date.day}-' \
                   f'{self.start_date.month}-{self.end_date.day}-{self.end_date.month}.png'
        plt.savefig(path_pic, bbox_inches='tight')
        return path_pic
