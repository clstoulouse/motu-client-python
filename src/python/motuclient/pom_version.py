from xml.etree import ElementTree

def getPOMVersion():
    POM_FILE="pom.xml"  # replace your path
    namespaces = {'xmlns' : 'http://maven.apache.org/POM/4.0.0'}
    tree = ElementTree.parse(POM_FILE)
    root = tree.getroot()
    deps = root.findall(".//xmlns:dependency", namespaces=namespaces)
    versionTxt='unknown'
    for d in deps:
        #artifactId = d.find("xmlns:artifactId", namespaces=namespaces)
        version    = d.find("xmlns:version", namespaces=namespaces)
        versionTxt=str(version.text)#print artifactId.text + '\t' + version.text
    return version.text