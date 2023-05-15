FROM python:3.10-slim
# set the working directory
WORKDIR /work

EXPOSE 9100
# install dependencies
COPY ./requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install pydantic[email]
RUN pip install python-multipart
RUN pip install psycopg2-binary



# copy the to the folder
COPY . ./

# start the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9100", "--reload"]
