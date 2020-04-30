#!/bin/bash
set -e

set -x 
zip snstoslack.zip snstoslack.py
aws s3 cp snstoslack.zip s3://cfsec/assets/
aws s3 cp cfsec.cform s3://cfsec/template/
set +x

echo -e "Our template location: \033[0;32mhttps://cfsec.s3.amazonaws.com/template/cfsec.cform\033[0m"
