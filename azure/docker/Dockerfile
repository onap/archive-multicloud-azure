FROM python:2

ENV MSB_ADDR "127.0.0.1"
ENV MSB_PORT "80"
ENV AAI_ADDR "aai.api.simpledemo.openecomp.org"
ENV AAI_PORT "8443"
ENV AAI_SCHEMA_VERSION "v13"
ENV AAI_USERNAME "AAI"
ENV AAI_PASSWORD "AAI"
ENV MR_ADDR "127.0.0.1"
ENV MR_PORT "3904"

EXPOSE 9008

RUN apt-get update && \
    apt-get install -y unzip && \
    apt-get install -y curl && \
    apt-get install -y wget
RUN apt-get install -y python-dev gcc libffi-dev libssl-dev make

# ARIA orchestrator addition
RUN pip install -U pip setuptools
COPY /aria/ /tmp/
WORKDIR /tmp/aria-extension-cloudify/src/aria
RUN pip install .

WORKDIR /tmp/aria-extension-cloudify
RUN pip install .

WORKDIR /tmp/aria-rest-server/src/main/python/aria-rest
RUN pip install .

RUN pip install --force-reinstall  pip==9.0.1
WORKDIR /tmp
ADD docker/cloudify_azure_plugin-1.4.2-py27-none-linux_x86_64.wgn /tmp/
RUN aria plugins install cloudify_azure_plugin-1.4.2-py27-none-linux_x86_64.wgn
RUN rm cloudify_azure_plugin-1.4.2-py27-none-linux_x86_64.wgn

COPY /multicloud-azure.zip /opt/

RUN  cd /opt/ && \
#    wget -q -O multicloud-azure.zip 'https://nexus.onap.org/service/local/artifact/maven/redirect?r=snapshots&g=org.onap.multicloud.azure&a=multicloud-azure&v=LATEST&e=zip' && \
    unzip multicloud-azure.zip && \
    rm -rf multicloud-azure.zip && \
    pip install -r multicloud_azure/requirements.txt

WORKDIR /opt
RUN chmod +x multicloud_azure/docker/*.sh && chmod +x multicloud_azure/*.sh
ENTRYPOINT multicloud_azure/docker/docker-entrypoint.sh
