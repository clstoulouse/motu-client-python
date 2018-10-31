import sys
import os

MOTU_CLIENT_CONFIG_PATH = os.path.join("motu_utils", "cfg")
LINUX_CONFIG_PATH = os.path.join("/usr", "local", MOTU_CLIENT_CONFIG_PATH)
WINDOWS_CONFIG_PATH = os.path.join(sys.prefix, MOTU_CLIENT_CONFIG_PATH)
VIT_ENV_CONFIG_PATH = MOTU_CLIENT_CONFIG_PATH
LOCAL_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "motu_utils", "cfg")

def getConfigPath():
    if os.path.isdir(LINUX_CONFIG_PATH):
    	return LINUX_CONFIG_PATH
    elif os.path.isdir(WINDOWS_CONFIG_PATH):
    	return WINDOWS_CONFIG_PATH
    elif os.path.isdir(LOCAL_CONFIG_PATH):
        return LOCAL_CONFIG_PATH
    elif os.path.isdir(VIT_ENV_CONFIG_PATH):
    	return VIT_ENV_CONFIG_PATH
    else:
    	return ""