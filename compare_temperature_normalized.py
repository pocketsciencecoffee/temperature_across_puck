#!/usr/bin/python3

import seaborn as sb
import matplotlib.pyplot as plt
import pandas
import re
import argparse
import matplotlib as mpl
from cycler import cycler
#import numpy as np

dose = 18
lrr = 1.0
puck_slices = 4

# Rohan - Choose profile for which data was collected
#shot_category = "MP_extractamundo"
#shot_category = "MP_turbo_6bar_flat"
#shot_category = "Niche_boomer"
shot_category = "Niche_blooming"

shot_types = ['above_puck_screen', 'below_puck_screen', '75_above_bottom', '50_above_bottom', '25_above_bottom', 'bottom']

# Rohan - Look at raw plots to visullay determine normalization flow-rate reference and therefore basket temperature due to seemingly direct correlation
#normalize_reference = 'below_puck_screen'
#normalize_reference = 'bottom'
#normalize_reference = '75_above_bottom'
normalize_reference = '50_above_bottom'

# Rohan - Set lower bound in seconds for lowest probe for which to trace temperature (do it visually based on when output flow begins or bottom probe temperature starts rising)
bottom_probe_trace_cutoff = 10
num_traces = 20
zero_flow_proxy = 0.2

temperature_csv = "/home/bhatta/Desktop/DE1_shots/" + shot_category + "/probe_data.csv"
#shot_1_file = "/home/bhatta/Desktop/DE1_shots/MP_turbo_6bar_flat/20220525T185611.shot"

temp_data_df = pandas.read_csv(temperature_csv, delimiter=';')

# Rohan - Grab data from shot files
timestamps = {}
basket_temp = {}
mix_temp= {}
out_flow = {}
in_flow = {}
shot_start = {}
shot_stop = {}
probe_temp = {}
probe_time = {}
for type in shot_types:
    shot_file = "/home/bhatta/Desktop/DE1_shots/" + shot_category + "/" + type + ".shot"

    timestamps[type] = []
    shot_start[type] = []
    basket_temp[type] = []
    mix_temp[type] = []
    in_flow[type] = []
    out_flow[type] = []
    shot_stop[type] = []
    with open(shot_file, 'rt') as infile:
        for line in infile:
            #print line
            clock_match = re.search(r'^espresso_start\s+(\d+.*)', line)
            if clock_match:
                shot_start[type] = float(clock_match.group(1))

            time_match = re.search(r'^espresso_elapsed\s+{(.*)}', line)
            if time_match:
                for timestamp in time_match.group(1).split():
                    timestamps[type].append(float(timestamp))

            temp_match = re.search(r'^espresso_temperature_basket\s+{(.*)}', line)
            if temp_match:
                for temp in temp_match.group(1).split():
                    basket_temp[type].append(float(temp))
                basket_temp[type].pop(0)

            mix_match = re.search(r'^espresso_temperature_mix\s+{(.*)}', line)
            if mix_match:
                for temp in mix_match.group(1).split():
                    mix_temp[type].append(float(temp))
                mix_temp[type].pop(0)

            in_flow_match = re.search(r'^espresso_flow\s+{(.*)}', line)
            if in_flow_match:
                for flow in in_flow_match.group(1).split():
                    in_flow[type].append(float(flow))
                in_flow[type].pop(0)
            
            out_flow_match = re.search(r'^espresso_flow_weight\s+{(.*)}', line)
            if out_flow_match:
                for flow in out_flow_match.group(1).split():
                    out_flow[type].append(float(flow))
                out_flow[type].pop(0)

            stop_match = re.search(r'^timers\(espresso_stop\)\s+(\d+.*)', line)
            if stop_match:
                shot_stop[type] = float(stop_match.group(1))/1000.0
    #print(type + " shot start: " + str(shot_start[type]))
    #print(type + " shot stop: " + str(shot_stop[type]))

    index = 0
    readflag = False
    probe_time[type] = []
    probe_temp[type] = []
    for clk in temp_data_df['UNIX time']:
        if clk >= shot_start[type]:
            readflag = True
        if clk >= shot_stop[type]:
            readflag = False
        if readflag:
            #print("index: " + str(index))
            time_diff = clk - shot_start[type]
            #print("time diff: " + str(time_diff))
            probe_time[type].append(time_diff)
            temp = (temp_data_df['temperature1'][index] - 32)*5/9
            #print("temp: " + str(temp))
            probe_temp[type].append(temp)

        index += 1


