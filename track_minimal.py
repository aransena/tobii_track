import tobii_research as tr
from csv import DictWriter
import time
import os
from copy import deepcopy
global data, file_path, count, prev_gaze_data

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

def gaze_data_callback(gaze_data):
    global data, file_path, count, prev_gaze_data
    if prev_gaze_data is None:
        prev_gaze_data = deepcopy(gaze_data)
    if gaze_data['device_time_stamp'] != prev_gaze_data['device_time_stamp']:
        prev_gaze_data = deepcopy(gaze_data)
        data = deepcopy(gaze_data)
    try:
        with open(file_path, 'a+', newline='') as write_obj:
            csv_writer = DictWriter(write_obj, fieldnames=list(gaze_data.keys()))
            csv_writer.writerow(gaze_data)
        count += 1
        if count % 100 == 0:
            print(f"{count} lines written.")

    except Exception as e:
        print(e)


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


if __name__ == '__main__':
    global data, file_path, count, prev_gaze_data
    prev_gaze_data = None
    count = 0
    data = None
    start_stamp = time.strftime("%y-%m-%d-%H-%M-%S")
    os.makedirs('data', exist_ok=True)
    file_path = "data/"+start_stamp+".csv"
    my_eyetracker = connect()
    if my_eyetracker is not None:
        my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
        prev_timestamp = 0
        try:
            while True:
                if data is not None:
                    if data['device_time_stamp'] != prev_timestamp:
                        prev_timestamp = data['device_time_stamp']

        except KeyboardInterrupt:  # ctrl+c to exit
            my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

