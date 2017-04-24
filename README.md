# README #

### What is this repository for? ###

This repository is about a tool for managing the deployment and monitoring of a set of web services containers.

### How do I get set up? ###

The only thing that is needed is a Python 2.7 runtime environment.

### Example usage ###

```
./dockertool.py build --image test --build-path sample_app
./dockertool.py deploy --image test
./dockertool.py monitor
./dockertool.py collectlogs --log-file /tmp/all.log
./dockertool.py checkstate
```

### Future steps ###
* Better logging/debugging functionality
* Embed testing and CI workflow using a tool of choice like Travis CI
* Migrate the stack_deploy action to using Docker Engine API. Sample usage:
```./dockertool.py stack_deploy --compose-file sample_app/docker-compose.yml --image test --stack testlab```