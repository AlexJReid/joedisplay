#!/bin/sh
rm -f event-producer-lambda.zip
cd vendor
zip -r9 ${OLDPWD}/event-producer-lambda.zip .
cd $OLDPWD
zip -g deployment.zip *.py
echo
echo '... ok now please upload deployment.zip to Lambda... you probably could afford a better deployment pipeline?! 🤠'
