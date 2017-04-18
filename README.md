# Saferoom CA
Lightweight Certificate Authority with REST API

# Features
to be defined

# Installation
This application can be installed manually or run as a Docker container. See the corresponding section below
## Docker
Saferoom CA can be run as a Docker container. Below you can find the instructions how to run Saferoom CA on CentOS, Ubuntu, Windows 10 and Windows 7
### CentOS
To run Saferoom CA as a Docker container on a CentOS please do the following:
1. Install Docker
    '''
     yum install docker
    '''
2. Pull the image from Docker Hub
3. Create a volume that will be used to store SQLite DB file. By default Saferoom CA is using SQLite database to store data
4. Run the container with specified volume
## Manual
