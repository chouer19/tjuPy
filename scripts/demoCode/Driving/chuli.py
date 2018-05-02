
f = open("example.map")
w = open("map",'w')

line = f.readline()

line = f.readline()

while line:
   
    args = line.split('\t')
    if args[0] == 0 and args[1] == 0:
        continue
    args = args[4:]
    for arg in args:
        ar = arg.split(',')
        if len(ar) > 2:
            w.write(ar[1] +'\t' +  ar[0] +'\t' +  ar[2] + '\n')
    line = f.readline()
