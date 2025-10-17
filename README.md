# WLM_python_server
Read the WLM server and send the data over a python socket.
The Server_WLM_Python_Save_Local_Single_Data_Connection.py sends only one data acquisition and then close the connection with the client. It is compatible between Windows and Linux.
The Server_WLM_Python_Save_Local_Many_Data_Connection.py can send many different acquisition before closing the socket, but it doesn't work with a linux client.
The wlmConst.py and wlmData.py are the C functions used to read from the WLM.
