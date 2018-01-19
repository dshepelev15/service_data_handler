import numpy as np
import sys


FOLDER_INPUT_NAME = 'csv_input'
FOLDER_OUTPUT_NAME = 'csv_output'

# column number
START_LON = 2
START_LAT = 3
END_LON = 5
END_LAT = 6


def main():
    if len(sys.argv) == 1:
        return

    filename = sys.argv[1]
    input_path = '{0}/{1}'.format(FOLDER_INPUT_NAME, filename)
    data = np.genfromtxt(input_path, skip_header=1, delimiter=',')

    coordinates = []
    for row in data:
        x1 = row[START_LAT]
        y1 = row[START_LON]
        x2 = row[END_LAT]
        y2 = row[END_LON]

        if x1 > x2:
            x1, y1, x2, y2 = x2, y2, x1, y1

        # уравнение Ax + By + C = 0, a = 1
        b = 0
        if y1 != y2:
            b = (x2 - x1) / (y1 - y2)
        c = -x1 - b * y1

        coordinates.append([x1, y1, x2, y2, b, c])

    np_coordinates = np.array(coordinates, dtype=np.float_)

    results = []
    for i, parent_row in enumerate(np_coordinates):
        for j, child_row in enumerate(np_coordinates):
            if i == j:
                continue
            if parent_row[-2] != child_row[-2] or \
                parent_row[-1] != child_row[-1]:
                continue
            if parent_row[0] <= child_row[0] and \
                parent_row[2] >= child_row[2]:
                row_result = list(data[i]) + list(data[j])
                results.append(row_result)

    fields = 'route_id,step_id,start_lon,start_lat,start_time,end_lon,end_lat,end_time,travel_mode,age_group,foreign'.split(',')
    prefixes = ('parent_','child_')
    header_fields = [prefix + field
                     for prefix in prefixes
                     for field in fields]
    header = ','.join(header_fields)

    output_path = '{0}/{1}'.format(FOLDER_OUTPUT_NAME, filename)
    with open(output_path, 'wb') as fp:
        fp.write((header + '\n').encode())
        np.savetxt(fp, np.array(results), fmt='%.4f')

if __name__ == '__main__':
    main()