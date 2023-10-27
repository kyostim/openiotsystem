
class CFile: 
    def GetFileContent(filename):
        content=''
        filename = filename.replace("//","/")
        try:
            contentfile = open(filename, 'r')
            content = contentfile.read()
            contentfile.close()
            print("CFile::GetFileContent %s (%i bytes)" % (filename, len(content)))
        except Exception as e:
            print("CFile::GetFileContent %s (%s)"% (filename, e))
            
        return str(content)
    
    def SetFileContent(filename, content):
        filename = filename.replace("//","/")
        try:
            contentfile = open(filename, 'w')
            contentfile.write(content)
            contentfile.close()
            print("CFile::SetFileContent %s (%i bytes)" % (filename, len(content)))
        except Exception as e:
            print("CFile::SetFileContent %s (%s)"% (filename, e))
            
        return str(content)

