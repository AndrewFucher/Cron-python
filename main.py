from crontab import CronTab
from croniter import croniter

from datetime import datetime

import os

import logging

from config import *

def getJobsList(tab_file_name):
    """Crontab file parser"""

    cron = CronTab(tabfile=tab_file_name)

    jobs_list = []

    # job_comment = ""
    job_command = ""
    job_time = ""

    datetime_to_start_cron = datetime.now()

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

    datetime_now = datetime.now()

    try:
    
        return_value = os.system(command)
    
    except Exception as e:

        logging.error("{}: error:\n{}".format(datetime_now, e))
    
    finally:
        logging.info("{}: Exit status: {}. Command to complete: {}".format(datetime_now, return_value, command))
        os._exit(return_value)

def loop(jobs_list):
    """Running an infinity loop and checking times of all jobs to be done"""

    # Create array to check the time
    
    jobs_time_to_check = []

    for job_time, command in jobs_list:
        jobs_time_to_check.append(job_time.get_next(datetime))

    while True:

        for i in range(len(jobs_time_to_check)):

            time_now = datetime.now()
            time_now = time_now.replace(microsecond=0, second=0)

            # print(jobs_time_to_check[i], time_now)

            if jobs_time_to_check[i] == time_now:
                
                jobs_time_to_check[i] = jobs_list[i][0].get_next(datetime)
                
                pid = os.fork()
                
                if pid > 0:
                    continue
                else:
                    runCommand(jobs_list[i][1])
                

if __name__ == "__main__":

    # Parsing congiguration (well, just setting value to the new variable)
    config = CONFIGURATION_INFO

    # Parsing crontab file to get list of jobs (time, command)
    jobs_list = getJobsList(config["CrontabFileName"])

    # Setting logging configuration
    logging.basicConfig(filename="logs.log",
    filemode="a",
    level=config["LoggingLevel"],
    format="%(levelname)s:%(message)s")

    # Starting infinity loop
    loop(jobs_list)
