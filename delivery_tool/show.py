from artifactory import ArtifactoryPath
import backoff
import requests


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=10)
def connect(url, name, creds, name_docker):
    art = ArtifactoryPath(url + '/' + name, auth=(creds['login'], creds['password']))
    res_docker = art.find_repository_local(name_docker)

    summary_size = 0
    summary_size_docker = 0

    for p in res_docker:
        summary_size_docker += p.stat().size

    res = art.find_repository_local(name)
    for p in res:
        summary_size += p.stat().size
    
    return summary_size, summary_size_docker


def show(art_config, creds, log):
    exceptions = []
    url = art_config['url']
    name = art_config['repositories']['files']
    name_docker = art_config['repositories']['docker']

    try:
        summary_size, summary_size_docker = connect(url, name, creds, name_docker)

    except requests.exceptions.RequestException as e:
        exceptions.append(e)

    if len(exceptions) != 0:
        log.debug("An exception occured while Artifactory connection\n")
        log.debug(exceptions)
    if len(exceptions) == 0:
        log.info(f"Summary size of files in {name} is {round(summary_size/1048576,2)} MB")
        log.info(f"Summary size of files in {name_docker} is {round(summary_size_docker/1048576,2)} MB")