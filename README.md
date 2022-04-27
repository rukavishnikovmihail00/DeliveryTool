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

    Note, that credentials must be `ARTIFACTORY_LOG=admin`:`ARTIFACTORY_PASS=password` for the first Artifactory launch.

- __Run the tool__
	
    Execute `delivery-tool-rukavishnikov-0.1.0.pyz` with any function

________________________________________________________________________________________________________________________

## Usage

- __install__ 

  ```python3 delivery-tool-rukavishnikov-0.1.0.pyz install [-r 1]```

    `-r` is optional, so you can include it, if you need to create Generic repository automatically.
    Note, that you need to specify default `admin/password` credentials for `install -r True` option.


  For the next functions you need to contain `create.yaml` and `artifactory.yaml` files in the same directory as delivery-tool-rukavishnikov.pyz 

- __pack__

   ```python3 delivery-tool-rukavishnikov-0.1.0.pyz pack```  


- __upload__  

  ```python3 delivery-tool-rukavishnikov-0.1.0.pyz upload```

Generic and Docker repositories are required for `upload` and `show` functions.  

Artifactory UI also requires a manual action in order to push images with `skopeo`:  

- Go to Artifactory -> General -> HTTP Settings
- Choose `port` as Docker Access Method
- Choose `nginx` as Server Provider
- Specify `localhost` as Internal Hostname and Public Server Name
- Specify HTTP Port (17001 according to my example)

Don't forget to `export` your new credentials, do:
```shell
export ARTIFACTORY_LOG=<your login>
export ARTIFACTORY_PASS=<your new password>
```


- __show__

    ```python3 delivery-tool-rukavishnikov-0.1.0.pyz show```
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





   

