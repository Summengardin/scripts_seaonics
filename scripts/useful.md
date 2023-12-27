
```shell
# See listening netowork ports
$ sudo lsof -i -P -n | grep LISTEN
```

```shell
# Run docker file with nvidia hardware
$ docker run -it --rm --net=host --runtime nvidia --gpus all -v /tmp/argus_socket:/tmp/argus_socket <CONTAINER-NAME>
```

```shell
# export docker image (f.eks to another computer)
$ docker save -o <output-name>.tar <image-name>:<optionally-tag>
```

```shell
# Import docker image
$ docker load -I <output-name>.tar
```