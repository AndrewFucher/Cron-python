# 
# In configuration you have to set name of crontab file
# and level of logging (INFO, DEBUG, WARNING, ERROR, CRITICAL)
# 
from logging import DEBUG, WARNING, INFO, ERROR, CRITICAL

CONFIGURATION_INFO = {
    "LoggingLevel" : INFO,
    "CrontabFileName" : "crontab.tab",
    "TestDST" : {
        "TestDST" : True,
        # Summer: Winter -> Summer
        # Winter: Summer -> Winter
        "ChangeTimeTo" : "Summer",
        "TimeBeforeDSTInMinutes" : 1,
        # Default set when DST occure. Sets as a time when it really occurce,
        # Otherwise program will set current time by UTC to that minus TimeBeforeDSTInMinutes
        "SummerToWinter" : {
            "year" : 2020,
            "month" : 10,
            "day" : 31,
            "hour" : 1,
            "minute" : 0,
            "second" : 0,
            "millisecond" : 0
        },
        "WinterToSummer" : {
            "year" : 2020,
            "month" : 3,
            "day" : 28,
            "hour" : 1,
            "minute" : 0,
            "second" : 0,
            "millisecond" : 0
        }
    } 
}