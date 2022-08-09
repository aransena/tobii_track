# Adapted from https://stackoverflow.com/questions/40126176/fast-live-plotting-in-matplotlib-pyplot
# ImportanceOfBeingErnest, Oct 19, 2016 at 18:54

import sys
import os
import time
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import tobii_research as tr
from copy import deepcopy
global data
from csv import DictWriter

def connect():
    found_eyetrackers = tr.find_all_eyetrackers()
    print(found_eyetrackers)
    if len(found_eyetrackers) > 0:
        eyetracker = found_eyetrackers[0]
        print("Address: " + eyetracker.address)
        print("Model: " + eyetracker.model)
        print("Name (It's OK if this is empty): " + eyetracker.device_name)
        print("Serial number: " + eyetracker.serial_number)
        print("Output frequency: " + str(eyetracker.get_gaze_output_frequency()))
        return eyetracker
    else:
        return None


class App(QtGui.QMainWindow):

    def gaze_data_callback(self, gaze_data):
        if self.gaze_data is None:
            self.gaze_data = deepcopy(gaze_data)
            self.gaze_cache.append(self.gaze_data)
        if (gaze_data['device_time_stamp'] != self.gaze_data['device_time_stamp']):
            self.gaze_data = deepcopy(gaze_data)
            self.gaze_cache.append(self.gaze_data)

            if len(self.gaze_cache) > self.N:
                self.gaze_cache.pop(0)
            try:
                with open(self.file_path, 'a+', newline='') as write_obj:
                    csv_writer = DictWriter(write_obj, fieldnames=list(gaze_data.keys()))
                    csv_writer.writerow(gaze_data)
            except Exception as e:
                print(e)


            # ['device_time_stamp', 'system_time_stamp', 'left_gaze_point_on_display_area', 'left_gaze_point_in_user_coordinate_system', 'left_gaze_point_validity', 'left_pupil_diameter', 'left_pupil_validity', 'left_gaze_origin_in_user_coordinate_system', 'left_gaze_origin_in_trackbox_coordinate_system', 'left_gaze_origin_validity', 'right_gaze_point_on_display_area', 'right_gaze_point_in_user_coordinate_system', 'right_gaze_point_validity', 'right_pupil_diameter', 'right_pupil_validity', 'right_gaze_origin_in_user_coordinate_system', 'right_gaze_origin_in_trackbox_coordinate_system', 'right_gaze_origin_validity']

    def __init__(self, my_eyetracker, parent=None):
        super(App, self).__init__(parent)

        #### Create Gui Elements ###########
        self.start_stamp = time.strftime("%y-%m-%d-%H-%M-%S")
        self.file_name = self.start_stamp + '.csv'
        os.makedirs('data', exist_ok=True)
        self.file_path = "data/" + self.file_name
        self.eyetracker = my_eyetracker
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        self.mainbox.layout().addWidget(self.canvas)

        self.label = QtGui.QLabel()
        self.mainbox.layout().addWidget(self.label)

        self.plots = []
        self.plots_data = []
        # [2, 'left_gaze_point_on_display_area', 4, 'left_gaze_point_validity', 5, 'left_pupil_diameter', 10, 'right_gaze_point_on_display_area', 12, 'right_gaze_point_validity', 13, 'right_pupil_diameter'])
        self.plot_keys = [2, 2, 4, 5, 10, 10, 12, 13]
        self.field_names = None

        self.gaze_data = None
        self.gaze_cache = []

        self.eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback, as_dictionary=True)
        titles = ['Eye X', 'Eye Y', 'Blink', 'Pupil Diameter']
        prev_timestamp = 0
        for i in range(8):
            if i < 4:
                col = 'r'
            else:
                col = 'b'
            if i < 4:
                self.plots.append(self.canvas.addPlot(row=i, col=0, title=titles[i]))
            self.plots_data.append(self.plots[i % 4].plot(row=i % 4, col=0, pen=col))
            if i%4 != 3:
                self.plots[-1].setYRange(0, 1.1)
            else:
                self.plots[-1].setYRange(0, 10)

            # self.canvas.nextRow()
            # self.canvas.nextColumn()

        #### Set Data  #####################
        self.N = 200
        # self.x = np.linspace(0, 1500., num=1000)

        self.counter = 0
        self.fps = 0.
        self.lastupdate = time.time()

        #### Start  #####################
        self._update()

    def _update(self):
        k = 0
        for i, p in enumerate(self.plots_data):
            x = []
            y = []


            for j, g in enumerate(self.gaze_cache):
                # [0, 'device_time_stamp',
                # 1, 'system_time_stamp',
                # 2, 'left_gaze_point_on_display_area',
                # 3, 'left_gaze_point_in_user_coordinate_system',
                # 4, 'left_gaze_point_validity',
                # 5, 'left_pupil_diameter',
                # 6, 'left_pupil_validity',
                # 7, 'left_gaze_origin_in_user_coordinate_system',
                # 8, 'left_gaze_origin_in_trackbox_coordinate_system',
                # 9, 'left_gaze_origin_validity',
                # 10, 'right_gaze_point_on_display_area',
                # 11, 'right_gaze_point_in_user_coordinate_system',
                # 12, 'right_gaze_point_validity',
                # 13, 'right_pupil_diameter',
                # 14, 'right_pupil_validity',
                # 15, 'right_gaze_origin_in_user_coordinate_system',
                # 16, 'right_gaze_origin_in_trackbox_coordinate_system',
                # 17, 'right_gaze_origin_validity'])
                x.append(j)
                try:
                    y.append(g[list(g.keys())[self.plot_keys[i]]][int(k)])
                except:
                    y.append(g[list(g.keys())[self.plot_keys[i]]])
            k = not k
            p.setData(y)

        now = time.time()
        dt = (now-self.lastupdate)
        if dt <= 0:
            dt = 0.000000000001
        fps2 = 1.0 / dt
        self.lastupdate = now
        self.fps = self.fps * 0.9 + fps2 * 0.1
        tx = 'Mean Frame Rate:  {fps:.3f} FPS'.format(fps=self.fps )
        self.label.setText(tx)
        QtCore.QTimer.singleShot(1, self._update)
        self.counter += 1


if __name__ == '__main__':
    global data
    data = None

    my_eyetracker = connect()
    if my_eyetracker is not None:

        app = QtGui.QApplication(sys.argv)
        thisapp = App(my_eyetracker)
        thisapp.show()
        sys.exit(app.exec_())