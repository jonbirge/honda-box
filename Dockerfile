# this is an official Python runtime
FROM python:3.7-slim

# set the working directory in the container to /app
WORKDIR /app

# add the current directory to the container as /app
ADD . /app

# execute pip
RUN pip install --trusted-host pypi.python.org -r reqs.txt

# unblock port 80 for the Flask app
EXPOSE 80

# execute the Flask app
CMD ["python", "app.py"]
