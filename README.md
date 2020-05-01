### Intro

Here is something i put together to learn more about cloudformation. I understand there are more people who are more interested in Terraform and i must admits I am also a fan and have written a lot of Terraform.

The only problem i find with terraform is that it is not AWS native, managing different terraform versions, terraform states acrosses multiple AWS accounts (and in my job, sometimes we are dealing with 10,20 accounts :( ) , it is not sustainable.

Using cloudformation is tidious and writing / debugging it is a pain and the error message you get can be a bit confusing, documentation is no where near as good as terraform AWS module. 

With that said, when you get the hang of it, deploying and rolling back works beautifully and the cloud experience is really complehiste because you are managing and doing everything inside AWS ecosystem.

This stack is still an experiment and the teplate is hosted in this public s3 bucket:

https://cfsec.s3.amazonaws.com/template/cfsec.cform

along with packaged lambda function here

https://cfsec.s3.amazonaws.com/assets/snstoslack.zip


### CFSEC

CFSEC contains some simple Cloudformation patterns that I use and hopefully it would help you in building yours.
CFSEC, when fully deployed contains the following features (more to be added when i clean up my code):

 - SNStoSlack lambda function that would send slack notification to you. This piece of code is aggregated and modified to support AlarmMetric SNS trigger + AutoScaling and custom event you want to send from other sources. This is the one place you want to change if your slackwebhook changes.
 - SNS Topic for the SNStoSlack Lambda: Anything you want to trigger slack notification can/should publish to this topic. 
 - HoneyHost EC2 machine running knockd and would publish notification to SNS topic to trigger slack alert - This is my poor man way for Canary host to monitor someone scanning internally. Granted this can also be done by looking at VPC flowlog (rise of ACCESS DENY) and that could be something I want to do in the future if it's not expensive.

 Here is an example of what the slack alert looks like :) 

 ![image](/images/cfsec.png)

 Please ignore the ugly `build.sh` script i put together to make development quicker/easier.

 Working with massive Yaml file can be tricky, i highly recommend using vscode extension called fold-plus ;)