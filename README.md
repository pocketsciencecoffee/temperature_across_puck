# temperature_across_puck
Code, shot files and temperature logs to plot temperature variance across an espresso puck that were published on this blog post:

https://pocketsciencecoffee.com/2022/09/13/temperature-gradient-across-an-espresso-puck/

There are two files (and their respective versions for viridis colors) for the following types of plots:
- Plots of probe temperature against basket_temp and machine_temp, along with plots of probe_temperature against input flow rates
- Plots of probe temperature against normalized flow rate

In both cases there are four categories of shot files. In case of each category the following may need to be adjusted appropriately based on shot type:
- ylim (y-axis limits) of temperature
- lowest cutoff time for bottom probe trace for temperature journey plots
- Label of subplots 
