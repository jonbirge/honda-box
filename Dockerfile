# this is an official Python runtime
FROM python:3.7-slim

# set the working directory in the container to /app
WORKDIR /app

# copy requirements file
COPY reqs.txt /app/reqs.txt

# install python packages
RUN pip install --trusted-host pypi.python.org -r reqs.txt

# add the current directory to the container as /app
COPY . /app

# move static content
RUN mkdir /data
RUN mv default /data/static

# unblock port 80 for the Flask app
EXPOSE 80

# execute the Flask app
CMD ["python", "app.py"]
