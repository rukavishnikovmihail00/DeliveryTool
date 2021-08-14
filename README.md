# Delivery-tool

The tool provides artifacts delivery to your local Artifactory storage

![](https://raw.githubusercontent.com/rukavishnikovmihail00/testGit/newbranch/delivery_tool.png "Delivery tool")
_______________________________________________________________________________________________________________________

There are 4 functions of the Delivery tool:
- __install__ - read an installation config and install Artifactory to the instance using ansible.
- __pack__   - read a packing config, download files and docker images using skopeo, create an archive with some structure.
- __upload__ - unpack the archive, parse an uploading config and the archive structure and upload files to Artifactory instance. Show full and delta size of
repositories.
- __show__   - show space by a repository.
_______________________________________________________________________________________________________________________

## Prerequisites
There are the things that have to be pre-installed on your system

- Python 3.8     :white_check_mark:
- Docker 20.10.7 :white_check_mark:
- Docker-compose 1.29.2 :white_check_mark:
- Skopeo 1.4.0 :white_check_mark:
- Ansible 2.11.1 :white_check_mark:
________________________________________________________________________________________________________________________

## User guide
There is an information about Delivery tool usage

- __Set your configurations__

    Change `config.yaml` and `artifactory.yaml` according to the example below.

- __Specify your credentials for Artifactory instance__

    Note, that credentials must be `ARTIFACTORY_LOG=admin`:`ARTIFACTORY_LOG=password` for the first Artifactory launch.

- __Run the tool__
	
    Execute `delivery-tool-rukavishnikov-0.1.0.pyz` with any function

________________________________________________________________________________________________________________________

That`s how Delivery tool functions are used:

- __install__ 

    usage: **python3 delivery-tool-rukavishnikov.pyz install [-r 1]**
	
    `-r` is optional, so you can include it, if you need to create Generic repository automatically.
    Note,  that `install` option needs sudo privileges.


    For the next functions you need to contain `create.yaml` and `artifactory.yaml` files in the same directory as delivery-tool-rukavishnikov.pyz 

- __pack__

    usage: **python3 delivery-tool-rukavishnikov.pyz pack**

- __upload__

    usage: **python3 delivery-tool-rukavishnikov.pyz upload**

    Generic and Docker repositories are required for `upload` and `show` functions

- __show__

    usage: **python3 delivery-tool-rukavishnikov.pyz show**
________________________________________________________________________________________________________________________

### The example of config.yaml

```
   files:
   - https://docker.bintray.io/artifactory/bintray-tools/com/jfrog/bintray/client/api/0.2/api-0.2.jar
   - https://docker.bintray.io/artifactory/jfrog-cli/v1/1.0.0/jfrog-cli-linux-386/jfrog
   images:
   - docker.bintray.io/jfrog/artifactory-pro:7.19.8
   - docker.bintray.io/postgres:13.2-alpine
   - docker.bintray.io/jfrog/nginx-artifactory-pro:7.19.8
```

You need to specify file URLs in `files` section and Docker images in `images` section according to the example above
_________________________________________________________________________________________________________________________
### The example of artifactory.yaml

```
   url: http://10.0.2.15:8082/artifactory
   docker_registry: 10.0.2.15:17001
   repositories:
     files: delivery_tool.files
     docker: delivery-tool.docker
   home_dir: /home/mikhail/.jfrog
   lic_path: /home/mikhail/artifactory.lic
```

This configuration file needs to contain the Artifactory URL specified in `url` section and docker registry.
In `repositories` section there should be a Generic repository name in `files` and Docker repository name in `docker`.
`lic_path` is a path to your artifactory.lic file, that contains Artifactory license key.
Besides, please, specify the Docker images in `images` section and your Artifactory home directory in `home_dir`.
_________________________________________________________________________________________________________________________





   

