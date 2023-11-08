import itertools
import json
import re


def check_on_demand(easy_db):
    processed_buses = []
    bus_ids = []
    wrong_stops = []
    transfer_stations = []
    for bus in easy_db:  # process_bus init
        if bus['bus_id'] not in bus_ids:
            bus_ids.append(bus['bus_id'])
            processed_buses.append(dict(bus_id=bus['bus_id'], stop_type=[], stops=[],
                                        s_stops=[], f_stops=[], t_stops=[], o_stops=[]))
    print('On demand stops test:')
    for process_bus, bus in itertools.product(processed_buses, easy_db):
        if bus['bus_id'] == process_bus['bus_id']:
            if bus['stop_name'] not in process_bus['stops']:
                process_bus['stops'].append(bus['stop_name'])
            if bus['stop_type'] not in process_bus['stop_type']:
                process_bus['stop_type'].append(bus['stop_type'])
            if bus['stop_type'] == 'S' and bus['stop_name'] not in process_bus['s_stops']:
                process_bus['s_stops'].append(bus['stop_name'])
            if bus['stop_type'] == 'F' and bus['stop_name'] not in process_bus['f_stops']:
                process_bus['f_stops'].append(bus['stop_name'])
            if bus['stop_type'] == 'O' and bus['stop_name'] not in process_bus['o_stops']:
                process_bus['o_stops'].append(bus['stop_name'])
        else:
            if bus['stop_name'] in process_bus['stops'] and bus['stop_name'] not in transfer_stations:
                transfer_stations.append(bus['stop_name'])
    print(processed_buses)
    print(transfer_stations)
    for bus in processed_buses:
        for bus_stop in bus['o_stops']:
            if bus_stop in bus['s_stops'] and bus_stop not in wrong_stops:
                wrong_stops.append(bus_stop)
            if bus_stop in bus['f_stops'] and bus_stop not in wrong_stops:
                wrong_stops.append(bus_stop)
            if bus_stop in transfer_stations and bus_stop not in wrong_stops:
                wrong_stops.append(bus_stop)
    if wrong_stops:
        print('Wrong stop type:', sorted(wrong_stops))
    else:
        print("OK")


def check_routes(easy_db):
    processed_buses = []
    bus_ids = []
    for bus in easy_db:
        if bus['bus_id'] not in bus_ids:
            bus_ids.append(bus['bus_id'])
            processed_buses.append(dict(bus_id=bus['bus_id'], stop_type=[], stops_num=0, stops=[]))
    bad_data_flag = 0
    start_stations = []
    finish_stations = []
    transfer_stations = []
    for process_bus, bus in itertools.product(processed_buses, easy_db):
        if bus['bus_id'] == process_bus['bus_id']:
            if bus['stop_type'] not in process_bus['stop_type']:
                process_bus['stop_type'].append(bus['stop_type'])
                process_bus['stops_num'] += 1
                if bus['stop_type'] == 'S' and bus['stop_name'] not in start_stations:
                    start_stations.append(bus['stop_name'])
                if bus['stop_type'] == 'F' and bus['stop_name'] not in finish_stations:
                    finish_stations.append(bus['stop_name'])
            elif bus['stop_type'] == 'S' and bus['stop_type'] in process_bus['stop_type']:
                print(f"There is incorrectly marked stop. Take a closer look at the line {bus['bus_id']}.")
                bad_data_flag = 1
                break
            elif bus['stop_type'] == 'F' and bus['stop_type'] in process_bus['stop_type']:
                print(f"There is incorrectly marked stop. Take a closer look at the line {bus['bus_id']}.")
                bad_data_flag = 1
                break
            if bus['stop_name'] not in process_bus['stops']:
                process_bus['stops'].append(bus['stop_name'])
        else:
            if bus['stop_name'] in process_bus['stops'] and bus['stop_name'] not in transfer_stations:
                transfer_stations.append(bus['stop_name'])
    for bus in processed_buses:
        if 'S' not in bus['stop_type']:
            print(f"There is incorrectly marked stop. Take a closer look at the line {bus['bus_id']}.")
            bad_data_flag = 1
            break
        if 'F' not in bus['stop_type']:
            print(f"There is incorrectly marked stop. Take a closer look at the line {bus['bus_id']}.")
            bad_data_flag = 1
            break
    if bad_data_flag == 0:
        print(f"Start stops: {len(start_stations)} {sorted(start_stations)}")
        print(f"Transfer stops: {len(transfer_stations)} {sorted(transfer_stations)}")
        print(f"Finish stops: {len(finish_stations)} {sorted(finish_stations)}")


