# Installing Amber

- Tested on a fresh Ubuntu 22.04 machine running Python 3.10.12
- Install time 0.5-1 cup of coffee

### 1. Upgrade system packages

```Shell
sudo apt update
sudo apt upgrade -y
```

### 2. Clone Amber into root

```Shell
cd /
git clone https://github.com/roshanshibu/amber.git
```

### 3. Install NGINX

```Shell
sudo apt install nginx
```

### 4. Update NGINX config

Update `/etc/nginx/nginx.conf` to:

```nginx
http{
        server{
                listen 80 default_server;
                listen [::]:80 default_server;

                server_name (your.hostname.com);

                location /Music {
                        if ($request_method = OPTIONS) {
                                add_header Access-Control-Allow-Origin *;
                                add_header Access-Control-Allow-Methods 'GET, OPTIONS';
                                add_header Access-Control-Allow-Headers 'Authorization';
                                add_header Content-Type text/plain;
                                add_header Content-Length 0;
                                return 204;
                        }
                        root /amber;
                        add_header Access-Control-Allow-Origin *;
                        auth_request /auth;
                }

                location / {
                        proxy_pass http://127.0.0.1:5000;
                }

                location = /auth {
                        internal;
                        proxy_pass http://127.0.0.1:5000/dummyAuth;
                        #add_header Access-Control-Allow-Origin *;
                        proxy_pass_request_body off;
                        proxy_set_header Content-Length "";
                        proxy_set_header X-Original-URI $request_uri;

                }
        }
}

events{}
```

Reload nginx for changes to take effect

```Shell
nginx -s reload
```

### 5. Configure SSL with Certbot

> [Detailed Doc here](https://github.com/christianlempa/videos/tree/main/nginx-reverseproxy)

Install certbot

```Shell
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d (your.hostname.com)
```

Follow the instructions on screen

Test auto-renewal of SSL certificates with:

```Shell
certbot renew --dry-run
```

### 6. Dependency Installs

Install llvm and ffmpeg

```Shell
wget https://apt.llvm.org/llvm-snapshot.gpg.key
sudo apt-key add llvm-snapshot.gpg.key
echo "deb http://apt.llvm.org/focal/ llvm-toolchain-focal-10 main" | sudo tee /etc/apt/sources.list.d/llvm.list

sudo apt update
sudo apt install llvm-10 llvm-10-dev

sudo apt install ffmpeg
```

### 7. Prepare Python Environment

```Shell
apt install python3-pip
apt install python3-venv
```

Create an environment inside the Scripts folder

```Shell
python3 -m venv AMBER_ENV
```

Activate the environment

```Shell
source AMBER_ENV/bin/activate
```

Install requirements

```Shell
pip install -r requirements.txt
```

Create `.env` file with the following contents

```properties
AMBER_DUMMY_TOKEN=token_value_here
```

### 8. Run the flask server

```Shell
python server.py
```
