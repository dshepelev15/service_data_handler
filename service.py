import os
import time

FOLDER_INPUT_NAME = 'csv_input'

runned_files = []

while True:
    files = os.listdir('csv_input')
    for file in files:
        file_path = '{0}/{1}'.format(FOLDER_INPUT_NAME, file)
        if os.path.isfile(file_path) and \
            not file.startswith('.') and \
            file not in runned_files:
            print('New file', file)
            runned_files.append(file)
            cmd = 'python3 data_handler.py %s' % file
            os.system(cmd)
    time.sleep(5)