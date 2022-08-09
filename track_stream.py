import tobii_research as tr
import socket
import time
import os
from copy import deepcopy
global data, file_path, count, prev_gaze_data, tcp_socket


def connect_tcp(TCP_IP, TCP_PORT, BUFFER_SIZE):
    global tcp_socket
    ready = False
    while not ready:
        try:
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.connect((TCP_IP, TCP_PORT))
            ready = True
        except Exception as e:
            print(e)
            time.sleep(0.5)


def gaze_data_callback(gaze_data):
    global data, file_path, count, prev_gaze_data, tcp_socket
    if prev_gaze_data is None:
        prev_gaze_data = deepcopy(gaze_data)
    if gaze_data['device_time_stamp'] != prev_gaze_data['device_time_stamp']:
        prev_gaze_data = deepcopy(gaze_data)
        data = deepcopy(gaze_data)
    try:
        data_msg = str(gaze_data['device_time_stamp']) + ',' + \
            str(gaze_data['left_gaze_point_on_display_area'][0]) + ',' + \
            str(gaze_data['left_gaze_point_on_display_area'][1]) + ',' + \
            str(gaze_data['left_gaze_point_validity']) + ',' + \
            str(gaze_data['left_pupil_diameter']) + ',' + \
            str(gaze_data['right_gaze_point_on_display_area'][0]) + ',' + \
            str(gaze_data['right_gaze_point_on_display_area'][1]) + ',' + \
            str(gaze_data['right_gaze_point_validity']) + ',' + \
            str(gaze_data['right_pupil_diameter'])
        print(data_msg)
        tcp_socket.send(data_msg.encode('utf-8'))

    except Exception as e:
        print(e)

        TCP_IP = '146.169.220.70'
        TCP_PORT = 8000
        BUFFER_SIZE = 1024
        connect_tcp(TCP_IP, TCP_PORT, BUFFER_SIZE)


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
    global data, file_path, count, prev_gaze_data, tcp_socket
    prev_gaze_data = None
    count = 0
    data = None

    my_eyetracker = connect()

    TCP_IP = '146.169.220.70'
    TCP_PORT = 8000
    BUFFER_SIZE = 1024

    connect_tcp(TCP_IP, TCP_PORT, BUFFER_SIZE)

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

