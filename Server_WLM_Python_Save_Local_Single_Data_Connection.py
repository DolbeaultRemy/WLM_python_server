import socket
import wlmData
import sys
import time
import os
import numpy as np

"""" Return the wavelengths of the corresponding channels (list), pressure and temperature """
def read_WLM_Lambda_P_T(channels):
    res = []
    for c in channels:
        res.append(wlmData.dll.GetWavelengthNum(c, 0))
    res.append(wlmData.dll.GetPressure(0.0))
    res.append(wlmData.dll.GetTemperature(0.0))
    return res

# User data
DLL_PATH = "wlmData.dll"
channels = [1, 2, 4]
time_step = 500 # In ms
HOST = "10.44.1.21"  # Ethernet IPadress  of laptop connected to WLM
PORT = 3601  # Port of the server
save_every = 100 # Save the data every save_every pts
data_name = "Data_Drift_WLM_Lambdas_P_T_2025_10_15_09h.txt"

# Load DLL from DLL_PATH
try:
    wlmData.LoadDLL(DLL_PATH)
except:
    sys.exit("Error: Couldn't find DLL on path %s. Please check the DLL_PATH variable!" % DLL_PATH)

# Check if exposure times < time_step
Time_exp = []
for c in channels:
    Time_exp.append(wlmData.dll.GetExposureNum(c, 1, 0))
max_time_exp = max(Time_exp)

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.setblocking(False) # Non blocking mode
sock.listen()

# Create saving folder
if not(os.path.isdir("SavedData")):
    os.mkdir("SavedData")

if time_step > 2*max_time_exp: # Time step 2 times bigger than exposition
    # Initialize
    t_start = time.time()
    Data = np.zeros((save_every, len(read_WLM_Lambda_P_T(channels))+1))
    Data[0, 0], Data[0, 1:] = 0, np.array(read_WLM_Lambda_P_T(channels))
    count = 1 # Count the nbr of acquisitions to save every save_every, starts at 1 as we initialized the arrays

    while True:

         # Save the data every save_every step
        if count % save_every == 0:
            print("Save the data")
            file = open("SavedData/"+data_name, "a")
            np.savetxt(file, Data[count-save_every:count, :])
            file.close()
            count = 0

        t = (time.time() - t_start)*1e3
        while t - Data[count-1, 0] < time_step: # Trigger an acquisition when t = time_step has passed
            t = (time.time() - t_start)*1e3 # In ms
        Data[count, 0] = t
        Data[count, 1:] = read_WLM_Lambda_P_T(channels)
        
        # Tries to connect to a client, if it works sends the last acquisition
        try:
            client, addr = sock.accept()

            # Prepare data of the last acquisition for sending over the server
            data = ""
            for d in Data[count]:
                data += str(d)+";"

            client.sendall(data[:-1].encode())

            print("Send last acquisition to %s:" %(addr[0]))
            print(data[:-1])
            client.close()
        except:
            pass

        count += 1
else:
    print("Time step too small")