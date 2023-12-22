#!/bin/bash

# Replace "/path/to/directory" with the path of the folder you want to open.
FOLDER_PATH="/home/seaonics/Desktop/scripts_seaonics/genicam"

# Replace "your_command_here" with the command you want to execute in the folder.
COMMAND1="source ./venv/bin/activate"
COMMAND2="python3 gentl_rtsp_server.py"

# Check if the folder exists
if [ -d "$FOLDER_PATH" ]; then
    # Open the folder in terminal
    cd "$FOLDER_PATH"
    echo "Opened folder: $FOLDER_PATH"
    
    # Execute the command
    echo "Executing command: $COMMAND1"    
    eval $COMMAND1

    # Execute the command
    echo "Executing command: $COMMAND2"    
    eval $COMMAND2

    # Keep the terminal open (on some systems, like macOS)
    exec $SHELL
else
    echo "Folder does not exist: $FOLDER_PATH"
fi
