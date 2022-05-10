# pull a light python docker image
FROM python:3.8-slim-buster

# copy required files to the container
RUN mkdir -p /home/app
COPY requirements.txt run_server.sh /home/app/
COPY ./app/nginx /home/app/nginx
COPY ./app/client /home/app/client
COPY ./app/server /home/app/server

# set a directory for the app
WORKDIR /home/app

# install dependencies
RUN apt-get update -y \
  && apt-get install -y --no-install-recommends \
     nginx \
  && pip install --upgrade pip setuptools \
  && pip install --no-cache-dir -r requirements.txt \  
  && apt-get purge -y --auto-remove $buildDeps \
  && rm -rf /var/lib/apt/lists/*

RUN pwd && ls -lh . && ls -lh server/  

# configure nginx
RUN pwd \
  && cp /home/app/nginx/nginx_home_prices.conf /etc/nginx/sites-available/nginx_home_prices.conf \
  && unlink /etc/nginx/sites-enabled/default \
  && ln -v -s /etc/nginx/sites-available/nginx_home_prices.conf /etc/nginx/sites-enabled \
  && ls -lh /etc/nginx/sites-enabled 
  
# port number the container should expose
EXPOSE 8080

# run script that start nginx and gunicorn when running container
CMD ["bash" , "run_server.sh"]
