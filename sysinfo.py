#!/usr/bin/env python3
#coding:utf-8
#Copyright (C) Mr.D

import paramiko
import re
import time

def get_mem(client):
	"""
	parameter:
		object 
	return: 
		string
	"""

	stdin,stdout,stderr = client.exec_command('free -m')
	out_s = stdout.read().decode()
	err_s = stderr.read().decode()
	if err_s:
		return
	s = re.search('Mem.*\n',out_s).group().strip('\n').split()
	return "[memory]  usage: " + str(round(float(s[2])/float(s[1])*100,2)) + "% total: "+ s[1] + "M used: " + s[2] + "M free: " + s[3] + "M buffer/cache: " + s[5] + "M"

def get_cpu(client):
	"""
	parameter:
		object 
	return: 
		string
	"""

	stdin,stdout,stderr = client.exec_command('cat /proc/stat')
	out_s = stdout.read().decode()
	err_s = stderr.read().decode()
	if err_s:
		return	
	s1 = re.search('cpu .*\n',out_s).group().strip('\n')
	time.sleep(1)
	stdin,stdout,stderr = client.exec_command('cat /proc/stat')	
	out_s = stdout.read().decode()
	err_s = stderr.read().decode()
	if err_s:
		return	
	s2 = re.search('cpu .*\n',out_s).group().strip('\n')
	cpu_time_1_l = re.findall('\d+',s1)
	cpu_time_2_l = re.findall('\d+',s2)
	cpu_time_total_1_i = 0
	cpu_time_total_2_i = 0	
	for i in cpu_time_1_l:
		cpu_time_total_1_i = cpu_time_total_1_i + int(i)
	for i in cpu_time_2_l:
		cpu_time_total_2_i = cpu_time_total_2_i + int(i)
	cpu_time_user_i = int(cpu_time_2_l[0]) - int(cpu_time_1_l[0])
	cpu_time_sys_i = int(cpu_time_2_l[2]) - int(cpu_time_1_l[2])
	cpu_time_idle_i = int(cpu_time_2_l[3]) - int(cpu_time_1_l[3])
	cpu_time_iowait_i = int(cpu_time_2_l[4]) - int(cpu_time_1_l[4])
	cpu_time_total_i = cpu_time_total_2_i - cpu_time_total_1_i
	cpu_usage_f = round((1-float(cpu_time_idle_i)/float(cpu_time_total_i))*100,2)
	cpu_user_f = round(float(cpu_time_user_i)/float(cpu_time_total_i)*100,2)
	cpu_sys_f = round(float(cpu_time_sys_i)/float(cpu_time_total_i)*100,2)
	cpu_idle_f = round(float(cpu_time_idle_i)/float(cpu_time_total_i)*100,2)
	cpu_iowait_f = round(float(cpu_time_iowait_i)/float(cpu_time_total_i)*100,2)
	return "[cpu]  usage: " + str(cpu_usage_f) + "% user: " + str(cpu_user_f) + "% sys: " + str(cpu_sys_f) + "% idle: " + str(cpu_idle_f) + "% iowait: " + str(cpu_iowait_f) + "%" 

def get_disk(client):
	"""
	parameter:
		object 
	return: 
		string
	"""

	stdin,stdout,stderr = client.exec_command('df -hT && df -ihT')
	out_s = stdout.read().decode()
	err_s = stderr.read().decode()
	if err_s:
		return
	return (out_s)

def get_net(client):
	"""
	parameter:
		object
	return:
		string
	"""
	stdin,stdout,stderr = client.exec_command('cat /proc/net/dev')
	out_s = stdout.read().decode()
	err_s = stderr.read().decode()
	if err_s:
		return
	if_all_1_l = re.findall('.*\d+.*\n',out_s)
	time.sleep(1)
	stdin,stdout,stderr = client.exec_command('cat /proc/net/dev')
	out_s = stdout.read().decode()
	err_s = stderr.read().decode()
	if err_s:
		return
	if_all_2_l = re.findall('.*\d+.*\n',out_s)
	l1 = []
	l2 = []
	return_s = ""
	for s in if_all_1_l:
		tmp_1_l = s.strip('\n').split(':')
		l = []
		l.append(tmp_1_l[0])
		tmp_2_l = tmp_1_l[1].split()
		l = l + tmp_2_l
		l1.append(l[0] + ' ' + l[1] + ' ' + l[9])
	for s in if_all_2_l:
		tmp_1_l = s.strip('\n').split(':')
		l = []
		l.append(tmp_1_l[0])
		tmp_2_l = tmp_1_l[1].split()
		l = l + tmp_2_l
		l2.append(l[0] + ' ' + l[1] + ' ' + l[9])
	for i in range(len(l1)):
		tmp_l1 = l1[i].split()
		tmp_l2 = l2[i].split()
		recieve_i = int(tmp_l2[1]) - int(tmp_l1[1])
		send_i = int(tmp_l2[2]) - int(tmp_l1[2])
		return_s = return_s + tmp_l1[0] + " recv: " + b2human(recieve_i * 8) + "bps " + " send: " + b2human(send_i * 8) + "bps\n"
	return (return_s)

def b2human(n):
	units = ('K','M','G','T','P','E','Z','Y')
	unit_d = {}
	for i,s in enumerate(units):
		unit_d[s] = 1 << (i + 1) * 10
	for s in reversed(units):
		if n >= unit_d[s]:
			return str(round(float(n)/float(unit_d[s]),2)) + s
	return str(n)

def get_conn(hostName,userName):
	"""
	parameter:
		string 
		string
	return: 
		object	
	"""

	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(hostname=hostName,username=userName,timeout=120,banner_timeout=120,auth_timeout=120)
	return (client)

if __name__ == '__main__':
	print ("\n--------------------web1--------------------\n")
	client = get_conn('web1','root')
	s = get_mem(client)
	print (s,"\n")
	s = get_cpu(client)
	print (s,"\n")
	s = get_disk(client)
	print (s)
	s = get_net(client)
	print (s) 
	print ("--------------------------------------------\n")
	client.close()