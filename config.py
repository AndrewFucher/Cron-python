# 
# In configuration you have to set name of crontab file
# and level of logging (INFO, DEBUG, WARNING, ERROR, CRITICAL)
# 
from logging import DEBUG, WARNING, INFO, ERROR, CRITICAL

CONFIGURATION_INFO = {
    "LoggingLevel" : INFO,
    "CrontabFileName" : "mycrontab.tab"
}