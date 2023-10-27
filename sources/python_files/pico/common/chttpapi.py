import uasyncio
import time
import machine
from pico.common.chttpparser import CHTTPParser
from pico.common.cfile import CFile
from pico.common.ciniparser import CIniParser

class CHTTPAPI:
    def __init__(self, loop, rootFolder, defaultPage, devices, device):
        self.loop = loop
        self.rootFolder = rootFolder
        self.defaultPage = defaultPage
        self.devices = devices
        self.device = device
        self.ssid = ""
        self.ssidpw = ""
        self.uuid = ""

        if(device != None):
            self.ssid = device.ssid
            self.ssidpw = device.ssidpw
            self.uuid = device.uuid
        else:
            connectionArgs = CIniParser.GetIni(self.rootFolder + "/connection.ini")
            if(len(connectionArgs) == 2):
                if("ssid" in connectionArgs):
                    self.ssid = connectionArgs["ssid"]
                if("ssidpw" in connectionArgs):
                    self.ssidpw = connectionArgs["ssidpw"]
                    
            deviceArgs = CIniParser.GetIni(self.rootFolder + "/device.ini")
            if(len(deviceArgs) == 2):
                if("uuid" in deviceArgs):
                    self.uuid = deviceArgs["uuid"]
            
            
        print('starting http connection api server on port 80...')
        try:
            self.loop.create_task(uasyncio.start_server(self.newHttpRequest, "0.0.0.0", 80))                    
        except Exception as e:
            print(e)

    async def newHttpRequest(self, reader, writer):
        print('http device api connection')
        
        request=""
        method=""
        path=""
        headers = {}

        requestline = await reader.readline()
        options = str(requestline.decode('utf-8')).split(' ')
        if(len(options)==3):
            method=options[0].strip()
            path=options[1].strip()
            
        requestline = await reader.readline()
        while(len(requestline)>2):
            headerparts = str(CHTTPParser.urldecode(requestline)).split(':')
            if(len(headerparts) == 2):
                headers[headerparts[0].strip()] = headerparts[1].strip()
            requestline = await reader.readline()
        print("method: %s path:%s" % (method, path))
        if(method == "GET"):
            arguments={}
            pathParts=path.split('?')
            if(len(pathParts) == 2):
                path = pathParts[0]
                argumentParts=pathParts[1].replace('+',' ').split('&')
                for argumentPart in argumentParts:
                    equalMark=argumentPart.find("=")
                    if(equalMark>=0):
                        name=argumentPart[0:equalMark]
                        value=argumentPart[equalMark+1:len(argumentPart)]
                        print("argument name:%s value:%s" % (name, value))
                        arguments[name] = value
                        
            if(path=="/" or path=="/connection" or path=="/config" or path=="/device"):
                html = "Not Found"
                if((path=="/" and self.defaultPage == "process") or path=="/process"):
                    html = self.GetProcessHtmlPage()
                elif((path=="/" and self.defaultPage == "connection") or path=="/connection"):
                    html = self.GetConnectionHtmlPage()
                elif((path=="/" and self.defaultPage == "config") or path=="/config"):
                    html = self.GetConfigHtmlPage()
                elif((path=="/" and self.defaultPage == "device") or path=="/device"):
                    html = self.GetDeviceHtmlPage()              
            
                writer.write('HTTP/1.0 200 OK\r\n')
                writer.write('Content-Type: text/html\r\n')
                writer.write('Content-Length: %d\r\n' % len(html))
                writer.write('Access-Control-Allow-Origin: *\r\n')
                writer.write('\r\n')
                
                writer.write(html)
                await writer.drain()
                
            elif(path=="/favicon.ico"):
                writer.write('HTTP/1.1 204 No Content\r\n')          
                writer.write('Access-Control-Allow-Origin: *\r\n')
                writer.write('Access-Control-Allow-Methods: *\r\n')
                writer.write('Access-Control-Allow-Headers: *\r\n')           
                writer.write('Content-Length: 0\r\n')            
                writer.write('\r\n')
                await writer.drain()
                await writer.wait_closed()
                
        elif(method == "POST"):
            print("post")
            contentLength=int(headers["Content-Length"])
            contentbytes=b'';
            while(len(contentbytes)<contentLength):
                contentbytes = contentbytes + await reader.read(contentLength)
            if(len(contentbytes)>0):
                content=CHTTPParser.urldecode(bytearray(contentbytes))
                
                arguments={}
                argumentParts=content.split('&')
                for argumentPart in argumentParts:
                    equalMark=argumentPart.find("=")
                    if(equalMark>=0):
                        name=argumentPart[0:equalMark]
                        value=argumentPart[equalMark+1:len(argumentPart)]
                        print("argument name:%s value:%s" % (name, value))
                        arguments[name] = value
                        
                        
                if(path=="/connection"):               
                    self.ConnectionPost(arguments)
                elif(path=="/config"):                   
                    if(len(content)>0):
                        if(content.find("configxml=") >=0):
                            self.ConfigPost(content)
                elif(path=="/device"):  
                    self.DevicePost(arguments)
                        
                writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                writer.write('<!DOCTYPE html>')
                writer.write('<html>')
                writer.write('<body onload="config()">')
                writer.write('<script>')
                writer.write('function config() {')
                #writer.write('window.open("/config");')
                writer.write('window.location = "/";')
                writer.write('}')
                writer.write('</script>')
                writer.write('</body>')
                writer.write('</html>')
                #writer.write(contentbytes)
                await writer.drain()
                await writer.wait_closed()
                #machine.reset()
            else:
                    writer.write('HTTP/1.0 404 OK\r\nContent-type: text/html\r\n\r\n')
                    writer.write('content-length=0')
                    await writer.drain()
                    await writer.wait_closed()                       
                 
        elif(method=="OPTIONS"):
            print('thttpapi options')
            writer.write('HTTP/1.1 204 No Content\r\n')
            #writer.write('Content-Type: image/x-icon\r\n')            
            writer.write('Access-Control-Allow-Origin: *\r\n')
            writer.write('Access-Control-Allow-Methods: GET,HEAD,PUT,PATCH,POST,DELETE\r\n')
            writer.write('Access-Control-Allow-Headers: X-PINGOTHER, Content-Type\r\n')
            writer.write('Vary: Access-Control-Request-Headers\r\n')            
            writer.write('Content-Length: 0\r\n')
            writer.write('Date: Fri, 28 Apr 2023 06:42:49 GMT\r\n')
            #writer.write('Connection: Keep-Alive\r\n') 
            
            writer.write('\r\n')
            await writer.drain()
            await writer.wait_closed()
        else:
            print("Unknown request:")
            #writer.write('HTTP/1.0 404 OK\r\nContent-type: text/html\r\n\r\n')
            writer.write('HTTP/1.0 404 OK\r\n')
            writer.write('Content-Type: text/html\r\n')
            #writer.write('Content-Length: %d\r\n' % len(response))
            writer.write('Access-Control-Allow-Origin: *\r\n')
            writer.write('\r\n')
            writer.write('Not found')
            await writer.drain()
            await writer.wait_closed()
            
    def ConnectionPost(self, arguments):
        iniMap = {}
        if("ssid" in arguments):
            self.ssid = arguments["ssid"]
            iniMap["ssid"] = self.ssid
            
        if("ssidpw" in arguments):
            self.ssidpw = arguments["ssidpw"]
            iniMap["ssidpw"] = self.ssidpw
            
        CIniParser.SetIni(self.rootFolder + "/connection.ini", iniMap)
    
    def ConfigPost(self, configxml):
        CFile.SetFileContent(self.rootFolder + "/config.xml", configxml.replace("configxml=",''))
        
    def DevicePost(self, arguments):
        iniMap = {}
        if("uuid" in arguments):
            self.uuid = arguments["uuid"]
            iniMap["uuid"] = self.uuid
        
            
        CIniParser.SetIni(self.rootFolder + "/device.ini", iniMap)
    
    def GetProcessHtmlPage(self):
        html = CFile.GetFileContent(self.rootFolder + "/pico/common/html/process.html")
        
        contentTagValues = "No ContentTags"
        if(self.device != None):
            contentTagValues = ""
            for contentTag in self.device.contentTags.values():
                if(contentTag.value != None):
                     contentTagValues = contentTagValues + "%s: %s<br>" % (contentTag.Name, str(contentTag.value))
        
        html = html.replace("{processcontent}", contentTagValues)
        return html
        
            
    def GetConnectionHtmlPage(self):
        
        html = CFile.GetFileContent(self.rootFolder + "/pico/common/html/connection.html") 
    
        formContent = '    <label for="ssid">SSID:</label><br>'
        formContent = formContent + '    <input type="text" id="ssid" name="ssid" value="' + self.ssid + '"><br><br>'
        formContent = formContent + '    <label for="ssidpw">Password:</label><br>'
        formContent = formContent + '    <input type="text" id="ssidpw" name="ssidpw" value="' + self.ssidpw + '"><br><br>'
        formContent = formContent + ''
        
        html = html.replace("{formcontent}", formContent)
                           
        return html
    
    def GetConfigHtmlPage(self):
        
        html = CFile.GetFileContent(self.rootFolder + "/pico/common/html/config.html")
        
        
        configxml = CFile.GetFileContent(self.rootFolder + "/config.xml")
        
        formContent = '    <label for="configxml">config.xml:</label><br>'
        formContent = formContent + '    <textarea id="configxml" name="configxml">' + configxml + '</textarea><br><br>'
        html = html.replace("{formcontent}", formContent)
                           
        return html
    
    def GetDeviceHtmlPage(self):
        html = CFile.GetFileContent(self.rootFolder + "/pico/common/html/device.html")
        
        formContent = '    <label for="uuid">Device Hierarchy UUID:</label><br>' 
        formContent = formContent + '    <select id="uuid" name="uuid">'
        for device in self.devices:
            selected = ""
            if(device.uuid == self.uuid):
                selected = ' selected'
            formContent = formContent + '        <option value="' + device.uuid + '"' + selected + '>' + device.name + '</option>'
        formContent = formContent + '    </select><br><br>' 
        
        html = html.replace("{formcontent}", formContent)
                           
        return html
    

        
        
        
    
    
    
    
    
    
            





