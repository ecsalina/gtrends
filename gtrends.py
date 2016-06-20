import os
import time
import csv
import datetime
import math
from fractions import *
try:
    import urllib.parse as urllib
except ImportError:
    import urllib

from _login import Downloader

def collectTrends(username, password, terms, startDt, endDt, granularity='d',
					geo='', cat='', gprops='', tz='', sum=False, savePath=None):
	"""
	Downloads normalized Google trend data between [startDt, endDt).

	Args:
		username: A string representing a Google username.
		password: A string representing the corresponding Google password.
		terms: A tuple of strings whose query volume is to be searched.
		startDt: A datetime object for the start of the period (inclusive).
			Only the month and year are considered.
		endDt: A datetime object for the end of the period (exclusive).
			Only the month and year are considered.
		granularity: The frequency with which the data should be spread.
			This can be: 'd'-> daily, or 'w'-> weekly.
		geo: A string representing a specific country to query.
			Ex: US, UK, DE, FR, etc.
		cat: A string representing the specific category code desired.
		gprops: A string representing the type of search to be included.
			Ex: images, news, froogle, and youtube
		tz: A string representing the desired timezone.
		sum: Sum values of multiple terms by day/week before normalizing.
		savePath: A string for the file path where the data can be saved

	Returns:
		A list where each line is a list of format:
		[datetime, value1, value2, value3, etc.], where "datetime" is the
		datetime of the query volume, and "value" is a float of the normalized
		query volume (between [0.0, 100.0]), where the largest value is
		set to 100. There is a header on the first line, with format:
		"date,term1,term2,term3, ... termN" where N is the total number of terms.
		Returns empty list if error.

	"""
	#General checks:
	if granularity != 'd' and granularity != 'w':
		print("Error: Granularity must be 'd' or 'w,' not "+granularity)
		return []
	if startDt > endDt:
		print("Error: startDt must come earlier in time than endDt")
		return []
	if startDt < datetime.datetime(month=1, day=1, year=2004):
		print("Error: Google Trends does not provide data before 2004, your start date was: "+str(startDt))
		return []
	if endDt > datetime.datetime.today():
		print("Error: Google Trends cannot see the future, your end date is : "
				+str(endDt)+", which is later than today")
		return []
	if not terms:
		print("Error: terms tuple is empty, please provide a populated tuple")
		return []

	#all set to download files:
	else:
		#Note: Always overlap by 1 month (which is why count = freq-1 ).
		if granularity == "d":
			countMonth = 1
			freq = "2m"

		else: #granularity == "w":
			countMonth = 5
			freq = "6m"

		numYears = endDt.year - startDt.year
		numMonths = endDt.month - startDt.month
		numMonths += numYears*12
		numFiles = float(numMonths) / countMonth
		numFiles = int(math.ceil(numFiles))

		#Packages terms into lists of 5 (the max that can be
		#queried at once).
		segmentedTerms = _packTerms(terms)
		reportData = []
		for segTerms in segmentedTerms:
			#download each 2m file csv as a string
			rawReport = _downloadReport(username, password, segTerms,
				startDt, numFiles, countMonth, freq, geo, cat, gprops, tz)
			#format rawReport into list of each multi-month list.
			report = _prepTrends(rawReport, startDt, numFiles, countMonth, granularity)
			#if there is nothing in the report data, then return empty list.
			if not report:
				print("Error: at least one file was unable to be downloaded."
					" Perhaps your search terms are invalid")
				return []

			reportData.append(report)

		#if, in the same period, between two sets, the added constant
		#term changes scale, then we must scale the second set to meet
		#the first one.
		scaleReports = _scaleRep(reportData)
		#when more than 4 terms, merge reports into single report.
		mergeTrend = _merge(scaleReports)
		initValues = mergeTrend[0][0]
		#calculate the percent change between subsequent data points
		#and merge monthly lists.
		percTrend = _calcPerc(numFiles, mergeTrend)
		#convert back into levels, all on same scale.
		reformTrend = _reformTrend(percTrend, initValues)
		if sum == True:
			#sum terms query volumes together.
			reformTrend = _calcSum(reformTrend)

		#normalized between [0.0,100.0].
		normTrend = _normalize(reformTrend)
		#trim off extra days, which only occur with granularity='w'
		trimTrend = _trim(normTrend, endDt)
		#add header.
		finalTrend = _addHeader(trimTrend, terms)
		if savePath != None:
			_save(savePath, finalTrend)

		return finalTrend




