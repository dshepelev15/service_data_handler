import os
import time

FOLDER_INPUT_NAME = 'csv_input'
FOLDER_OUTPUT_NAME = 'csv_output'

if not os.path.exists(FOLDER_OUTPUT_NAME):
    os.makedirs(FOLDER_OUTPUT_NAME)

runned_files = [
    file
    for file in os.listdir(FOLDER_OUTPUT_NAME)
        if os.path.isfile('{0}/{1}'.format(FOLDER_OUTPUT_NAME, file))
]

while True:
    files = os.listdir(FOLDER_INPUT_NAME)
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