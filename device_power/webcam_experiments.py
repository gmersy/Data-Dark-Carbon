from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import time
import json
import os
plt.style.use('seaborn-v0_8-paper')
from webcam import VideoEmbodiedCarbon

class VideoExperiment(VideoEmbodiedCarbon):
    def __init__(self, video_file, num_frames):
        super().__init__(video_file, num_frames)
    
    def set_relevant_data(self, relevant_data):
        self._relevant_data = relevant_data
    
    def sense(self):
        self._start_capture = datetime.now()
        self.capture_webcam(self._video_file, self._num_frames)
        # wait for io to finish
        time.sleep(3)
        self._end_capture = datetime.now()
        # let the cpu rest
        time.sleep(2)


if __name__ == '__main__':
    power_sample_rate = int(input("What is the power sampling rate in milliseconds?\n"))

    dec1 = pd.read_csv("carbon_intensity_pricing/12_01_2022.csv", thousands=',')
    CARBON_INTENSITIES = json.load(open("MISO_carbon_intensity.json"))
    dfs = [dec1]
    for i in range(len(dfs)):
        dfs[i] = dfs[i].drop(axis=1, columns=['Other', 'Storage'])
        datetimes, grid_carbon_intensities = [], []
        for hour in dfs[i]['Hour']:
            datetimes.append(datetime(2022, 12, i+1, hour-1))
        
        dfs[i] = dfs[i].drop(axis=1, columns=['Hour'])

        dfs[i]['Time'] = datetimes


    full = pd.concat(dfs, axis=0)
    full = full.set_index('Time')

    full[full.columns] = full[full.columns].astype('float64')
    total = full['Coal'] + full['Gas'] + full['Wind'] + full['Nuclear'] + full['Solar'] + full['Hydro']

    full['g CO2 e/KWh'] = (1/total)*(CARBON_INTENSITIES['Coal']*full['Coal'] + \
        CARBON_INTENSITIES['Gas']*full['Gas'] + CARBON_INTENSITIES['Wind']*full['Wind'] + \
        CARBON_INTENSITIES['Nuclear']*full['Nuclear'] \
        + CARBON_INTENSITIES['Solar']*full['Solar'] + CARBON_INTENSITIES['Hydro']*full['Hydro'])    
    
    full = full[['g CO2 e/KWh']]
    video_file = 'device_power/experiments.mp4'

    trackers = []
    num_frames = 500

    for _ in range(24):
        tracker = VideoExperiment(video_file, num_frames)
        tracker.sense()
        trackers.append(tracker)
        os.remove(video_file)
        time.sleep(5)


    power_file = input("First terminate the power logging. Now, what is the path of the power file?\n")
    
    trackers[0].parse_power_data(power_file, power_sample_rate)

    for i in range(1, len(trackers)):
        trackers[i].set_relevant_data(trackers[0]._relevant_data)
    energy_values = []
    for tracker in trackers:
        sensing = tracker.query_power_data(tracker._start_capture, tracker._end_capture)
        sense_energy = tracker.energy(sensing, power_sample_rate, unit='J')
        energy_values.append(sense_energy)
    
    full['Energy (J)'] = energy_values
    full['Emissions (g CO2 e)'] = (full['Energy (J)']/3600000)*(full['g CO2 e/KWh'])

    full.plot.scatter(x='Energy (J)', y='Emissions (g CO2 e)')
    plt.savefig('figs/energy_carbon_scatter.png', dpi=600, bbox_inches="tight")
