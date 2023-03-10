# Dark Carbon: Assessing the Hidden Sustainability Costs of Data Management
Hello! Welcome to the repository accompanying the submission Dark Carbon: Assessing the Hidden Sustainability Costs of Data Management. We will explain the steps to reproduce the results and explore how carbon provenance works. 

# Installation
## Prerequisites
1. Python 3
2. We use the Intel Power Gadget to obtain the power draw of hardware components. The Intel Power Gadget is compatible with 2nd Generation up to 10th Generation Intel Core processors and has native support for Mac and Windows. There are existing ports for [Linux](https://github.com/vitillo/power_gadget), but we cannot verify their accuracy. 

## Steps
1. Clone, fork, or download the repo
2. Install Python requirements via `pip install -r requirements.txt`
3. Install the [Intel Power Gadget](https://www.intel.com/content/www/us/en/developer/articles/tool/power-gadget.html)
# Raw Generation Sources
We collected publicly-available generation source data from both the [Midwest Independent System Operator](https://www.misoenergy.org/) (MISO) and [California Independent System Operator](https://www.caiso.com/Pages/default.aspx)
(CAISO). These raw data can be found in `carbon_intensity_pricing/`. We display the data sources in the below table for each applicable figure:

Figure        | Data Source(s)
------------- | -------------
1             | https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/ https://www.caiso.com/TodaysOutlook/Pages/supply.aspx#section-supply-trend
2             | https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/ https://www.caiso.com/TodaysOutlook/Pages/supply.aspx#section-supply-trend
3             | N/A, system diagram
4             | N/A, on-device power 
5             | https://www.misoenergy.org/markets-and-operations/RTDataAPIs/


# Carbon Intensity Methodology
The carbon intensity of each generation source in kg CO2e/MWh = g CO2e/kWh for the Midwest Independent System Operator and the California Independent System Operator are in `MISO_carbon_intensity.json` and `CAISO_carbon_intensity.json` respectively. Each JSON object contains the links to the references.

## CI for Low-Carbon Sources
Low-carbon sources are given life cycle carbon intensities. This metric includes emissions from manufacturing renewable components, ongoing operations, and disposing of the materials at the end of the component lifetime. We rely on metrics from the [National Renewable Energy Lab](https://www.nrel.gov/docs/fy21osti/80580.pdf) that calibrate a median life cycle value across multiple published life cycle asessments. For CAISO, the biogas CI is derived from a [study](https://onlinelibrary.wiley.com/doi/full/10.1002/elsc.201000073?casa_token=XonEKx8AkwgAAAAA%3APwu3O6k_tPFVCgStvsOudMk-JuxklWwq4WewR1xNd5KG2bQb2M6jldvV6NSDsf6saQm_DsINDgXXeuU) where the CI is the average of the 10 plant CIs given in Figure 3 of their paper. 

## CI for Fossil Fuels
The fossil fuels are given a grid-specific *combustion CI* derived from historical 2020 data to improve the geographical accuracy of the grid carbon intensities. Combustion CI does not include the rest of the power plant life cycle. You can visualize the data [here](https://www.epa.gov/egrid/data-explorer) by selecting **output emission rates (lb/MWh)** for **CO2 equivalent** for **all fuels** at the **balancing authority level** for **2020**. From there, you can click on the MISO and CAISO grids by navigating to the Midwest or California on the map. 

## Average CI for the Grid
Let $G_t$ denote the total power generation in MW at time $t$, $G_{ts}$ denote the generation in MW at time $t$ by generation source $s \in S$, and $CI_s$ denote the carbon intensity in kg CO2 e/MWh of generation source $s \in S$. Then, we define the average carbon intensity $C_t$ at time $t$ as: 
$$C_t = \sum_{s \in S} (G_{ts} / {G_t}) \times CI_s$$
where the total generation is
$$G_{t} = \sum_{s \in S} G_{ts}$$

# Power Methodology
There are two plausible ways to compute the energy in the context of the Intel Power Gadget. The first is using the "empirical" log data, which may contain a small I/O delay. To avoid this delay, we chose the "theoretical" energy, assuming that the power was logged at each discrete sampling time defined by the first log time and multiples of the sampling rate. Specifically, let $\mathbf{p} = [p_1, p_2, \ldots, p_r]$ be the power readings in Watts during the collection of a webcam video and $\Delta$ be the sensor sampling rate in seconds. The total energy in Joules is given by:
$$E = \sum_{t = 1}^{r} p_t \times \Delta$$

We can then convert the value to kWh by taking $E = E / 3.6 \times 10^6$ to match the grid average carbon intensity.  

# Carbon emissions
We compute the carbon emissions via:

$$\mathrm{emissions} = C_t \times E$$

where $C_t$ is the average carbon intensity at time $t$ and $E$ is the energy consumed during the collection of the webcam video.


# Reproducing Plots
The below table gives the correspondence between Figure x in the paper and the code file that reproduces that plot. 

Figure        | Code File
------------- | -------------
1             | `device_power/CAISO_MISO_webcam_experiments.py`
2             | `renewables_price_plots.ipynb`
3             | N/A, system diagram
4             | `device_power/webcam.py`
5             | `renewables_price_plots.ipynb`

Before running `device_power/webcam.py` or `device_power/CAISO_MISO_webcam_experiments.py` you must first start the power logging that saves the power for your hardware to a file at a given sampling rate. You will need to configure the sampling rate in milliseconds and the path that your logger will use like in the below image. Note that the GUI sampling rate is distinct from the *logging sampling rate*, which is the quantity that needs to be configured.

![Configure logging](https://www.intel.com/content/dam/develop/external/us/en/images/options-184535.png)

These values will be prompted by `device_power/webcam.py` and `device_power/CAISO_MISO_webcam_experiments.py` so please make note of them.

# Results
The stored results from the 24 short video experiment run on the 2019 Macbook Pro is in `experiment_results/results.csv`. The power logging for both the 2 minute video power plot and the 24 short video experiment are in `device_power/power_data_provenance_demo.csv` and `device_power/power_experiments.csv` respectively. All of the plots are in the `figs/` directory.


