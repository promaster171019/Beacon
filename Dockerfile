# docker build -t ubuntu1604py36
FROM ubuntu:16.04
LABEL python_version=python3.6

RUN apt-get update
RUN apt-get install -y software-properties-common vim
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv
RUN apt-get install -y git

# update pip
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

RUN apt-get -y install libpango1.0-0
RUN apt-get -y install libcairo2
RUN apt-get -y install libpq-dev
RUN apt-get install -y nginx
RUN apt-get install -y uwsgi
RUN apt-get install -y supervisor
RUN apt-get install -y uwsgi-plugin-python3
RUN apt-get install -y libssl-dev uwsgi-src uuid-dev libcap-dev libpcre3-dev
RUN apt-get -y upgrade

RUN pip3 install virtualenv
RUN virtualenv --no-download /env -p python3.6

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

ADD . /app/BEacon
COPY ./dockerfiles/nginx.conf /etc/nginx/nginx.conf
COPY ./dockerfiles/uwsgi.ini /etc/uwsgi/apps-enabled
#COPY ./dockerfiles/localtime /etc/localtime

RUN pip3 install -r /app/BEacon/requirements.txt
RUN mkdir -p /var/log/app_engine

# uwsgi create plugin python 3.6
RUN export PYTHON=python3.6
RUN uwsgi --build-plugin "/usr/src/uwsgi/plugins/python python36"
RUN mv python36_plugin.so /usr/lib/uwsgi/plugins/python36_plugin.so
RUN chmod 644 /usr/lib/uwsgi/plugins/python36_plugin.so

CMD ["bash", "/app/BEacon/dockerfiles/entrypoint.sh"]
