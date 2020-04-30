import json
import urllib
import urllib3
import os

# Loading SLACK_WEBHOOK environment variable set via cloudformation template.
SLACK_URL = os.getenv('SLACK_WEBHOOK')
ICON = {
    "cloudwatch": {
        "OK":  ":cloudwatch:",
        "ALARM": ":alarm:",
    },
    "autoscaling": {
        "EC2_INSTANCE_LAUNCH":      ":heavy_plus_sign:",
        "EC2_INSTANCE_LAUNCH_ERROR":  ":no_entry:",
        "EC2_INSTANCE_TERMINATE":     ":heavy_minus_sign:",
        "EC2_INSTANCE_TERMINATE_ERROR": ":no_entry:",
        "TEST_NOTIFICATION":      ":grey_exclamation:",
    },
}


# Send slack notification using webhook.
def nofify_slack(payload):
    headers = {'Content-type': 'application/json'}
    data = json.dumps(payload)
    http = urllib3.PoolManager()
    res = http.request('POST', SLACK_URL, body=data, headers=headers)
    return res


def lambda_handler(event, context):
    records = event["Records"]
    for record in records:
        # Handle SNS trigger:
        if "Sns" in record:
            msg = record["Sns"]["Message"]
            try:
                # Try loading our message as json
                msg = json.loads(msg)
            except:
                # If not, send the raw message to slack.
                print(json.dumps(record["Sns"]))
                payload = {
                    "icon_emoji": ":sns:",
                    "username": str(record["Sns"]["Subject"]),
                    "text": str(msg)
                }
                nofify_slack(payload)
                continue

            # CloudWatch events
            if "AlarmName" in msg:
                payload = {
                    "icon_emoji": ICON["cloudwatch"][msg["NewStateValue"]],
                    "username": "CloudWatch - {0}".format(msg["NewStateValue"]),
                    "text": str(record["Sns"]["Subject"]),
                    "attachments": [
                        {
                            "fallback": str(record["Sns"]["Subject"]),
                            "fields": [
                                {
                                    "title": "AlarmName",
                                    "value": "<https://console.aws.amazon.com/cloudwatch/home#alarm:alarmFilter=ANY;name={0}|{0}>".format(msg["AlarmName"]),
                                    "short": True
                                },
                                {
                                    "title": "Namespace",
                                    "value": str(msg["Trigger"]["Namespace"]),
                                    "short": True
                                },
                                {
                                    "title": "MetricName",
                                    "value": str(msg["Trigger"]["MetricName"]),
                                    "short": True
                                },
                                {
                                    "title": str(msg["Trigger"]["Dimensions"][0]["name"]),
                                    "value": str(msg["Trigger"]["Dimensions"][0]["value"]),
                                    "short": True
                                },
                                {
                                    "title": "Reason",
                                    "value": str(msg["NewStateReason"]),
                                },
                                {
                                    "title": "Description",
                                    "value": str(msg["AlarmDescription"]),
                                },
                            ],
                            "color": "warning"
                        }
                    ]
                }
            # AutoScaling events
            elif "AutoScalingGroupName" in msg:
                event = str(msg["Event"]).split(":")[-1]
                payload = {
                    "icon_emoji": ICON["autoscaling"][event],
                    "username": "AutoScaling - {0}".format(event),
                    "text": str(msg["Description"]),
                    "attachments": [
                        {
                            "fallback": str(msg["Description"]),
                            "fields": [
                                {
                                    "title": "AutoScalingGroup",
                                    "value": "<https://console.aws.amazon.com/ec2/autoscaling/home#AutoScalingGroups:id={0}|{0}>".format(msg["AutoScalingGroupName"]),
                                    "short": True
                                },
                                {
                                    "title": "InstanceId",
                                    "value": "<https://console.aws.amazon.com/ec2/v2/home#Instances:search={0}|{0}>".format(msg["EC2InstanceId"]),
                                    "short": True
                                },
                                {
                                    "title": "Cause",
                                    "value": str(msg["Cause"]),
                                },
                            ],
                            "color": "warning"
                        }
                    ]
                }
            # Custom events
            elif "cfsec_payload" in msg:
                payload = msg["cfsec_payload"]
            # Catch all
            else:
                payload = {
                    "icon_emoji": ":sns:",
                    "username": str(record["Sns"]["Subject"]),
                    "text": json.dumps(msg, indent=4)
                }
                print(json.dumps(record["Sns"]))

            nofify_slack(payload)


