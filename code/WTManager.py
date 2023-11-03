##### Functions used #####
import lvm_read
import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

class WTmanager:
    def __init__(self,file_path, flag_output=False):
        current_directory = os.getcwd()
        cwd_manager = os.path.exists(os.path.join( \
            current_directory,"AllFiles.p"))
        fp_manager = os.path.exists(os.path.join( \
            file_path,"AllFiles.p"))
        if cwd_manager:
            with open(os.path.join(current_directory, "AllFiles.p"), "rb") \
                as filename:
                all_files = pickle.load(filename)
        elif fp_manager:
            with open(os.path.join(file_path, "AllFiles.p"), "rb") \
                as filename:
                all_files = pickle.load(filename)
        else:
            all_files = generate_guide_file(file_path)
        self.__lvm = None
        self.__all_files = all_files
        display(all_files.head())
        print("\n##########\nPossible values:\n##########")
        print('Cases:', all_files['Case'].unique())
        print('Temperature:', all_files['Temperature'].unique())
        print('Sensor_scheme:', all_files['Sensor_scheme'].unique())
        print('Wave_type:', all_files['Wave_type'].unique())
        print('Wave:', all_files['Wave'].unique())
        print('Total number of cases:', all_files.shape[0])
        if flag_output:
            return all_files

    def get_all_files(self):
        return self.__all_files

    def load(self, case="A", temp="(+00)", scheme="1", \
        wave="sine_sweep", flag_output=False):
        file = specific_case_address(self.__all_files, case, temp, scheme, wave)
        ##### Loading #####
        lvm = lvm_read.read(file, read_from_pickle=False)
        ##### Looking inside the lvm #####
        print('LVM Keys:', lvm.keys())
        print('LVM presents '+str(len(lvm[0]['Channel names']))+' channels')
        print('With the names:', lvm[0]['Channel names'])
        self.__lvm = lvm
        if flag_output:
            return lvm


#############################
##### GENERAL FUNCTIONS #####
#############################

##### Function to generate a guide file #####
def generate_guide_file(file_path, return_file=1):
    cwd = os.getcwd()
    case_vector = ['R','A','B','C','D','E','F','G','H','I','J','K','L']
    temperature_vector = ['(+00)','(+05)','(+10)','(+15)','(+20)','(+25)','(+30)','(+35)','(+40)','(-05)','(-10)','(-15)']
    sensors_scheme_vector = ['1','2']
    wave_type = ['sine_sweep','white_noise_']
    all_files = pd.DataFrame([], columns=['Case','Temperature','Sensor_scheme','Wave_type','Wave','Address'])

    for case in range(len(case_vector)):
        for temp in range(len(temperature_vector)):
            for scheme in range(len(sensors_scheme_vector)):
                waves = [wave_type[0]]
                if case_vector[case] == 'R':
                    for i in range(20):
                        waves.append(wave_type[1]+str(i+1))
                else:
                    for i in range(5):
                        waves.append(wave_type[1]+str(i+1))
                for signal in range(len(waves)):
                    directory='Case_'+case_vector[case]+'_'+temperature_vector[temp]
                    directory=directory+'\\'+directory+'_'+sensors_scheme_vector[scheme]+'\\'
                    filename=waves[signal]+'.lvm'
                    file=file_path+directory+filename
                    if signal==0:
                        wtype = wave_type[0]
                    else:
                        wtype = wave_type[1][:-1]
                    all_files = all_files.append(
                        pd.concat(
                            [   
                                pd.DataFrame([case_vector[case]], columns=['Case']),
                                pd.DataFrame([temperature_vector[temp]], columns=['Temperature']),
                                pd.DataFrame([sensors_scheme_vector[scheme]], columns=['Sensor_scheme']),
                                pd.DataFrame([wtype], columns=['Wave_type']),
                                pd.DataFrame([waves[signal]], columns=['Wave']),
                                pd.DataFrame([file], columns=['Address']),
                            ],
                            axis=1,
                        ),
                        ignore_index=True,
                    )

    with open(os.path.join(os.getcwd(), "AllFiles.p"), "wb") as fname:
        pickle.dump(all_files, fname)

    print('Guide file saved!')

    if return_file==1:
        return all_files


def get_signal(lvm_object, signal_name):
    wanted_signal_index  = lvm_object[0]['Channel names'].index(signal_name)
    return lvm_object[0]['data'][:,wanted_signal_index]


def approx(signal, desired_value):
    return min(range(len(signal)), key=lambda i: abs(signal[i]-desired_value))


##### Address for a specific case, based on guide file #####
def specific_case_address(guide, case, temperature, sensor_scheme, wave_type):
    Addresses = guide[(guide['Case']==case) & (guide['Temperature']==temperature) & (guide['Sensor_scheme']==sensor_scheme) & (guide['Wave']==wave_type)]['Address']
    return Addresses.values[0]


##############################
##### PLOTTING FUNCTIONS #####
##############################

##### Functions to plot #####
def force_analysis(lvm, flag_plot=1, name=0):
    indTime  = lvm[0]['Channel names'].index("X_Value")
    indForce = lvm[0]['Channel names'].index("force")
    Time = lvm[0]['data'][:,indTime]
    Force = lvm[0]['data'][:,indForce]
    if flag_plot==1:
        plt.figure(figsize=(12,8))
        plt.plot(Time, Force)
        plt.xlabel('Time (s)')
        plt.ylabel('Force (N)')
        plt.grid()
        plt.show()
        if type(name)==np.str:
            plt.savefig(name+'.png', format='png', bbox_inches='tight', dpi=300)

