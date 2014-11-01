#on run this program sends an email to the 
#given address containg the IP address 
#in the meassage body and subject line. 
#thiscode is based on that found here:
#http://cagewebdev.com/index.php/raspberry-pi-sending-emails-on-boot/
#http://elinux.org/RPi_Email_IP_On_Boot_Debian
#@author: Jeremy Blythe
#http://jeremyblythe.blogspot.co.uk/2013/03/raspberry-pi-system-monitor-embedded-on.html

#this programm apends a .csv file started at boot by startup_mailer.py
#the file name is a timestamp at boot time bystartup_mailer.py
#a pickle file flie_list.pickle stores the file name between runs

import subprocess
import smtplib
import socket
import os
from email.mime.text import MIMEText
import datetime
import time
import pickle

# Change to your own account information

to = 'user to send to @gmail.com'
gmail_user = 'your_email@gmail.com'
gmail_password = 'your password'
smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
smtpserver.ehlo()
smtpserver.starttls()
smtpserver.ehlo
smtpserver.login(gmail_user, gmail_password)
today = datetime.date.today()

#Determine the IP Address 

def get_ipaddr():
    try:
        arg='ip route list'
        p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
        data = p.communicate()
        split_data = data[0].split()
        return (split_data[split_data.index('src')+1])
    except:
        return 0


# report time now
from time import gmtime, strftime
time_now = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

def get_ram():
    "Returns a tuple (total ram, available ram) in megabytes. See www.linuxatemyram.com"
    try:
        s = subprocess.check_output(["free","-m"])
        lines = s.split('\n')       
        return ( int(lines[1].split()[1]), int(lines[2].split()[3]) )
    except:
        return 0
 
def get_process_count():
    "Returns the number of processes"
    try:
        s = subprocess.check_output(["ps","-e"])
        return len(s.split('\n'))       
    except:
        return 0
 
def get_up_stats():
    "Returns a tuple (uptime, 5 min load average)"
    try:
        s = subprocess.check_output(["uptime"])
        load_split = s.split('load average: ')
        load_five = float(load_split[1].split(',')[1])
        up = load_split[0]
        up_pos = up.rfind(',',0,len(up)-4)
        up = up[:up_pos].split('up ')[1]
        return ( up , load_five )       
    except:
        return ( '' , 0 )
 
def get_connections():
    "Returns the number of network connections"
    try:
        s = subprocess.check_output(["netstat","-tun"])
        return len([x for x in s.split() if x == 'ESTABLISHED'])
    except:
        return 0
     
def get_temperature():
    "Returns the temperature in degrees C"
    try:
        s = subprocess.check_output(["/opt/vc/bin/vcgencmd","measure_temp"])
        return float(s.split('=')[1][:-3])
    except:
        return 0


# The information to report 
ip_rpt = 'IP address: ' +str(get_ipaddr())
temp_rpt = 'Temperature in C: ' +str(get_temperature())
conn_rpt = 'Nr. of connections: '+str(get_connections())
ram_rpt = 'Free RAM: '+str(get_ram()[1])+' ('+str(get_ram()[0])+')'
proc_rpt= 'Nr. of processes: '+str(get_process_count())
uptime_rpt = 'Up time: '+get_up_stats()[0]


#send email

mail_body = 'Hello Dr Hills.\n \n It is now: ' + time_now +  '\n ' +  ip_rpt + '\n' + ram_rpt + '\n ' + proc_rpt + '\n' + uptime_rpt + '\n' + conn_rpt +'\n' + temp_rpt + '\n' 
msg = MIMEText(mail_body)
msg['Subject'] = 'RasPI @ '+ ip_rpt +' started up on %s' % today.strftime('%b %d %Y')
msg['From'] = gmail_user
msg['To'] = to
smtpserver.sendmail(gmail_user, [to], msg.as_string())
smtpserver.quit()



#WRITE FILE  
#this section writes a file containg the above information.  The filename is timestamped
# the file can be updated in another programme triggered periodocly e.g in crontab)
#The file is writte to a directoy /home/pi/sysstat_file/


    #Reading the last runs values from a pickle file.

f = open('flie_list.pickle')
file_list = pickle.load(f)
f.close()

#Create file .csv with time stamp name and that contains the curretnt System Stats at statup

time_stmp = strftime("%Y%m%d%H%M%S",gmtime())

#the file name will be "YEARMODATETIME.csv"

file_name = file_list[0]

data = strftime("%Y,%m,%d,%H,%M,%S",gmtime()), time_stmp, get_up_stats()[0], str(get_ipaddr()), str(get_temperature()), str(get_connections()), str(get_ram()[1]), str(get_process_count())

f =  open('/home/pi/sysstat_file/'+file_name, 'a')
#f.write(data_structure+"\n")
for item in data:
    f.write (str(item)+ ",")
f.write("\n")
f.close()


