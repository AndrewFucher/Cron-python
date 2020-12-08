from crontab import CronTab
from croniter import croniter

from datetime import datetime, timedelta, timezone

import os
import signal
import sys

import logging

from config import *

def changeSystemTime():
    """Do not touch that poo"""
    import ctypes
    import ctypes.util
    import time

    # time_tuple = ( 2012, # Year
    #               9, # Month
    #               6, # Day
    #               0, # Hour
    #              38, # Minute
    #               0, # Second
    #               0, # Millisecond
    #           )
    
    if config["TestDST"]["ChangeTimeTo"] == "Summer":

        time_tuple = (
            config["TestDST"]["WinterToSummer"]["year"],
            config["TestDST"]["WinterToSummer"]["month"],
            config["TestDST"]["WinterToSummer"]["day"],
            config["TestDST"]["WinterToSummer"]["hour"],
            config["TestDST"]["WinterToSummer"]["minute"],
            config["TestDST"]["WinterToSummer"]["second"],
            config["TestDST"]["WinterToSummer"]["millisecond"]
        )

    if config["TestDST"]["ChangeTimeTo"] == "Winter":

        time_tuple = (
            config["TestDST"]["SummerToWinter"]["year"],
            config["TestDST"]["SummerToWinter"]["month"],
            config["TestDST"]["SummerToWinter"]["day"],
            config["TestDST"]["SummerToWinter"]["hour"],
            config["TestDST"]["SummerToWinter"]["minute"],
            config["TestDST"]["SummerToWinter"]["second"],
            config["TestDST"]["SummerToWinter"]["millisecond"]
        )

    import subprocess
    import shlex

    time_string = datetime(*time_tuple).isoformat()

    subprocess.call(shlex.split("timedatectl set-ntp false"))  # May be necessary
    subprocess.call(shlex.split("sudo date -s '%s'" % time_string))
    subprocess.call(shlex.split("sudo hwclock -w"))

def getJobsList(tab_file_name):
    """Crontab file parser"""

    cron = CronTab(tabfile=tab_file_name)

    jobs_list = []

    # job_comment = ""
    job_command = ""
    job_time = ""

    # Default value
    datetime_to_start_cron = datetime.now()

    # if we test for DST
    # if config["TestDST"]["TestDST"]:
    #     datetime_to_start_cron = datetime.now(timezone.utc)
    #     if config["TestDST"]["ChangeTimeTo"] == "Summer":
    #         datetime_to_start_cron = datetime_to_start_cron.replace(
    #             year=config["TestDST"]["WinterToSummer"]["year"],
    #             month=config["TestDST"]["WinterToSummer"]["month"],
    #             day=config["TestDST"]["WinterToSummer"]["day"],
    #             hour=config["TestDST"]["WinterToSummer"]["hour"],
    #             minute=config["TestDST"]["WinterToSummer"]["minute"],
    #             second=config["TestDST"]["WinterToSummer"]["second"]
    #         )
    #         datetime_to_start_cron = datetime_to_start_cron - timedelta(minutes=config["TestDST"]["TimeBeforeDSTInMinutes"])

    for job in cron:

        job_command = ""
        job_time = ""

        job_command = job.command

        for t in job:
            job_time = job_time + str(t) + " "

        job_time_in_croniter = croniter(job_time, datetime_to_start_cron)
        # job_time_in_croniter.get_next()

        jobs_list.append([job_time_in_croniter, job_command])

    return jobs_list

def runCommand(command):

    try:
    
        return_value = os.system(command)
        # logging.info("")
        logging.info("Succesfuly executed command: '{}'".format(command))
    except Exception as e:

        logging.error("Error:{}, CommandToExecute: '{}'".format(e, command))
    
    finally:
        # os._exit(return_value)
        # os.kill(os.getpid(), signal.SIGKILL)
        sys.exit(return_value)

def loop(jobs_list):
    """Running an infinity loop and checking times of all jobs to be done"""

    # Create array to check the time
    
    jobs_time_to_check = []

    for job_time, command in jobs_list:
        jobs_time_to_check.append(job_time.get_next(datetime))
    
    if len(jobs_time_to_check) > 0:
        pass
    else:
        logging.info("Nothing to execute. Check if there is any commands and their spelling is right. End of program")
        os._exit(0)

    # time_test = datetime(
    #     datetime.now().year,
    #     datetime.now().month,
    #     datetime.now().day,
    #     hour=datetime.now().hour,
    #     minute=datetime.now().minute,
    #     second=datetime.now().second,
    #     microsecond=datetime.now().microsecond
    # )

    # time_test = datetime.now()

    # if config["TestDST"]["TestDST"]:
    #     time_test = datetime(
    #         year=config["TestDST"]["WinterToSummer"]["year"],
    #         month=config["TestDST"]["WinterToSummer"]["month"],
    #         day=config["TestDST"]["WinterToSummer"]["day"],
    #         hour=config["TestDST"]["WinterToSummer"]["hour"],
    #         minute=config["TestDST"]["WinterToSummer"]["minute"],
    #         second=config["TestDST"]["WinterToSummer"]["second"]
    #     )
    #     time_test = time_test - timedelta(minutes=config["TestDST"]["TimeBeforeDSTInMinutes"])

    # time_starting_point = datetime.now()
    # time_delta = datetime.now() - time_test

    while True:

        # print((datetime.now() - time_starting_point).total_seconds() / 60.0)

        for i in range(len(jobs_time_to_check)):

            # TODO
            time_now = datetime.now()
            time_now = time_now.replace(microsecond=0, second=0)

            # Check if we test for the time change
            # if config["TestDST"]["TestDST"]:
            #     time_now = datetime.now() - time_delta
            #     time_now = time_now.replace(microsecond=0, second=0)
                

            print(jobs_time_to_check[i], time_now)

            if jobs_time_to_check[i] == time_now:
                
                jobs_time_to_check[i] = jobs_list[i][0].get_next(datetime)
                
                pid = os.fork()
                
                if pid > 0:
                    # Allows to prevent zombie processes. But cannot access exit code from parent afterwards
                    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
                    continue
                else:
                    runCommand(jobs_list[i][1])
                

if __name__ == "__main__":

    # Parsing congiguration (well, just setting value to the new variable)
    config = CONFIGURATION_INFO

    # If u want to live to the old days then do not uncomment next lines
    # if config["TestDST"]["TestDST"]:
        # changeSystemTime()

    # Parsing crontab file to get list of jobs (time, command)
    jobs_list = getJobsList(config["CrontabFileName"])

    # Setting logging configuration
    logging.basicConfig(filename="logs.log",
    filemode="a",
    level=config["LoggingLevel"],
    format="[%(asctime)s]:%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S")

    # Logging the start of program work
    logging.info("Start of program")

    # Starting infinity loop
    loop(jobs_list)

    # print(jobs_list[0][0].get_next(datetime))
    # datetime = datetime.replace(hour=(datetime.now().hour-1))
    # datetime.now()
    
