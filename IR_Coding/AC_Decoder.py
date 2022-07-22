
SHORT= 550
LONG =1650
MARGIN=100

SEPARATOR1=4400
SEPARATOR2=5300

DECODE=''

def Decoder(val1,val2):
    if (abs(val1-SHORT)<MARGIN) and (abs(val2-SHORT)<MARGIN):
        print('0')
        return '0'
    elif (abs(val1-SHORT)<MARGIN) and (abs(val2-LONG)<MARGIN):
        print('1')
        return '1'
    elif (abs(val1-SEPARATOR1)<MARGIN) and (abs(val2-SEPARATOR1)<MARGIN):
        print('[')
        return '['
    elif (abs(val1-SHORT)<MARGIN) and (abs(val2-SEPARATOR2)<MARGIN):
        print(']')
        return ']'



f=open('19_F4',"r")


print(f.readline())
print(f.readline())

lines=f.readlines()
result=[]
for x in lines:
    try: 
        x=x[:-1]
        T=x.split(' ')
        sT = list(filter(None, T))   
        #print (sT)
        #print(x)
        result.append(sT)
    except:
        print('ddd')
f.close()
#print(result)
result.pop()
# result.pop()
# result.pop()
# result.pop()

for J in result:
    print(J)
    if (len(J)==6):
        DECODE+= Decoder(int(J[0]),int(J[1]))
        DECODE+= Decoder(int(J[2]),int(J[3]))
        DECODE+= Decoder(int(J[4]),int(J[5]))
    if (len(J)==4):
        DECODE+= Decoder(int(J[0]),int(J[1]))
        DECODE+= Decoder(int(J[2]),int(J[3]))
    if (len(J)==2):
        DECODE+= Decoder(int(J[0]),int(J[1]))

print(" ")
print(" ")
print(" ")
print(DECODE)





