import uasyncio
import time
import gc

class CHTTPParser:           
    def urldecode(urlbytearray):
        response = bytearray();
        i = 0
        while(len(urlbytearray) > i):    
            if(urlbytearray[i] == 37 and len(urlbytearray) > i+2):
                asciiBytes = bytearray()
                asciiBytes.append(urlbytearray[i+1])
                asciiBytes.append(urlbytearray[i+2])
                ascii = int(asciiBytes.decode('utf-8'), 16)
                response.append(ascii)
                i=i+2
                #urlbytearray = urlbytearray[3:]
                #del urlbytearray[0]
                #del urlbytearray[0]
                #del urlbytearray[0]
            elif(urlbytearray[i] == 43): #+ -> space
                response.append(32)
            else:
                response.append(urlbytearray[i])
                #urlbytearray = urlbytearray[1:]
                #del testi[0]
            i=i+1
            if(i > 100):
                urlbytearray = urlbytearray[i:]
                i=0
        return response.decode('utf-8')