def collectRawTrends(username, password, terms, startDt, endDt, geo='', cat='', gprops='', tz='', savePath=None):
	"""
	Downloads raw Google Trends data.

	The most basic download function. Simply downloads the raw csv file from
	Google Trends as a string. No transformations are performed on any of the
	data.

	Args:
		username: A string representing a Google username.
		password: A string representing the corresponding Google password.
		terms: A tuple of strings whose query volume is to be searched. Google
			only accepts 5 terms per query.
		startDt: A datetime object for the start of the period (inclusive).
			Only the month and year are considered.
		endDt: A datetime object for the end of the period (exclusive).
			Only the month and year are considered.
		savePath: A string for the file path where the data can be saved

	Returns:
		A list of 1 string representing the entire downloaded csv.

	"""
	#General checks:
	if startDt > endDt:
		print("Error: startDt must come earlier in time than endDt")
		return []
	if startDt < datetime.datetime(month=1, day=1, year=2004):
		print("Error: Google Trends does not provide data before 2004, your start date was: "+str(startDt))
		return []
	if endDt > datetime.datetime.today():
		print("Error: Google Trends cannot see the future, your end date is : "
				+str(endDt)+", which is later than today")
		return []
	if not terms:
		print("Error: terms tuple is empty, please provide a populated tuple")
		return []
	if len(terms) > 5:
		print("Error: Google Trends only accepts 5 terms at a time")
		return []

	#all set to download files:
	else:
		numYears = endDt.year - startDt.year
		numMonths = endDt.month - startDt.month
		numMonths += numYears*12
		report = _downloadReport(username, password, terms, startDt, 1, 0, str(numMonths)+"m", geo, cat, gprops, tz)
		if not report:
			print("Error: file was unable to be downloaded.")
			return []
		else:
			if savePath != None:
				_save(savePath, report)

			return report




def _packTerms(terms):
	"""
	Packages terms into lists of 4.
	If the length of terms is not divisible by 4, then the final
	list is short a bit (but this is okay).
	"""
	segmentedTerms = []
	index = 0
	while True:
		endIndex = index + 4
		if endIndex >= len(terms):
			endIndex = len(terms)
			segmentedTerms.append(terms[index : endIndex])
			break
		else:
			segmentedTerms.append(terms[index : endIndex])
			index += 4
			continue
	#this make sure that all data in different segments
	#have the same scaling factor. One of the terms is
	#used in all the segments for scaling, and then removed
	#later
	for seg in segmentedTerms:
		seg.append(terms[0])

	return segmentedTerms




def _downloadReport(username, password, terms, startDt, numFiles,
					countMonth, freq, geo, cat, gprops, tz):
	"""
	Helper function to actually downloading Google trend data.
	Must have a maximum of FIVE terms.
	"""

	report = []

	dloader = Downloader(username, password)

	for i in range(0, numFiles):
		month = startDt.month + i*countMonth
		year = startDt.year
		while month > 12:
			year += 1
			month -= 12
	
		#create query
		query = "http://www.google.com/trends/trendsReport?&q="
		for term in terms:
			query += urllib.quote(term)+"%2C"
		query = query[:-3] #remove final comma
		query += "&geo="+urllib.quote(geo)+"&cat="+urllib.quote(cat)+"&gprop="+urllib.quote(gprops)
		query += "&cmpt=q&content=1&export=1&date="+str(month)+"%2F"+str(year)+"%20"+urllib.quote(freq)
		
		print(query)
	
		data = dloader.downloadReport(query)
		report.append(data)

	return report




