#!/bin/bash
x0vncserver -kill
sleep 2
# What's the script name
#SCRIPTNAME="startvnc"

# Where the x0vncserver executable is located, default:
#VNCSERVER="/usr/bin/x0vncserver"

# Set home directory
#HOMEDIR=${HOME}

# Default VNC User directory
#VNCDIR="${HOMEDIR}/.vnc"

# Set log file for debugging
#LOGFILE="${VNCDIR}/logfile"

# The vnc passwd file. If it doesn't exist, you need to create it
#PASSWDFILE="${VNCDIR}/passwd"

# Leave this on ":0", since we want to log in to the actual session
#DISPLAY=":0"

# Set the port (default 5900)
#VNCPORT="5900"

# PID of the actual VNC server running
# The PID is actually created this way, so it is compatible with the vncserver command
# if you want to kill the VNC server manually, just type 
# vncserver -kill :0
#PIDFILE="${VNCDIR}/${HOSTNAME}${DISPLAY}.pid"

# Add some color to the script
#OK="[\033[1;32mok\033[0m]"
#FAILED="[\033[1;31mfailed\033[0m]"
#RUNNING="[\033[1;32mrunning\033[0m]"
#NOTRUNNING="[\033[1;31mnot running\033[0m]"

# Function to get the process id of the VNC Server
#fn_pid() {
#    CHECKPID=$(ps -fu ${USER} | grep "[x]0vncserver" | awk '{print $2}')
#    if [[ ${CHECKPID} =~ ^[0-9]+$ ]] 
#    then
#        VAR=${CHECKPID}
#        return 0
#    else
#        return 1
#    fi
#}


#if [ ! -d ${VNCDIR} ]
#then
#    echo -e "Directory ${VNCDIR} doesn't exist. Create it first." ${FAILED}
#    echo
#    exit 1
#fi

#if [ ! -f ${PASSWDFILE} ]
#then
#    echo -e "${PASSWDFILE} doesn't exist. Create VNC password first. ${FAILED}"
#    echo "Type \"vncpasswd\" to create passwd file."
#    echo
#    exit 1
#fi
#        echo -n "Stopping VNC Server: "
#        fn_pid
#        if [ $? -eq 0 ]
#        then
#            kill -9 ${VAR}
#            echo -ne ${OK}
#            echo -e " (pid: ${VAR})"
#	    echo
#        else
#            echo -e ${FAILED}
#            echo -e "VNC Server is not running."
#	    echo
#            exit 1
#        fi
