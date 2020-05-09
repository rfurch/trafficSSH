#!/usr/bin/python3.6

# libraries we will need

import argparse
import getopt
import sys
import time
import json
import socket
import struct
import mysql.connector
import multiprocessing

from ping3 import ping, verbose_ping

# global variable for verbosity level
_verbose=0

# default DB Data
DB_USER="nocuser"
DB_PASS="AguasaguaS"
DB_DATABASE="topology"

VENDOR_ID_UBNT = 3

UBNT_NBM5 =	1
UBNT_NSM5 = 2
UBNT_RKM5 =	3
UBNT_UAPINDOOR = 4
UBNT_UAPOUTDOOR	= 5
UBNT_TOUGHSWITCH = 6
UBNT_AF25 = 10
UBNT_AF5 = 11
UBNT_MCA = 12
UBNT_R5AC = 13
UBNT_EDGESWITCH = 14

#--------------------------------------------------------------------------------

class trafficData:

	ip = ''	
	devID = 0
	deviceName = ''
	trafficName = ''
	deviceVendor = -1 
	deviceModel = -1

	def __init__(self, ip, dev_id, nombre, descr, vendor, model):
		self.ip = ip
		self.dev_id = dev_id
		self.deviceName = nombre
		self.trafficName = descr
		self.vendor = vendor
		self.model = model

#--------------------------------------------------------------------------------

def worker(procnum, return_dict):
	'''worker function'''
	print (str(procnum) + ' represent!')
	return_dict[procnum] = procnum

#--------------------------------------------------------------------------------

def workersPing(list):
	manager = multiprocessing.Manager()
	return_dict = manager.dict()
	jobs = []
	
	for i in range(5):
		p = multiprocessing.Process(target=worker, args=(i,return_dict))
		jobs.append(p)
		p.start()

	for proc in jobs:
		proc.join()
	print (return_dict.values())

#--------------------------------------------------------------------------------

def readDB():

	results = []	

	try:
		cnx = mysql.connector.connect(host="192.168.208.13", user=DB_USER, password=DB_PASS, database=DB_DATABASE, connect_timeout=10, charset='utf8', use_unicode=True)

		cursor = cnx.cursor()

		query = """SELECT a.id, a.nombre, a.ip,
		b.description, a.vendor_id, a.model_id 
		FROM devices a LEFT JOIN devices_bw b ON a.id=b.dev_id WHERE 
		a.enable>0 AND b.enable>0 AND a.snmp<=0 AND a.cli_acc=2 AND a.vendor_id=3;
		"""

		# En este caso no necesitamos limpiar ningún dato
		cursor.execute(query)

		for (id, nombre, ip , descr, vendor, model) in cursor:
			print(id, nombre, descr, ip, vendor, model)
			#results.append( (id, nombre, ip , descr, vendor, model) )
			
			d = trafficData(ip, id, nombre, descr, vendor, model)
			results.append(d)			 

	
	except mysql.connector.Error as err:
		print("Mysql DB COnnection ERROR: ", err)

	finally:
		cnx.close()
	
	return results

#--------------------------------------------------------------------------------

def main():
	global _verbose


	print(ping ('10.10.10.10'))
	print(ping ('192.168.205.10'))

	try:
		opts, args = getopt.getopt(sys.argv[1:], "i:c:vh", ["help", "verbose"])
	except getopt.GetoptError as err:
		# print help information and exit:
		print (str(err))  # will print something like "option -a not recognized"
		usage()
		sys.exit(2)

	for o, a in opts:
		if o in ("-v", "--verbose"):
			_verbose+=1
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
#		elif o in ("-i"):
#			IPAddress = a
		else:
			assert False, "unhandled option"
		
	# read fromDB
	deviceList = readDB()

	# ping to each device
	workersPing(deviceList)

	sys.exit()

#--------------------------------------------------------------------------------

def usage():
	print ("\n\n")
	print ("Read REDIS HASH for traffic bandwidth and send data to GRAPHITE")
	print ("-v [Optional verbosity level.  the more 'v' the more verbose!]")
	print ("-h [Print this message]")
	print ("\n\n")

#--------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
    
#--------------------------------------------------------------------------------
