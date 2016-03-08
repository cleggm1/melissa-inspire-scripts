import re

filename_in = 'tmp_refs.in'
filename_out = '/afs/fnal.gov/files/home/room3/cleggm1/tmp_refs.out.txt'
mylist = []
new_num = raw_input('new reference number:')
new_num2 = '$$9CURATOR$$o'+new_num+'$$'
new_num3 = '999C5 $$9CURATOR$$o'+new_num+'$$'
ouput = open(filename_out, 'w')
for i in open(filename_in, 'r').readlines():
    matchObj = re.search(r'(\$\$o.*?\$\$)', i)
    if matchObj:
        wrong = matchObj.group()
        x = re.sub(r'\$\$o.*?\$\$', new_num2, i)
        mylist.append(x)
    else:
        matchObj1 = re.search(r'999C5 \$\$o\w{2,5}-\w{2,3}$', i)
        if matchObj1:
            pass
        else:
            x = re.sub(r'999C5 \$\$', new_num3, i) 
            mylist.append(x)
mystring = ''.join(mylist)
ouput.write(mystring)
print mystring
ouput.close()