# Debug SNS topic locally
if __name__ == "__main__":
    debugSNSevent = json.loads(r"""{
    "Records": [{
        "EventSource": "aws:sns",
        "EventVersion": "1.0",
        "EventSubscriptionArn": "arn:aws:sns:us-east-1:XXX:cw-to-slack-Topic-1B8S548158492:a0e76b10-796e-471d-82d3-0510fc89ad93",
        "Sns": {
            "Type": "Notification",
            "MessageId": "[...]",
            "TopicArn": "arn:aws:sns:us-east-1:XXX:cw-to-slack-Topic-1B8S548158492",
            "Subject": "ALARM: \"cw-to-slack-Alarm-9THDKWBS1876\" in US East (N. Virginia)",
            "Message": "{\"AlarmName\":\"cw-to-slack-Alarm-9THDKWBS1876\",\"AlarmDescription\":null,\"AWSAccountId\":\"XXX\",\"NewStateValue\":\"ALARM\",\"NewStateReason\":\"Threshold Crossed: 1 datapoint [3.22 (29/10/17 13:20:00)] was greater than the threshold (1.0).\",\"StateChangeTime\":\"2017-10-30T13:20:35.831+0000\",\"Region\":\"US East (N. Virginia)\",\"OldStateValue\":\"INSUFFICIENT_DATA\",\"Trigger\":{\"MetricName\":\"EstimatedCharges\",\"Namespace\":\"AWS/Billing\",\"StatisticType\":\"Statistic\",\"Statistic\":\"MAXIMUM\",\"Unit\":null,\"Dimensions\":[{\"name\":\"Currency\",\"value\":\"USD\"}],\"Period\":86400,\"EvaluationPeriods\":1,\"ComparisonOperator\":\"GreaterThanThreshold\",\"Threshold\":1.0,\"TreatMissingData\":\"\",\"EvaluateLowSampleCountPercentile\":\"\"}}",
            "Timestamp": "2017-10-30T13:20:35.855Z",
            "SignatureVersion": "1",
            "Signature": "[...]",
            "SigningCertUrl": "[...]",
            "UnsubscribeUrl": "[...]",
            "MessageAttributes": {}
        }
    }]
    }""")

    debugAutoscaleEvent = json.loads(r"""{
    "Records": [
        {
            "EventSource": "aws:sns",
            "EventVersion": "1.0",
            "EventSubscriptionArn": "arn:aws:sns:us-east-1:123456789123:AutoScalingNotifications:00000000-0000-0000-0000-000000000000",
            "Sns": {
                "Type": "Notification",
                "MessageId": "00000000-0000-0000-0000-000000000000",
                "TopicArn": "arn:aws:sns:us-east-1:123456789:AutoScalingNotifications",
                "Subject": "Auto Scaling: termination for group \"autoscale-group-name\"",
                "Message": "{\"Progress\":50,\"AccountId\":\"123456789123\",\"Description\":\"Terminating EC2 instance: i-00000000\",\"RequestId\":\"00000000-0000-0000-0000-000000000000\",\"EndTime\":\"2016-09-16T12:39:01.604Z\",\"AutoScalingGroupARN\":\"arn:aws:autoscaling:us-east-1:123456789:autoScalingGroup:00000000-0000-0000-0000-000000000000:autoScalingGroupName/autoscale-group-name\",\"ActivityId\":\"00000000-0000-0000-0000-000000000000\",\"StartTime\":\"2016-09-16T12:37:39.004Z\",\"Service\":\"AWS Auto Scaling\",\"Time\":\"2016-09-16T12:39:01.604Z\",\"EC2InstanceId\":\"i-00000000\",\"StatusCode\":\"InProgress\",\"StatusMessage\":\"\",\"Details\":{\"Subnet ID\":\"subnet-00000000\",\"Availability Zone\":\"us-east-1a\"},\"AutoScalingGroupName\":\"autoscale-group-name\",\"Cause\":\"At 2016-09-16T12:37:09Z a user request update of AutoScalingGroup constraints to min: 0, max: 0, desired: 0 changing the desired capacity from 1 to 0.  At 2016-09-16T12:37:38Z an instance was taken out of service in response to a difference between desired and actual capacity, shrinking the capacity from 1 to 0.  At 2016-09-16T12:37:39Z instance i-00000000 was selected for termination.\",\"Event\":\"autoscaling:EC2_INSTANCE_TERMINATE\"}",
                "Timestamp": "2016-09-16T12:39:01.661Z",
                "MessageAttributes": {}
            }
        }
    ]
    }""")
    debugCustomEvent = json.loads(r"""{
    "Records": [
        {
            "EventSource": "aws:sns",
            "EventVersion": "1.0",
            "EventSubscriptionArn": "arn:aws:sns:us-east-1:123456789123:AutoScalingNotifications:00000000-0000-0000-0000-000000000000",
            "Sns": {
                "Type": "Notification",
                "MessageId": "00000000-0000-0000-0000-000000000000",
                "TopicArn": "arn:aws:sns:us-east-1:123456789:AutoScalingNotifications",
                "Subject": "Auto Scaling: termination for group \"autoscale-group-name\"",
                "Message": "{\"cfsec_payload\":{\"icon_emoji\":\":santa:\",\"username\":\"Santrancisco Test\",\"text\":\"Hello world!\"}}",
                "Timestamp": "2016-09-16T12:39:01.661Z",
                "MessageAttributes": {}
            }
        }
    ]
    }""")

    lambda_handler(debugCustomEvent, "")
