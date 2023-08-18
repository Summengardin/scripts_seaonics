# Docker container
Run docker container with
> sudo docker run --name rtsp-to-web --network host -v <PATH_TO_FOLDER>/config/config.json:/config/config.json ghcr.io/deepch/rtsptoweb:latest

# Config
See (the config file)[./config/config.json] for an example. Keep in mind its not strictly necessary to change it, as changes made 
in the web GUI will be added to the config