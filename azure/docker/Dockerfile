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

EXPOSE 9004

RUN apt-get update && \
    apt-get install -y unzip && \
    apt-get install -y curl && \
    apt-get install -y wget


RUN  cd /opt/ && \
    wget -q -O multicloud-azure.zip 'https://nexus.onap.org/service/local/artifact/maven/redirect?r=snapshots&g=org.onap.multicloud.openstack.vmware&a=multicloud-openstack-vmware&v=LATEST&e=zip' && \
    unzip multicloud-azure.zip && \
    rm -rf multicloud-azure.zip && \
    pip install -r azure/requirements.txt


WORKDIR /opt
ENTRYPOINT azure/docker/docker-entrypoint.sh
