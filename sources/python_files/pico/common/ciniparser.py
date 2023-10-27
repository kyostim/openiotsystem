from pico.common.cfile import CFile
class CIniParser: 
    def SetIni(filename, arguments):
        connectionini = ""
        for argumentName in arguments:
            connectionini = connectionini + argumentName + "=" + arguments[argumentName] + "\n"
            
        CFile.SetFileContent(filename, connectionini)
        
    def GetIni(filename):
        inifile = CFile.GetFileContent(filename)
        arguments = {}
        argumentLines = inifile.split("\n") 
        for argumentLine in argumentLines:
            argumentParts = argumentLine.split("=")
            if(len(argumentParts) == 2):
                name = argumentParts[0].strip()
                value = argumentParts[1].strip()
                arguments[name] = value
                print("CIniParser: name:%s value:%s" % (name, value))
                
        return arguments
                
        