# Rohan - Determine shorted shot and trim rest of the shots to that length for efficient normalization
min_len = 10000
for type in shot_types:
    if len(basket_temp[type]) < min_len:
        min_len = len(basket_temp[type])
for type in shot_types:
    del timestamps[type][min_len:]
    del basket_temp[type][min_len:]
    del mix_temp[type][min_len:]
    del in_flow[type][min_len:]
    del out_flow[type][min_len:]


# Rohan - Trim probe arrays to match time duration with shot arrays
for type in shot_types:
    probe_index = 0
    for p_time in probe_time[type]:
        if p_time >= timestamps[type][-1]:
            break
        probe_index += 1
    del probe_time[type][probe_index:]
    del probe_temp[type][probe_index:]

# Rohan - Find delta between probe temp and closest basket_temp
#delta_probe_basket = {}
normalized_probe_temp = {}
for type in shot_types:
    normalized_probe_temp[type] = []
    if type == normalize_reference:
        for p_temp in probe_temp[type]:
            normalized_probe_temp[type].append(p_temp)
        continue
    probe_index = 0
    for p_time in probe_time[type]:
        shot_index = 0
        for timestamp in timestamps[type]:
            if timestamp >= p_time:
                break
            shot_index+= 1
        temp_delta = basket_temp[type][shot_index] - probe_temp[type][probe_index]
        updated_probe_temp = basket_temp[normalize_reference][shot_index] - temp_delta
        normalized_probe_temp[type].append(updated_probe_temp)
        probe_index += 1

# Rohan - Trace "temperature journey" of unit volume of water
tracepoints = []
trace_count = 1
startpoint_trace = probe_time['bottom'][-1]
tracepoints.append(startpoint_trace)
trace_delta = (startpoint_trace - bottom_probe_trace_cutoff)/num_traces
tracepoint = startpoint_trace
while trace_count < num_traces:
    tracepoint -= trace_delta
    tracepoint = round(tracepoint, 1)
    tracepoints.append(tracepoint)
    trace_count += 1

shot_types.reverse()
temp_trace = {}
time_trace = {}
for tracepoint in tracepoints:
    #print(f'tracepoint keys {time_trace.keys()}')
    #print(f'tracepoint is {tracepoint}')
    slurry_volume = dose * lrr
    anchor_point = tracepoint
    if tracepoint not in time_trace.keys():
        tracepoint = round(tracepoint, 1)
        temp_trace[tracepoint] = []
        time_trace[tracepoint] = []
    for type in shot_types:
        #print(f'type is {type}')
        #print(f'anchor point is {anchor_point}')
        probe_index = 0
        for p_time in probe_time[type]:
            if p_time >= anchor_point:
                break
            probe_index += 1

        temp_trace[tracepoint].append(normalized_probe_temp[type][probe_index])
        time_trace[tracepoint].append(probe_time[type][probe_index])

        if type == 'below_puck_screen':
            break

        shot_index = 0
        for timestamp in timestamps[type]:
            if timestamp >= anchor_point:
                break
            shot_index += 1

        anchor_point_flow = in_flow[normalize_reference][shot_index]
        if anchor_point_flow < 0.2:
            # Rohan - Trace back along zero-flow line till a point back in time where flow was higher. Assumption is water isn't moving in that duration so tracing the probe temp for that type for that duration should be a fair assumption
            while anchor_point_flow < 0.2:
                #print('In while loop for zero-flow')
                shot_index -= 1
                anchor_point_flow = in_flow[normalize_reference][shot_index]
                probe_index = 0
                for p_time in probe_time[type]:
                    if p_time >= timestamps[normalize_reference][shot_index]:
                        break
                    probe_index += 1
                temp_trace[tracepoint].append(normalized_probe_temp[type][probe_index])
                time_trace[tracepoint].append(probe_time[type][probe_index])
            # Rohan - Reducing probe index by 1 on purpose to ensure it doesn't end up at a zero-flow point and get stuck in a loop
            anchor_point = probe_time[type][probe_index-1]
        else:
            new_anchor_point = anchor_point - (slurry_volume/puck_slices)/anchor_point_flow
            anchor_point = new_anchor_point
            #print(f'anchor point flow is {anchor_point_flow}')

