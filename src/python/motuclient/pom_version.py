from xml.etree import ElementTree

def getPOMVersion():
    version="Unknown"  # replace your path
    try:
        version = __getPOMVersion("pom.xml")
    except:
        version = __getPOMVersion("../../pom.xml")
    return version
    
def __getPOMVersion(POM_FILE):
    namespaces = {'xmlns' : 'http://maven.apache.org/POM/4.0.0'}
    tree = ElementTree.parse(POM_FILE)
    root = tree.getroot()
    version = root.find("xmlns:version", namespaces=namespaces)
    return str(version.text)