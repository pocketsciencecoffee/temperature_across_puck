#!/usr/bin/python3

import seaborn as sb
import matplotlib.pyplot as plt
import pandas
import re
import argparse

shot_category = "MP_turbo_6bar_flat"
#shot_category = "MP_extractamundo"
#shot_category = "Niche_boomer"
shot_category = "Niche_blooming"

shot_types = ['above_puck_screen', 'below_puck_screen', '75_above_bottom', '50_above_bottom', '25_above_bottom', 'bottom']

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

# Rohan - Plot collected data

fig = plt.figure(figsize = (2,1))

ax1 = fig.add_subplot(2,1,1)
ax1.plot(probe_time['above_puck_screen'], probe_temp['above_puck_screen'], label='probe_above_puck_screen', color='#fde725')
ax1.plot(timestamps['above_puck_screen'], basket_temp['above_puck_screen'], label='basket_temp', color='#fde725', linestyle="--")
ax1.plot(timestamps['above_puck_screen'], mix_temp['above_puck_screen'], label='mix_temp_machine', color='#fde725', linestyle="dotted")
ax1.plot(probe_time['below_puck_screen'], probe_temp['below_puck_screen'], label='probe_below_puck_screen', color='#7ad151')
ax1.plot(timestamps['below_puck_screen'], basket_temp['below_puck_screen'], label='basket_temp', color='#7ad151', linestyle="--")
ax1.plot(timestamps['below_puck_screen'], mix_temp['below_puck_screen'], label='mix_temp_machine', color='#7ad151', linestyle="dotted")
ax1.plot(probe_time['75_above_bottom'], probe_temp['75_above_bottom'], label='probe_75_above_bottom', color='#22a884')
ax1.plot(timestamps['75_above_bottom'], basket_temp['75_above_bottom'], label='basket_temp', color='#22a884', linestyle="--")
ax1.plot(timestamps['75_above_bottom'], mix_temp['75_above_bottom'], label='mix_temp_machine', color='#22a884', linestyle="dotted")
ax1.plot(probe_time['50_above_bottom'], probe_temp['50_above_bottom'], label='probe_50_above_bottom', color='#2a788e')
ax1.plot(timestamps['50_above_bottom'], basket_temp['50_above_bottom'], label='basket_temp', color='#2a788e', linestyle="--")
ax1.plot(timestamps['50_above_bottom'], mix_temp['50_above_bottom'], label='mix_temp_machine', color='#2a788e', linestyle="dotted")
ax1.plot(probe_time['25_above_bottom'], probe_temp['25_above_bottom'], label='probe_25_above_bottom', color='#414487')
ax1.plot(timestamps['25_above_bottom'], basket_temp['25_above_bottom'], label='basket_temp', color='#414487', linestyle="--")
ax1.plot(timestamps['25_above_bottom'], mix_temp['25_above_bottom'], label='mix_temp_machine', color='#414487', linestyle="dotted")
ax1.plot(probe_time['bottom'], probe_temp['bottom'], label='probe_at_bottom', color='#440154')
ax1.plot(timestamps['bottom'], basket_temp['bottom'], label='basket_temp', color='#440154', linestyle="--")
ax1.plot(timestamps['bottom'], mix_temp['bottom'], label='mix_temp_machine', color='#440154', linestyle="dotted")
#ax1.set_ylim(20,110)
#ax1.set_xlim(0,14)
ax1.set_xlabel("shot time (s)")
ax1.set_ylabel("temperature (C)")
ax1.set_title("Blooming shot on Niche")
ax1.legend(ncol=2, loc='lower right')
#
#ax2 = ax1.twinx()
#ax2.plot(timestamps, out_flow, label='output_flow', color='brown', linestyle="--")
#ax3.plot(timestamps, in_flow, label='input_flow', color='blue', linestyle="--")
#ax2.set_ylim(0,8.5)
#ax2.set_ylabel("flow (g/s)")
#ax2.legend(loc='upper right')
#ax1.set_xlim(0,14)
#

ax2 = fig.add_subplot(2,1,2)
ax3 = ax2.twinx()
ax2.plot(probe_time['above_puck_screen'], probe_temp['above_puck_screen'], label='probe_above_puck_screen', color='#fde725')
ax3.plot(timestamps['above_puck_screen'], in_flow['above_puck_screen'], label='in_flow', color='#fde725', linestyle="--")
ax2.plot(probe_time['below_puck_screen'], probe_temp['below_puck_screen'], label='probe_below_puck_screen', color='#7ad151')
ax3.plot(timestamps['below_puck_screen'], in_flow['below_puck_screen'], label='in_flow', color='#7ad151', linestyle="--")
ax2.plot(probe_time['75_above_bottom'], probe_temp['75_above_bottom'], label='probe_75_above_bottom', color='#22a884')
ax3.plot(timestamps['75_above_bottom'], in_flow['75_above_bottom'], label='in_flow', color='#22a884', linestyle="--")
ax2.plot(probe_time['50_above_bottom'], probe_temp['50_above_bottom'], label='probe_50_above_bottom', color='#2a788e')
ax3.plot(timestamps['50_above_bottom'], in_flow['50_above_bottom'], label='in_flow_50_above_bottom', color='#2a788e', linestyle="--")
ax2.plot(probe_time['25_above_bottom'], probe_temp['25_above_bottom'], label='probe_25_above_bottom', color='#414487')
ax3.plot(timestamps['25_above_bottom'], in_flow['25_above_bottom'], label='in_flow_25_above_bottom', color='#414487', linestyle="--")
ax2.plot(probe_time['bottom'], probe_temp['bottom'], label='probe_at_bottom', color='#440154')
ax3.plot(timestamps['bottom'], in_flow['bottom'], label='in_flow_bottom', color='#440154', linestyle="--")
ax2.set_ylim(30,100)
ax3.set_ylim(-0.5,7)
ax2.set_xlabel("shot time (s)")
ax2.set_ylabel("temperature (C)")
ax3.set_ylabel("flow (g/s)")
ax2.set_title("Blooming shot on Niche")
ax2.legend(ncol=2, loc='upper left')
ax3.legend(ncol=2, loc='upper right')

plt.show()


