#!/usr/bin/env bash
# Script used to build when project is cloned from on GitHub
#Test to comment only once
stringParent=`head -n 2 pom.xml | tail -n 1`
if [[ "$stringParent" != *"--"* ]]; then
    echo "INFO: Comment in pom.xml the parent tag because it is only usable in CLS premise for CLS specific tasks, but not necessary at all on GitHub to build the project."
    sed -i "1,/<parent/ s/<parent/<\!-- <parent/; 1,/<\/parent>/ s/<\/parent>/<\/parent> -->/;" pom.xml
    echo "INFO: Done."
fi
