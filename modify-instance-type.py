#!/usr/bin/python3
import sys
import boto3
import time

sys.stdout.flush()

instance_id = sys.argv[1]
target_type = sys.argv[2]

ec2C = boto3.client('ec2', region_name='ap-south-1')

describeEc2 = ec2C.describe_instances(InstanceIds=[instance_id,])
source_type = describeEc2['Reservations'][0]['Instances'][0]['InstanceType']
describeEc2Status = ec2C.describe_instance_status(InstanceIds=[instance_id,], IncludeAllInstances=True)

if describeEc2Status['InstanceStatuses'][0]['InstanceState']['Name'] == "running":
    ec2C.stop_instances(InstanceIds=[instance_id,])
    for retries in range(1,7):
       # response = ec2C.describe_instance_status(InstanceIds=[instance_id,], IncludeAllInstances=True)
        response = ec2C.Instance(instance_id)
        if response.state['Name'] != "stopped":
            if retries == 6:
                print("Instance is taking longer than usual time to stop. Better check the status in console")
                break
            time.sleep(retries*60)
        elif response.state['Name'] == "stopped":
            print("Instance successfully stopped")
            break

ec2C.modify_instance_attribute(
    InstanceId=instance_id,
    InstanceType={
        'Value': target_type,
    },
)

ec2C.start_instances(InstanceIds=[instance_id,])
for retries in range(1,7):
    response = ec2C.Instance(instance_id)
    if response.state['Name'] == "running":
        print("The instance with id {} is successfully started with new instance type {}".format(instance_id, target_type))
        break
    elif retries == 6:
        print("The instance took longer time than usual to start, better check the status in the console")
        break
    time.sleep(retries*60)

upgradedEc2 = ec2C.describe_instances(InstanceIds=[instance_id,], IncludeAllInstances=True)
upgradedEc2Ip = upgradedEc2['Reservations'][0]['Instances'][0]['PublicIpAddress']
