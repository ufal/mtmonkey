MTMonkey in Docker
==================

MTMonkey supports running workers together with Moses server inside Docker
containers. Running the appserver in Docker is not supported at the moment.

Because workers are able to automatically register with the appserver (and
unregister on exit), deploying new MT systems with Docker can be quite flexible.

To use MTMonkey in Docker, you first need to [install
Docker](https://docs.docker.com/engine/installation/). You will also need to
build the MTMonkey Docker image.

Building the Docker image
-------------------------

In the directory `docker/worker`, run the following command:

```
docker build -t mtmonkey-worker --build-arg CPU_CORES=4 .
```

You can set the number of CPU cores higher to speed up the build. Once the
command finishes, your image should be available for use. You can verify that by
running the following command:

```
docker images
```

Appserver configuration
-----------------------

Here we assume that you have already installed the MTMonkey appserver. In order
to enable dynamic registration of workers, you need to set up a shared
passphrase for the appserver and the workers. In the appserver configuration,
add the following line:

```
PASSPHRASE = 'verysecret'
```

Because workers in Docker automatically register with the server, there is no
need to specify which workers are available. A minimal configuration file looks
as follows:

```
PORT = 8080
WORKERS = {}
URL = '/mtmonkey'
PASSPHRASE = 'verysecret'
```

Model preparation
-----------------

MTMonkey uses [Docker
volumes](https://docs.docker.com/engine/tutorials/dockervolumes/) to provide
Moses models to the container. If you have a trained Moses model, put all the
required files into a directory and make sure that the primary configuration
file `moses.ini` uses only relative paths. For example, a language model feature
could be defined as follows:

```
KENLM name=LM0 factor=0 path=lm.trie order=5
```

Running the containers
----------------------

Once you have set up and started the appserver and prepared the model, you can
start the Docker container using the following command:

```
WORKER_PUBLIC_PORT=9999
APPSERVER_URL="http://example.com:8080/mtmonkey"
PASSPHRASE="verysecret"
SRCLANG=fr
TGTLANG=en
CPU_CORES=4
MODEL_PATH=/path/to/model/directory/

docker run -d -p $WORKER_PUBLIC_PORT:8080 \
  -e MTMONKEY_APPSERVER_URL="$APPSERVER_URL" \
  -e MTMONKEY_PASSPHRASE="$PASSPHRASE" \
  -e MTMONKEY_PUBLIC_PORT=$WORKER_PUBLIC_PORT \
  -e MTMONKEY_SRCLANG=$SRCLANG \
  -e MTMONKEY_TGTLANG=$TGTLANG \
  -e CPU_CORES=$CPU_CORES \
  -v $MODEL_PATH:/mt-model mtmonkey-worker
```

Change the variable values as appropriate. Note that the model directory must be
mounted in the `/mt-model` directory in the container and that it must contain
the file `moses.ini` for the Moses server.

Docker creates a virtual network interface for each container that it starts and
by default, it assigns a random port to the service port exposed by the
container (the MTMonkey worker runs on port 8080 in the container). Do not use a
random port number; instead, choose a free port and bind it manually using the
parameter `-p` when executing `docker run`. For the worker registration to
function, you must provide this public port number as an environment variable
`MTMONKEY_PUBLIC_PORT` to the container (so that the worker can report this port
number to the appserver).

When the worker registers with the appserver, the server will automatically use
the IP address of the request. In some cases, this is not the correct address
where the worker is reachable on. To override this behavior, you may also
provide the correct IP address using an additional environment variable
`MTMONKEY_PUBLIC_ADDR`.
