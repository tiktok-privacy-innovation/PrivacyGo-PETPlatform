FROM python:3.9-bullseye

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates-java openjdk-11-jre-headless openjdk-8 maven && \
    rm -rf /var/lib/apt/lists/*

COPY . /app/

RUN mv /app/src/* /app/ && \
    pip install /app/external/*.whl && \
    pip install -r /app/requirements.txt && \
    pip install -r /app/PETSQL/requirements.txt && \
    pip install -r /app/PETML/requirements.txt && \
    rm -rf /root/.cache/pip

WORKDIR /app/PETML
RUN python3 setup.py install

WORKDIR /app/PETSQL/java
RUN mvn clean package && \
    mv target/petsql*.jar /app/PETSQL/petsql/compiler/__binding && \
    rm -rf target && \
    rm -rf .m2

WORKDIR /app/PETSQL
RUN python3 setup.py install

WORKDIR /app
RUN adduser --disabled-password --gecos '' petplatformuser
USER petplatformuser ENTRYPOINT ["sh", "bootstrap.sh"]
