#Using python
FROM python:3.9-slim
# Using Layered approach for the installation of requirements
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
#Copy files to your container
COPY . ./
EXPOSE 8080
EXPOSE 80
#Running your APP and doing some PORT Forwarding
CMD gunicorn --chdir ./application -b 0.0.0.0:80 app:server