#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Deprecated
# Only for retrocompatibility of Motu <= v1.7
import motuclient

deprecatedWarnMsg = '"motu-client" module is deprecated since version1.8. A new Python module named "motuclient" without a dash separator between motu and client shall be used instead of "motu-client".'
motuclient.initLogger()
motuclient.log.warn(deprecatedWarnMsg)


def main():
    motuclient.main()


if __name__ == '__main__':
    motuclient.main()
