# -*- coding: utf-8 -*-
import pytest
import getpass
import datetime
import gtrends

#SETUP

username = getpass.getpass("username: ")
password = getpass.getpass("password: ")
startDt = datetime.datetime(year=2006, month=1, day=1)
#countMonth = 1 for daily and 5 for weekly


#TEST DOES DOWNLOAD?

#many files
def testDownloadOneFile():
	report = gtrends._downloadReport(username, password, ["banana"], startDt, 1,
				1, '2m', '', '', '', '')
	assert len(report) == 1

def testDownloadTwoFile():
	report = gtrends._downloadReport(username, password, ["banana"], startDt, 2,
				1, '2m', '', '', '', '')
	assert len(report) == 2

def testDownloadThreeFile():
	report = gtrends._downloadReport(username, password, ["banana"], startDt, 3,
				1, '2m', '', '', '', '')
	assert len(report) == 3

#many terms
def testDownloadTwoTerms():
	report = gtrends._downloadReport(username, password, ["banana", "pie"], startDt, 1,
				1, '2m', '', '', '', '')
	assert len(report) == 1

def testDownloadThreeTerms():
	report = gtrends._downloadReport(username, password, ["banana", "pie", "mango"], startDt, 1,
				1, '2m', '', '', '', '')
	assert len(report) == 1

#weird input
def testDownloadUnicode():
	report = gtrends._downloadReport(username, password, [u"banana"], startDt, 1,
				1, '2m', '', '', '', '')
	assert len(report) == 1

def testDownloadUnicodeLatinChar():
	report = gtrends._downloadReport(username, password, ["café"], startDt, 1,
				1, '2m', '', '', '', '')
	assert len(report) == 1

def testDownloadUnicodeNonLatinChar():
	report = gtrends._downloadReport(username, password, ["咖啡店"], startDt, 1,
				1, '2m', '', '', '', '')
	assert len(report) == 1

def testDownloadNum():
	report = gtrends._downloadReport(username, password, ["666"], startDt, 1,
				1, '2m', '', '', '', '')
	assert len(report) == 1

def testDownloadPunct():
	report = gtrends._downloadReport(username, password, "~!@#$%^&*()_+-=;':[]{]\|,<.>/?}]", startDt, 1,
				1, '2m', '', '', '', '')
	assert len(report) == 1


#extra attributes (countries, categories, timezones, etc.)
def testDownloadGeo():
	report = gtrends._downloadReport(username, password, ["ciao"], startDt, 1,
				1, '2m', 'IT', '', '', '')
	assert len(report) == 1

def testDownloadCat():
	report = gtrends._downloadReport(username, password, ["ciao"], startDt, 1,
				1, '2m', '', '0-7', '', '')
	assert len(report) == 1

def testDownloadSearchType():
	report = gtrends._downloadReport(username, password, ["ciao"], startDt, 1,
				1, '2m', '', '', 'news', '')
	assert len(report) == 1

def testDownloadTZ():
	report = gtrends._downloadReport(username, password, ["ciao"], startDt, 1,
				1, '2m', '', '', '', 'America/Detroit')
	assert len(report) == 1





#TEST CORRECT DOWNLOAD?

#many terms
def testDownloadOneTermCorr():
	report = gtrends._downloadReport(username, password, ["banana"], startDt, 1,
				1, '2m', '', '', '', '')
	lines = report[0].split("\n")
	assert "banana" in lines[0]

def testDownloadTwoTermCorr():
	report = gtrends._downloadReport(username, password, ["banana", "albero"], startDt, 1,
				1, '2m', '', '', '', '')
	lines = report[0].split("\n")
	assert "banana" in lines[0] and "albero" in lines[0]

def testDownloadFiveTermCorr():
	report = gtrends._downloadReport(username, password, ["banana", "albero", "finestra", "tutelare", "ambiente"], startDt, 1,
				1, '2m', '', '', '', '')
	lines = report[0].split("\n")
	assert "banana" in lines[0] and "albero" in lines[0] and "finestra" in lines[0] and "tutelare" in lines[0] and "ambiente" in lines[0]


#extra attributes (countries, categories, timezones, etc.)
def testDownloadGeoRight():
	report = gtrends._downloadReport(username, password, ["ciao"], startDt, 1,
				1, '2m', 'IT', '', '', '')
	lines = report[0].split("\n")
	assert "Italy" in lines[1]

def testDownloadCat():
	report = gtrends._downloadReport(username, password, ["ciao"], startDt, 1,
				1, '2m', '', '0-71', '', '')
	assert "Food & Drink" in report[0]

def testDownloadSearchType():
	report = gtrends._downloadReport(username, password, ["ciao"], startDt, 1,
				1, '2m', '', '', 'news', '')
	lines = report[0].split("\n")
	assert "News" in lines[0]

#there is no way to test TZ, so I leave this as an exercize to the reader.
# def testDownloadTZ():
# 	report = gtrends._downloadReport(username, password, ["ciao"], startDt, 1,
# 				1, '2m', '', '', '', 'America/Detroit')
# 	assert ?