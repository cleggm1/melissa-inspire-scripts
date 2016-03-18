import re

input_to_do = open('ads_to_do.in', 'r').readlines()
input_done = open('ads_done.in', 'r').readlines()
output = open('/afs/fnal.gov/files/home/room3/cleggm1/clean_ads_to_do.txt', 'w')
input_to_do = [re.sub(r'\d+\)\s+', '', i) for i in input_to_do]
input_done = [re.sub(r'\d+\)\s+', '', i) for i in input_done]
output.write(''.join(list(set(input_to_do) - set(input_done))))
output.close()