def _prepTrends(rawReport, startDt, numFiles, countMonth, granularity):
	"""
	Helper function which reformats data into list of lists with correct data
	types. If anything is empty or has incorrect data, then an empty list is
	returned.
	"""
	#load each rawReport into separate list
	reportData = []
	for i in range(numFiles):
		#convert string to 2d list
		raw = rawReport[i]
		rawLines = raw.split("\n")
		lines = []
		for rawLine in rawLines:
			line = rawLine.split(",")
			lines.append(line)

		#check if the actual granularity matches the desired granularity. If
		#no, then alter to match and continue
		trueGran = lines[4][0]
		if granularity == "d" and trueGran == "Week":
			print("Error: The file returned from Google Trends doesn't match your desired granularity."
				" Altering your desired granularity to match.")
			granularity = 'w'
		if granularity == "w" and trueGran == "Day":
			print("Error: The file returned from Google Trends doesn't match your desired granularity."
				" Altering your desired granularity to match.")
			granularity = 'd'


		#prep data

		#remove header
		lines = lines[5:]

		#remove country data
		for j, line in enumerate(lines):
			if line[0] == "":	#checks if line is empty
				lines = lines[:j]
				break
			else:
				continue

		#remove 2nd month data (except 1st day)
		for j, line in enumerate(lines):
			try:

				if granularity == 'd':
					dt = datetime.datetime.strptime(line[0], "%Y-%m-%d")
				else: #granularity == 'w':
					dt = line[0][:-13]
					dt = datetime.datetime.strptime(dt, "%Y-%m-%d")

				finalMonth = startDt.month + (i+1)*countMonth	#would just use % operator for this
				while finalMonth > 12:							#however it doesn't work bc the range
					finalMonth -= 12							#runs from 1-12, not 0-11

				if dt.month == finalMonth:
					lines = lines[:j+1] #+1 bc we want to keep this first day/week/month
					break
				else:
					continue
			#If there is a ValueError, then there is incorrectly week data,
			#and so we should just return an empty array, bc the data is not
			#correct to begin with.
			except ValueError:
				print("Value Error: Unable to format datetime correctly from file, returning empty list.")
				return []

		#Checks that there is data. If not, then returns empty list.
		if len(lines) == 0:
			return []

		#Saves data to list, which is element of larger list.
		report = []
		for line in lines:
			try:
				newLine = []
				if granularity == 'd':
					dt = datetime.datetime.strptime(line[0], "%Y-%m-%d")
				else: #granularity == 'w':
					dt = line[0][:-13]
					dt = datetime.datetime.strptime(dt, "%Y-%m-%d")
				newLine.append(dt)
				#Removes the final item in the line, which is the constant term
				#This makes sure that there is the same scaling.
				for j in range(1, len(line)-1):
					value = int(line[j])
					newLine.append(value)
				report.append(newLine)

			except ValueError:	#issue with data, return empty list
				print("Value Error: Unable to format datetime correctly from file, returning empty list.")
				return []

		reportData.append(report)

	return reportData



def _scaleRep(reportData):
	"""
	Scales reports of different sets of terms.
	Using the percent change with the 1 month overlap should take care of the
	variation in time of a single report. However, if, at the same moment in
	time, a secondary report contains a term which is larger than the constant
	term and so causes the constant to have different values, then the scale is
	off. To fix this, we select a value for the constant term at the same time
	across the new and old reports. factor = old / new, and multiply factor
	across the new report to have the same scale as the old one.
	"""
	baseMonth = reportData[0][0]
	for i in range(1, len(reportData)):
		testMonth = reportData[i][0]
		factor = 0.0
		for j in range(len(baseMonth)):
			old = baseMonth[j][len(baseMonth[j])-1] #last term in line
			new = testMonth[j][len(testMonth[j])-1]	#ditto
			if abs(new - old) > 3:
				#^means that there is a large difference and we need to scale
				old = 1.0 if old == 0.0 else old
				new = 1.0 if new == 0.0 else new
				factor = old / float(new)
				break
		if abs(factor) >  0.0003:	#in case floating point error
			for j in range(len(reportData[i])):
				for k in range(len(reportData[i][j])):
					for l in range(1, len(reportData[i][j][k])):
						reportData[i][j][k][l] = factor*reportData[i][j][k][l]
	return reportData


def _merge(reportData):
	"""Merges the separate reports into one large report."""
	merged = reportData[0]

	for i in range(1, len(reportData)):							#the report
		for j in range(len(reportData[i])):						#the month(s)
			for k in range(len(reportData[i][j])):				#the line
				for l in range(1, len(reportData[i][j][k])):	#the values in the line
					merged[j][k].append(reportData[i][j][k][l])
	return merged



