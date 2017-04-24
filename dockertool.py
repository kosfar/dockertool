#!/usr/bin/python

# A tool for managing the deployment and monitoring of a set of web
# services containers using Docker containers and it's Remote API

import os
import argparse
import subprocess
from string import Template
import tempfile
import docker
import logging
import utils

# Builds a Docker image from a given path where the Dockerfile
# and the app reside
def _build(image, build_path):
    client = docker.from_env()
    image = client.images.build(path=build_path,tag=image,rm=True)

# Deploy a few containers from an image
def _deploy(image):
    client = docker.from_env()
    for x in range(0, 3):
        container = client.containers.run(image=image, detach=True)

# Using docker client CLI commands
# TBD: migrate to using the API
def _stack_deploy(compose_file, image, stack):

    filein = open(compose_file)
    src = Template(filein.read())
    d={ 'image':image }
    result = src.substitute(d)

    with tempfile.NamedTemporaryFile() as temp:
        temp.write(result)
        temp.flush()
        cmd = "sudo docker stack deploy -c {} {}".format(temp.name,stack)
        p = subprocess.Popen(cmd , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if err:
            logging.debug('%s' % err)
        temp.close()

# Validates container instances' state
def _checkstate():
    client = docker.from_env()
    for container in client.containers.list(all=True):
      print "{}: {}".format(container.short_id, container.status.upper())

# Consolidate the log output of all the containers in a single file
def _collectlogs(log_file):
    client = docker.from_env()
    f = open(log_file, 'w')

    for container in client.containers.list(all=True):
        f.write(container.logs())

    f.close()

# Monitor the resource usage of each container
def _monitor():
    client = docker.from_env()
    if len(client.containers.list()) != 0:
        for container in client.containers.list():
           constat = container.stats(stream=False)
           print "{}: CPU: {} MEM: {}".format(container.short_id, \
                  utils.get_cpu_percentage(container,constat), utils.get_mem_percentage(container,constat))
    else:
        print "No containers are running :("

def main():

    # Ugly bork-out until we fix our socket permissions
    if not os.geteuid() == 0:
        exit("\nOnly root can run this script\n")

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug',  help="Print lots of debugging statements", action="store_const", 
                            dest="loglevel", const=logging.DEBUG, default=logging.WARNING)
    parser.add_argument('-v', '--verbose', help="Be verbose", action="store_const", 
                            dest="loglevel", const=logging.INFO,)
 
    parser.add_argument('action', choices=('build', 'deploy', 'stack_deploy', 'checkstate', 'monitor', 'collectlogs'))
    parser.add_argument('--image', dest='image', default=argparse.SUPPRESS)
    parser.add_argument('--build-path', dest='build_path', default=argparse.SUPPRESS)
    parser.add_argument('--compose-file', dest='compose_file', default=argparse.SUPPRESS)
    parser.add_argument('--stack', dest='stack', default=argparse.SUPPRESS)
    parser.add_argument('--log-file', dest='log_file', default=argparse.SUPPRESS)

    args = parser.parse_args()
 
    logging.basicConfig(level=args.loglevel)

    if args.action == 'build':
        _build(args.image,args.build_path)
    if args.action == 'stack_deploy':
        _stack_deploy(args.compose_file,args.image,args.stack)
    if args.action == 'deploy':
        _deploy(args.image)
    if args.action == 'checkstate':
        _checkstate()
    if args.action == 'monitor':
        _monitor()
    if args.action == 'collectlogs':
        _collectlogs(args.log_file)

if __name__ == '__main__':
    main()
