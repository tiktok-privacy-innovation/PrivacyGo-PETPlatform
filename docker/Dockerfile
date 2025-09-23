FROM python:3.9-bullseye

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl zip unzip ca-certificates-java openjdk-11-jre-headless maven sqlite3 && \
    rm -rf /var/lib/apt/lists/* && \
    curl -s "https://get.sdkman.io" | bash && \
    bash -c "source /root/.sdkman/bin/sdkman-init.sh && sdk install java 8.0.392-tem"

ENV JAVA_HOME="/root/.sdkman/candidates/java/current"
ENV PATH="$JAVA_HOME/bin:$PATH"

COPY . /app/

RUN mv /app/src/* /app/ && \
    pip install --upgrade pip && \
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
USER petplatformuser 
ENTRYPOINT ["sh", "bootstrap.sh"]