def _calcPerc(numFiles, report):
	"""Calculates the percent change between subsequent data points."""
	percTrend = []
	#calculate the percent change of each datapoint
	for i in range(numFiles):
		#for first day of first month, percent change is set to 1.
		#for each subsequent month, the percent change on the first
		#day is calculated at the very end of the previous month.
		if len(percTrend) == 0:
			#percent change is set to 1.0 for first day of first month
			newLine = []
			dt = report[0][0][0]
			newLine.append(dt)
			for k in range(1, len(report[0][0])):
				newLine.append(1.0)
			percTrend.append(newLine)


		#go through each day and calculate percent change over prev day
		for j in range(1, len(report[i])):
			newLine = []
			line = report[i][j]
			prevLine = report[i][j-1]

			dt = line[0]
			newLine.append(dt)
			for k in range(1, len(report[i][j])):
				#to avoid divide-by-zero error, set all 0's in data to 1's
				line[k] = 1 if line[k] == 0 else line[k]
				prevLine[k] = 1 if prevLine[k] == 0 else prevLine[k]
				perc = Fraction(line[k], prevLine[k])
				newLine.append(perc)
			percTrend.append(newLine)

	return percTrend




def _reformTrend(percs, inits):
	"""
	Helper function to recreate original trend based on percent change data.
	"""
	trend = []
	trend.append(percs[0])

	for i in range(1, len(percs)):
		newLine = []
		newLine.append(percs[i][0])				#append the date
		for j in range(1, len(percs[i])):		#for each term on date
			level = float(trend[i-1][j]) * percs[i][j].numerator / percs[i][j].denominator	#level is the prev level * %change
			newLine.append(level)

		trend.append(newLine)

	return trend



def _calcSum(data):
	"""
	Sums the values of the reports.
	"""
	trend = []
	for line in data:
		sum = 0.0
		for i in range(1, len(line)):
			sum += line[i]
		dt = line[0]
		trend.append([dt, sum])

	return trend




def _normalize(data):
	"""
	Helper function to normalize data between [0.0, 100.0].
	This is based on largest value found. If the values for individual terms
	are not summed across terms, then this is the largest value among all terms
	as well.
	"""
	maxVal = 0.0
	for i, line in enumerate(data):
		for j in range(1, len(line)):
			if line[j] > maxVal:
				maxVal = line[j]

	trend = []
	for line in data:
		newLine = []
		newLine.append(line[0])
		for j in range(1, len(line)):
			norm = line[j]*100
			norm /= maxVal
			norm = round(norm, 3)
			newLine.append(norm)

		trend.append(newLine)

	return trend


def _trim(data, endDt):
	"""Removes datetime-value pairs >= endDt to the precision of one month."""
	index = 0
	for i,line in enumerate(data):
		if line[0].month == endDt.month and line[0].year == endDt.year:
			index = i
			break
	return data[0:i]



def _addHeader(data, terms):
	header = ["date"]
	if sum == True:
		other = ""
		for term in terms:
			other += " "+term
		header.append(other)
	else:
		for term in terms:
			header.append(term)
	
	trend = []
	trend.append(header)
	for line in data:
		trend.append(line)

	return trend



def _deleteFiles(path, numFiles):
	"""Delete unnecissary Google trend report files."""
	for i in range(numFiles):
		if i == 0:
			name = path+"report.csv"
		else:
			name = path+"report ("+str(i)+").csv"
		os.remove(name)



def _save(path, data):
	"""Writes data to file."""
	file = open(path, "wb")
	writer = csv.writer(file, delimiter=",")

	#header line
	writer.writerow(data[0])

	#other lines
	for i in range(1, len(data)):
		newLine = []
		newLine.append(data[i][0].strftime("%Y-%m-%d"))
		for j in range(1, len(data[i])):
			newLine.append(data[i][j])
		writer.writerow(newLine)
	file.close()



def _read(path):
	"""Reads data into list."""
	file = open(path)
	reader = csv.reader(file, delimiter=",")

	#header line
	lines = []
	for line in reader:
		lines.append(line)
	data = []
	data.append(lines[0])

	#other lines
	for i in range(1, len(lines)):
		newLine = []
		dt = datetime.datetime.strptime(lines[i][0], "%Y-%m-%d")
		newLine.append(dt)
		for j in range(1, len(lines[i])):
			newLine.append(float(lines[i][j]))
		data.append(newLine)
	file.close()

	return data