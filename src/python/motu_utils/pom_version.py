from xml.etree import ElementTree
import os

def getPOMVersion():
    version="Unknown"
    try:
        # For production tree, while run from cur folder
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        version = __getPOMVersion(os.path.join(dname, "..", "pom.xml") )
    except:
        # For development tree
        try:
            version = __getPOMVersion(os.path.join(dname, "..", "..", "pom.xml") )
        except :
            version = __getPOMVersion(os.path.join(dname, "..", "..", "..", "pom.xml") )
    finally:
        return version
    
def __getPOMVersion(POM_FILE):
    namespaces = {'xmlns' : 'http://maven.apache.org/POM/4.0.0'}
    tree = ElementTree.parse(POM_FILE)
    root = tree.getroot()
    version = root.find("xmlns:version", namespaces=namespaces)
    return str(version.text)
