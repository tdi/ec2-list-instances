#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import sys
from tabulate import tabulate
import ConfigParser
import cmd
import os
import signal
__version__ = '0.1'

class EC2cmd(cmd.Cmd):
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.instance_cache = {}
        self.profile = None
        self.profiles = []
        self.prompt = '(aws) '
        self.intro = 'Welcome to the simple AWS EC2 shell'

    def _load_profiles(self):
        cp = ConfigParser.ConfigParser()
        cp.read(os.getenv('AWS_HOME') + '/config')
        for i in cp.sections():
            if 'profile' in i:
               self.profiles.append(i.split()[1])
            else:
                self.profiles.append(i)

        
    def _make_session(self):
        if self.profile:
            try:
                self.session = boto3.session.Session(profile_name = self.profile)
                return
            except Exception, e:
                print("➜  Can't find profile {}".format(self.profile))
        else:
            try:
                self.session = boto3.session.Session()
            except Exception, e:
                print("➜  Can't find profile {}".format(self.profile))
                return
        self.ec2 = self.session.resource('ec2')

    def preloop(self):
        self._load_profiles()
        self._make_session()

    def complete_ssh(self, text, line, begidx, endidx):
        if not text:
            completions = self.instance_cache.keys()[:]
        else:
            completions = [ f for f in self.instance_cache.keys() if f.startswith(text)]
        return completions

    def complete_profile(self, text, line, begidx, endidx):
        if not text:
            completions = self.profiles[:]
        else:
            completions = [ f for f in self.profiles if f.startswith(text)]
        return completions

    def _ssh(self, host, profile=None, timeout=10):
        if profile:
            host = profile + '+' + host
            return "ssh -o ConnectTimeout={} {}".format(timeout, host)
        else:
            return "ssh -o ConnectTimeout={} {}".format(timeout, host)


    def do_ssh(self, line):
        """ ssh [hostname | #] connects to a hostname """
        print(self.instance_cache)
        print(type(line))
        print(self.instance_cache[line])
        if line not in self.instance_cache:
            os.system(self._ssh(line, profile=self.profile ))
        os.system(self._ssh(self.instance_cache[line][2], profile=self.profile))
        
    def do_profiles(self, line):
        """ Show profiles from $AWS_HOME/config 
            or profiles reload will reread profiles from $AWS_HOME/config 
        """
        if line == 'reload':
            print('➜ Reloading profiles')
            self._load_profiles()
        print ', '.join(self.profiles)

    def do_profile(self, line):
        """ Set profile as defined in $AWS_HOME/config """
        if line:
            self.profile = line
            self._make_session()
            self.prompt = '(aws) ' + self.profile + ' ' 
        print 'Profile set to ' + self.profile
  
    def do_exit(self, line):
        """ Exits the shell """
        raise SystemExit

    def emptyline(self):
        pass 

    def do_show(self, line):
        """ Show instances in a table """
        a = self._show()
        if a:
            print a

    def _show(self):
        instances = self.ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        fortab = []
        index = 1
        try:
            for i in instances:
                name = ""
                for tag in i.tags:
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                fortab.append([index, name, i.instance_id, i.public_ip_address, i.private_ip_address])
                self.instance_cache[str(index)] = (name, i.public_ip_address, i.private_ip_address, i.instance_id)
                index = index + 1
        except Exception, e:
            print('➜ Unfortunately, an error occurred, check if AWS_* variables are set')
            return
        return tabulate(fortab, ['#', 'Name', 'Instance ID', 'Public IP', 'Private IP'])

if __name__ == "__main__":
    def signal_handler(signal, frame):
        print('bye!')
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    EC2cmd().cmdloop()

