import pytest
import getpass
import datetime
import gtrends

#SETUP
username = getpass.getpass("username: ")
password = getpass.getpass("password: ")
startDt = datetime.datetime(year=2006, month=1, day=1)
#countMonth = 1 for daily and 5 for weekly


#TEST

def testDownloadOneFile():
	report = gtrends._downloadReport(username, password, ["banana"], startDt, 1,
				1, '2m', '', '', '', '')
	assert len(report) == 1

def testDownloadTwoFile():
	report = gtrends._downloadReport(username, password, ["banana"], startDt, 1,
				1, '2m', '', '', '', '')
	assert len(report) == 1