def check_arrival_times(easy_db):
    processed_buses = []
    bus_ids = []
    bad_data_flag = 0
    for bus in easy_db:
        if bus['bus_id'] not in bus_ids:
            bus_ids.append(bus['bus_id'])
            processed_buses.append(dict(bus_id=bus['bus_id'], a_times=[bus['a_time']], bad_data=0))
    print('Arrival time test:')
    for process_bus, bus in itertools.product(processed_buses, easy_db):
        if bus['bus_id'] == process_bus['bus_id']:
            if bus['a_time'] > process_bus['a_times'][-1] or len(process_bus['a_times']) == 1:
                if process_bus['bad_data'] == 0:
                    process_bus['a_times'].append(bus['a_time'])
                else:
                    continue
            else:
                if process_bus['bad_data']:
                    continue
                else:
                    process_bus['bad_data'] = 1
                    print(f"bus_id line {bus['bus_id']}: wrong time on station {bus['stop_name']}")
                    bad_data_flag = 1
    if bad_data_flag == 0:
        print("OK")


def ids_and_stops(easy_db):
    buses = {}
    for bus in easy_db:
        key = str(bus['bus_id'])
        if key in buses.keys():
            buses[key] += 1
        else:
            buses[key] = 1
    print("Line names and number of stops:")
    for bus_id, stops in buses.items():
        print(f'bus_id: {bus_id}, stops: {stops}')


def format_issues(easy_db):
    stop_types = {'S', 'O', 'F'}  # stop types hard coded from format requirements
    f_issues = {'bus_id': 0, 'stop_id': 0, 'stop_name': 0, 'next_stop': 0, 'stop_type': 0, 'a_time': 0}
    for bus in easy_db:
        if isinstance(bus['stop_name'], str):
            stops_template = '(([A-Z]{1}[a-z]+ )+(Road|Avenue|Boulevard|Street))?$'
            if re.match(stops_template, bus['stop_name']) is None:
                f_issues['stop_name'] += 1
        if isinstance(bus['stop_type'], str) and bus['stop_type'] != '':
            if bus['stop_type'] not in stop_types or len(bus['stop_type']) > 1:
                f_issues['stop_type'] += 1
        if isinstance(bus['a_time'], str) and len(bus['a_time']) > 0:
            time_template = r'^(([0-1][0-9])|(2[0-3]))\:[0-5][0-9]$'
            if re.match(time_template, bus['a_time']) is None:
                f_issues['a_time'] += 1
    issue_num = sum(f_issues.values())
    print(f'Format validation: {issue_num} errors')
    print(f'stop_name: {f_issues["stop_name"]}')
    print(f'stop_type: {f_issues["stop_type"]}')
    print(f'a_time: {f_issues["a_time"]}')


def type_req_issues(easy_db):
    issue_counter = {'bus_id': 0, 'stop_id': 0, 'stop_name': 0, 'next_stop': 0, 'stop_type': 0, 'a_time': 0}
    for bus in easy_db:
        if not isinstance(bus['bus_id'], int):
            issue_counter['bus_id'] += 1
        if not isinstance(bus['stop_name'], str):
            issue_counter['stop_name'] += 1
        else:
            if bus['stop_name'] == '':
                issue_counter['stop_name'] += 1
        if not isinstance(bus['stop_id'], int):
            issue_counter['stop_id'] += 1
        if not isinstance(bus['next_stop'], int):
            issue_counter['next_stop'] += 1
        if not isinstance(bus['stop_type'], str) or len(bus['stop_type']) > 1:
            issue_counter['stop_type'] += 1
        if not isinstance(bus['a_time'], str) or len(bus['a_time']) < 5:
            issue_counter['a_time'] += 1
    issue_num = sum(issue_counter.values())
    print(f'Type and required field validation: {issue_num} errors')
    for issue in issue_counter:
        print(f'{issue}: {issue_counter[issue]}')


def main():
    easy_db = input()  # input from stdin for testing purposes, can be changed to file processing
    easy_db = json.loads(easy_db)
    # type_req_issues(easy_db)  # data validation script #1
    # format_issues(easy_db)  # data validation script #2
    # ids_and_stops(easy_db)  # data processing script #1
    # check_routes(easy_db) # data processing script #2
    # check_arrival_times(easy_db)  # data processing script #3
    check_on_demand(easy_db)  # data processing script #4


if __name__ == '__main__':
    main()
