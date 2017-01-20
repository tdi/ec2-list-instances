#!/usr/bin/env python
import boto3
import sys
from tabulate import tabulate

if __name__ == "__main__":
    session = boto3.session.Session()
    ec2 = session.resource('ec2')
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    fortab = []
    for i in instances:
        name = ""
        for tag in i.tags:
            if tag['Key'] == 'Name':
                name = tag['Value']
        fortab.append([name, i.public_ip_address, i.public_dns_name, i.private_ip_address, i.private_dns_name])
    print tabulate(fortab, ['Name', 'Public IP', 'Public DNS', 'Private IP', 'Private DNS'])