# import uasyncio
# import time
# import machine
# from pico.common.chttpparser import CHTTPParser
# 
# class CHTTPAPI:
#     def __init__(self, loop):
#         self.loop = loop
#         #self.contentarray=reservedarray
#         self.uuid=""
#         self.ssid=""
#         self.ssidpw=""
#         
#         print('starting http api server on port 80...')
#         try:
#             self.loop.create_task(uasyncio.start_server(self.newHttpRequest, "0.0.0.0", 80))                    
#         except Exception as e:
#             print(e)
#             
#     def setdevicevalues(self, uuid, ssid, pw, imot):
#         self.uuid=uuid
#         self.ssid=ssid
#         self.pw=pw
#         self.imot=imot
# 
#     async def newHttpRequest(self, reader, writer):
#         print('http api connection')
#         
#         request=""
#         method=""
#         path=""
#         headers = {}
#         #print(self.imotxml)
# 
#         requestline = await reader.readline()
#         options = str(requestline.decode('utf-8')).split(' ')
#         if(len(options)==3):
#             method=options[0].strip()
#             path=options[1].strip()
#             
#         requestline = await reader.readline()
#         while(len(requestline)>2):
#             headerparts = str(CHTTPParser.urlparse(requestline)).split(':')
#             if(len(headerparts) == 2):
#                 headers[headerparts[0].strip()] = headerparts[1].strip()
#             requestline = await reader.readline()
#         print("method: %s path:%s" % (method, path))
#         if(method == "GET"):
#             arguments={}
#             pathParts=path.split('?')
#             if(len(pathParts) == 2):
#                 path = pathParts[0]
#                 argumentParts=pathParts[1].replace('+',' ').split('&')
#                 for argumentPart in argumentParts:
#                     equalMark=argumentPart.find("=")
#                     if(equalMark>=0):
#                         name=argumentPart[0:equalMark]
#                         value=argumentPart[equalMark+1:len(argumentPart)]
#                         print("argument name:%s value:%s" % (name, value))
#                         arguments[name] = value          
#             if(path=="/"):
#                 html=self.devicePage(arguments)
#                 writer.write('HTTP/1.0 200 OK\r\n')
#                 writer.write('Content-Type: text/html\r\n')
#                 writer.write('Content-Length: %d\r\n' % len(html))
#                 writer.write('Access-Control-Allow-Origin: *\r\n')
#                 writer.write('\r\n')
#                 
#                 writer.write(html)
#                 await writer.drain()
#                 
#             elif(path=="/favicon.ico"):
#                 writer.write('HTTP/1.1 204 No Content\r\n')          
#                 writer.write('Access-Control-Allow-Origin: *\r\n')
#                 writer.write('Access-Control-Allow-Methods: *\r\n')
#                 writer.write('Access-Control-Allow-Headers: *\r\n')           
#                 writer.write('Content-Length: 0\r\n')            
#                 writer.write('\r\n')
#                 await writer.drain()
#                 await writer.wait_closed()
#                 
#         elif(method == "POST"):
#             print("post")
#             if(path=="/device"):
#                 contentLength=int(headers["Content-Length"])
#                 contentbytes=b'';
#                 while(len(contentbytes)<contentLength):
#                     contentbytes = contentbytes + await reader.read(contentLength)
#                 #print(contentbytes)
#                 if(len(contentbytes)>0):
#                     contentarguments=str(contentbytes.decode('utf-8')).replace('+',' ').split('&')
#                     for contentargument in contentarguments:
#                         print(contentargument)
#                         if(contentargument.find("uuid=")>=0):
#                             self.uuid = CHTTPParser.urlparse(contentargument.replace("uuid=",'')).strip()
#                         elif(contentargument.find("ssid=")>=0):
#                             self.ssid = CHTTPParser.urlparse(contentargument.replace("ssid=",'')).strip()
#                         elif(contentargument.find("pw=")>=0):
#                             self.pw = CHTTPParser.urlparse(contentargument.replace("pw=",'')).strip()
#                         elif(contentargument.find("imot=")>=0):
#                             self.imot = CHTTPParser.urlparse(contentargument.replace("imot=",'')).strip()
#                     
# #                     idFile = open("id.ini", 'w')
# #                     idFile.write("HierarchyUUID=" + self.uuid + "\n")
# #                     idFile.write("SSID=" + self.ssid + "\n")
# #                     idFile.write("PW=" + self.pw + "\n")
# #                     idFile.write("IMOT=" + self.imot + "\n")
# #                     idFile.close()
#                     
#                     writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
#                     writer.write('<!DOCTYPE html>')
#                     writer.write('<html>')
#                     writer.write('<body onload="config()">')
#                     writer.write('<script>')
#                     writer.write('function config() {')
#                     #writer.write('window.open("/config");')
#                     writer.write('window.location = "/device";')
#                     writer.write('}')
#                     writer.write('</script>')
#                     writer.write('</body>')
#                     writer.write('</html>')
#                     #writer.write(contentbytes)
#                     await writer.drain()
#                     await writer.wait_closed()
#                     #machine.reset()
#                     
#                 else:
#                     writer.write('HTTP/1.0 404 OK\r\nContent-type: text/html\r\n\r\n')
#                     writer.write('content-length=0')
#                     await writer.drain()
#                     await writer.wait_closed()
#             
#         elif(method=="OPTIONS"):
#             print('thttpapi options')
#             writer.write('HTTP/1.1 204 No Content\r\n')
#             #writer.write('Content-Type: image/x-icon\r\n')            
#             writer.write('Access-Control-Allow-Origin: *\r\n')
#             writer.write('Access-Control-Allow-Methods: GET,HEAD,PUT,PATCH,POST,DELETE\r\n')
#             writer.write('Access-Control-Allow-Headers: X-PINGOTHER, Content-Type\r\n')
#             writer.write('Vary: Access-Control-Request-Headers\r\n')            
#             writer.write('Content-Length: 0\r\n')
#             writer.write('Date: Fri, 28 Apr 2023 06:42:49 GMT\r\n')
#             #writer.write('Connection: Keep-Alive\r\n') 
#             
#             writer.write('\r\n')
#             await writer.drain()
#             await writer.wait_closed()
#         else:
#             print("Unknown request:")
#             #writer.write('HTTP/1.0 404 OK\r\nContent-type: text/html\r\n\r\n')
#             writer.write('HTTP/1.0 404 OK\r\n')
#             writer.write('Content-Type: text/html\r\n')
#             #writer.write('Content-Length: %d\r\n' % len(response))
#             writer.write('Access-Control-Allow-Origin: *\r\n')
#             writer.write('\r\n')
#             writer.write('Not found')
#             await writer.drain()
#             await writer.wait_closed()
#             
#     def devicePage(self, arguments):
#         uuid = self.uuid
#         ssid = self.ssid
#         ssidpw = self.ssidpw
#         if("uuid" in arguments):
#             uuid = arguments["uuid"]
#         if("ssid" in arguments):
#             ssid = arguments["ssid"]
#         if("ssidpw" in arguments):
#             ssidpw = arguments["ssidpw"]
#             
#             
#         html='<!DOCTYPE html>'
#         html=html+'<html>'
#         html=html+'<body>'
#         html=html+'<style>label {font-size:2.5em;} input {font-size:2.5em;}</style>'
#         html=html+'<form action="/device" method="post">'
#         html=html+'    <label for="uuid">Device Hierarchy UUID:</label><br>'
#         html=html+'    <input type="text" id="uuid" name="uuid" size="50" value="'+ uuid +'"><br><br>'
#         html=html+'    <label for="ssid">SSID:</label><br>'
#         html=html+'    <input type="text" id="ssid" name="ssid" size="50"value="'+ ssid +'"><br><br>'
#         html=html+'    <label for="ssidpw">SSID Password:</label><br>'
#         html=html+'    <input type="text" id="ssidpw" name="ssidpw" value="' + ssidpw + '" size="50"><br><br><br>'
#         html=html+'    <input type="submit" value="Set Device Info">'
#         html=html+'</form>'
#         html=html+'</body>'
#         html=html+'</html>' 
#         
#         return html
#             
#         
# #         if(method=="GET" and path=="/"):            
# # #            offset=0
# # #            writer.write(self.devicehtml)
# # #             page = open("values.html", 'r')
# # #             while True:
# # #                 contentline = page.readline()
# # #                 if contentline:                
# # #                     for i in range(len(contentline)):
# # #                         self.contentarray[offset + i] = ord(contentline[i].encode())
# # #                     offset=offset+len(contentline)
# # #                 else:
# # #                     break
# # #             contentsize=offset;
# #             
# #             writer.write('HTTP/1.0 200 OK\r\n')
# #             writer.write('Content-Type: text/html\r\n')
# #             writer.write('Content-Length: %d\r\n' % len(self.devicehtml))
# #             writer.write('Access-Control-Allow-Origin: *\r\n')
# #             writer.write('\r\n')
# #             
# #             writer.write(self.devicehtml)
# #             await writer.drain()
# #             
# # #             i=0
# # #             while(i < contentsize):
# # #                 end = i+1024
# # #                 if(end > contentsize):
# # #                     end=contentsize
# # #                 writer.write(self.contentarray[i:end])
# # #                 await writer.drain()
# # #                 i=end;
# #             await writer.wait_closed()
# #         elif(method=="GET" and path=="/device"):
# #             response = self.web_page()
# #             response = response.replace("uuidvalue", self.uuid)
# #             response = response.replace("ssidvalue", self.ssid)
# #             response = response.replace("pwvalue", self.pw)
# #             response = response.replace("imotvalue", self.imot)
# # 
# #             writer.write('HTTP/1.1 200 OK\r\n')
# #             writer.write('Content-Type: text/html\r\n')            
# #             writer.write('Access-Control-Allow-Origin: http://192.168.1.197:40001/config\r\n')            
# #             writer.write('Access-Control-Allow-Headers: Content-Type,Authorization\r\n')
# #             writer.write('Access-Control-Allow-Methods: GET,PUT,POST,OPTIONS\r\n')
# #             writer.write('Content-Length: %d\r\n' % len(response))
# #             
# #             
# #             writer.write('\r\n')
# #             writer.write(response)
# # 
# #             await writer.drain()
# #             await writer.wait_closed()
# #         elif(method=="POST" and path=="/device"):
# #             contentLength=int(headers["Content-Length"])
# #             contentbytes=b'';
# #             while(len(contentbytes)<contentLength):
# #                 contentbytes = contentbytes + await reader.read(contentLength)
# #             #print(contentbytes)
# #             if(len(contentbytes)>0):
# #                 contentarguments=str(contentbytes.decode('utf-8')).replace('+',' ').split('&')
# #                 for contentargument in contentarguments:
# #                     print(contentargument)
# #                     if(contentargument.find("uuid=")>=0):
# #                         self.uuid = CHTTPParser.urlparse(contentargument.replace("uuid=",'')).strip()
# #                     elif(contentargument.find("ssid=")>=0):
# #                         self.ssid = CHTTPParser.urlparse(contentargument.replace("ssid=",'')).strip()
# #                     elif(contentargument.find("pw=")>=0):
# #                         self.pw = CHTTPParser.urlparse(contentargument.replace("pw=",'')).strip()
# #                     elif(contentargument.find("imot=")>=0):
# #                         self.imot = CHTTPParser.urlparse(contentargument.replace("imot=",'')).strip()
# #                 
# #                 idFile = open("id.ini", 'w')
# #                 idFile.write("HierarchyUUID=" + self.uuid + "\n")
# #                 idFile.write("SSID=" + self.ssid + "\n")
# #                 idFile.write("PW=" + self.pw + "\n")
# #                 idFile.write("IMOT=" + self.imot + "\n")
# #                 idFile.close()
# #                 
# #                 writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
# #                 writer.write('<!DOCTYPE html>')
# #                 writer.write('<html>')
# #                 writer.write('<body onload="config()">')
# #                 writer.write('<script>')
# #                 writer.write('function config() {')
# #                 #writer.write('window.open("/config");')
# #                 writer.write('window.location = "/device";')
# #                 writer.write('}')
# #                 writer.write('</script>')
# #                 writer.write('</body>')
# #                 writer.write('</html>')
# #                 #writer.write(contentbytes)
# #                 await writer.drain()
# #                 await writer.wait_closed()
# #                 machine.reset()
# #                 
# #             else:
# #                 writer.write('HTTP/1.0 404 OK\r\nContent-type: text/html\r\n\r\n')
# #                 writer.write('content-length=0')
# #                 await writer.drain()
# #                 await writer.wait_closed()
# #         elif(method=="GET" and path=="/favicon.ico"):
# #             writer.write('HTTP/1.1 204 No Content\r\n')          
# #             writer.write('Access-Control-Allow-Origin: *\r\n')
# #             writer.write('Access-Control-Allow-Methods: *\r\n')
# #             writer.write('Access-Control-Allow-Headers: *\r\n')           
# #             writer.write('Content-Length: 0\r\n')            
# #             writer.write('\r\n')
# #             await writer.drain()
# #             await writer.wait_closed()
# #             
# #         elif(method=="OPTIONS"):
# #             print('thttpapi options')
# #             writer.write('HTTP/1.1 204 No Content\r\n')
# #             #writer.write('Content-Type: image/x-icon\r\n')            
# #             writer.write('Access-Control-Allow-Origin: *\r\n')
# #             writer.write('Access-Control-Allow-Methods: GET,HEAD,PUT,PATCH,POST,DELETE\r\n')
# #             writer.write('Access-Control-Allow-Headers: X-PINGOTHER, Content-Type\r\n')
# #             writer.write('Vary: Access-Control-Request-Headers\r\n')            
# #             writer.write('Content-Length: 0\r\n')
# #             writer.write('Date: Fri, 28 Apr 2023 06:42:49 GMT\r\n')
# #             #writer.write('Connection: Keep-Alive\r\n') 
# #             
# #             writer.write('\r\n')
# #             await writer.drain()
# #             await writer.wait_closed()
# #             
# #         else:
# #             print("Unknown request:")
# #             #writer.write('HTTP/1.0 404 OK\r\nContent-type: text/html\r\n\r\n')
# #             writer.write('HTTP/1.0 404 OK\r\n')
# #             writer.write('Content-Type: text/html\r\n')
# #             #writer.write('Content-Length: %d\r\n' % len(response))
# #             writer.write('Access-Control-Allow-Origin: *\r\n')
# #             writer.write('\r\n')
# #             writer.write('Not found')
# #             await writer.drain()
# #             await writer.wait_closed()                 
#             
#     def web_page(self):
#         indexPage = open("index.html", 'r')
#         indexHtml = indexPage.read()
#         indexPage.close()
#         return indexHtml
# 