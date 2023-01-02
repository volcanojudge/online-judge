FROM python:slim

RUN useradd --create-home volcano
RUN apt update
RUN apt install -y g++ libseccomp-dev sqlite3

USER volcano
RUN mkdir /home/volcano/judge
WORKDIR /home/volcano/judge
ENV PATH="${PATH}:/home/volcano/.local/bin"
RUN pip3 install flask flask_login flask_sqlalchemy flask_admin flask_migrate requests gunicorn

ADD src /home/volcano/judge
ADD wsgi.py /home/volcano/judge
ADD secret_key.txt /home/volcano/judge

USER root
RUN chown -R volcano:volcano *

USER volcano
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--log-file", "server.log", "wsgi:app"]


