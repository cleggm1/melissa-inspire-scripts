import re
output = open('ads_skip_recids.txt', 'w')
output.write('recids = [')
recids = []
with open('clean_ads_to_do.txt', 'r') as input:
    for line in input.readlines():
        matchObj = re.search(r'mismatch (\d+) (\d+)?', line)
        if matchObj:
            recid = "'"+matchObj.group(1)+"'"
            recids.append(recid)
            recid = "'"+matchObj.group(2)+"'"
            recids.append(recid)
output.write(',\n'.join(sorted(set(recids))))
output.write(']')
output.close()