# Rohan - Plot collected and normalized data

fig = plt.figure(figsize = (2,1))

ax1 = fig.add_subplot(2,1,1)
ax1.plot(probe_time['above_puck_screen'], normalized_probe_temp['above_puck_screen'], label='probe_above_puck_screen', color='C0')
ax1.plot(timestamps['above_puck_screen'], basket_temp['above_puck_screen'], label='basket_temp', color='C0', linestyle="--")
#ax1.plot(timestamps['above_puck_screen'], mix_temp['above_puck_screen'], label='mix_temp_machine', color='C0', linestyle="dotted")
ax1.plot(probe_time['below_puck_screen'], normalized_probe_temp['below_puck_screen'], label='probe_below_puck_screen', color='C1')
ax1.plot(timestamps['below_puck_screen'], basket_temp['below_puck_screen'], label='basket_temp', color='C1', linestyle="--")
#ax1.plot(timestamps['below_puck_screen'], mix_temp['below_puck_screen'], label='mix_temp_machine', color='C1', linestyle="dotted")
ax1.plot(probe_time['75_above_bottom'], normalized_probe_temp['75_above_bottom'], label='probe_75_above_bottom', color='C2')
ax1.plot(timestamps['75_above_bottom'], basket_temp['75_above_bottom'], label='basket_temp', color='C2', linestyle="--")
#ax1.plot(timestamps['75_above_bottom'], mix_temp['75_above_bottom'], label='mix_temp_machine', color='C2', linestyle="dotted")
ax1.plot(probe_time['50_above_bottom'], normalized_probe_temp['50_above_bottom'], label='probe_50_above_bottom', color='C3')
ax1.plot(timestamps['50_above_bottom'], basket_temp['50_above_bottom'], label='basket_temp', color='C3', linestyle="--")
#ax1.plot(timestamps['50_above_bottom'], mix_temp['50_above_bottom'], label='mix_temp_machine', color='C3', linestyle="dotted")
ax1.plot(probe_time['25_above_bottom'], normalized_probe_temp['25_above_bottom'], label='probe_25_above_bottom', color='C4')
ax1.plot(timestamps['25_above_bottom'], basket_temp['25_above_bottom'], label='basket_temp', color='C4', linestyle="--")
#ax1.plot(timestamps['25_above_bottom'], mix_temp['25_above_bottom'], label='mix_temp_machine', color='C4', linestyle="dotted")
ax1.plot(probe_time['bottom'], normalized_probe_temp['bottom'], label='probe_at_bottom', color='C5')
ax1.plot(timestamps['bottom'], basket_temp['bottom'], label='basket_temp', color='C5', linestyle="--")
#ax1.plot(timestamps['bottom'], mix_temp['bottom'], label='mix_temp_machine', color='C5', linestyle="dotted")
ax1.set_ylim(30,100)
#ax1.set_xlim(0,9)
ax1.set_xlabel("shot time (s)")
ax1.set_ylabel("temperature (C)")
ax1.legend(ncol=2, loc='lower right')
ax1.set_title("Blooming shot on Niche")

ax3 = fig.add_subplot(2,1,2)
#mpl.rcParams['axes.prop_cycle'] = cycler(color=mpl.colors.to_rgba_array(['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6']))
#ax3.plot(time_trace[list(temp_trace.keys())[0]], temp_trace[list(time_trace.keys())[0]], label = list(time_trace.keys())[0])
for tracepoint in temp_trace.keys():
    ax3.plot(time_trace[tracepoint], temp_trace[tracepoint], label = tracepoint)
ax3.legend(ncol=3, loc='lower right', title="unit volume exit time (s)")
ax3.set_xlabel('time (s)')
ax3.set_ylabel('temperature (C)')
ax3.set_title("Blooming shot on Niche")


plt.show()


