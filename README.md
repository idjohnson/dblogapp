
# Logs DB

An app for testing ingestion of logs from a remote service.

This uses a deployment in Kubernetes, an Azure Service Bus Queue and a PostgreSQL database.

In my case, I'm using a free-tier instance in Aiven.io for the Database (but one could host PostgreSQL anywhere).

Before using the databse, please use the script in 'dbinit.sql' to set up the initial tables and (optional) sample data.

# Local Testing


## Building

```
$ docker build -t mytestdb:0.1 .
[+] Building 6.3s (10/10) FINISHED                                                                       docker:default
 => [internal] load build definition from Dockerfile                                                               0.0s
 => => transferring dockerfile: 371B                                                                               0.0s
 => [internal] load metadata for docker.io/library/python:3.9-slim                                                 0.0s
 => [internal] load .dockerignore                                                                                  0.0s
 => => transferring context: 2B                                                                                    0.0s
 => [1/5] FROM docker.io/library/python:3.9-slim                                                                   0.0s
 => [internal] load build context                                                                                  0.1s
 => => transferring context: 5.67kB                                                                                0.0s
 => CACHED [2/5] WORKDIR /app                                                                                      0.0s
 => [3/5] COPY requirements.txt .                                                                                  0.1s
 => [4/5] RUN pip install --no-cache-dir -r requirements.txt                                                       4.9s
 => [5/5] COPY . .                                                                                                 0.1s
 => exporting to image                                                                                             0.3s
 => => exporting layers                                                                                            0.2s
 => => writing image sha256:f4c51396601bb37f93f5028ddd9d2f8d32b5f8a129a0c63c6efaa6cfa1222e22                       0.0s
 => => naming to docker.io/library/mytestdb:0.1                                                                    0.0s
```

## Running

We can now run locally
```
$ docker run -p 5000:5000 mytestdb:0.1
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.17.0.2:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 779-498-882
172.17.0.1 - - [12/Jun/2025 20:21:50] "GET / HTTP/1.1" 200 -
```


# Az Service Bus Test

First, setup the environment
```
$ pip3 install azure-servicebus --break-system-packages
```

Then you can push the message
```
$ export SERVICE_BUS_CONNECTION_STR="Endpoint=sb://daprpubsubdemo1.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=xxxxxxxxxxxx
$ python3 send_message.py
```