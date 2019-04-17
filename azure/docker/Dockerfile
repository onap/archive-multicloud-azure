FROM python:2-alpine

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

RUN apk update && \
    apk add unzip curl wget git python-dev gcc libffi-dev openssl-dev make libc-dev

RUN addgroup -S onap && adduser -S -G onap onap
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

RUN git clone -b 1.4.2 https://github.com/cloudify-incubator/cloudify-azure-plugin

RUN sed -i "s/utils.get_resource_config(_ctx=ipc)/{'properties': utils.get_resource_config(_ctx=ipc)}/g" cloudify-azure-plugin/cloudify_azure/resources/network/ipconfiguration.py

RUN wagon create ./cloudify-azure-plugin

RUN aria plugins install cloudify_azure_plugin-1.4.2-py27-none-linux_x86_64.wgn
RUN rm cloudify_azure_plugin-1.4.2-py27-none-linux_x86_64.wgn
#RUN rm -rf cloudify-azure-plugin


RUN  cd /opt/ && \
    wget -q -O multicloud-azure.zip 'https://nexus.onap.org/service/local/artifact/maven/redirect?r=snapshots&g=org.onap.multicloud.azure&a=multicloud-azure&v=LATEST&e=zip' && \
    unzip multicloud-azure.zip && \
    rm -rf multicloud-azure.zip && \
    pip install -r multicloud_azure/requirements.txt && \
    chown onap:onap /opt/multicloud_azure -R

RUN mkdir -p /home/onap && chown onap:onap /home/onap -R

WORKDIR /opt
RUN chmod +x multicloud_azure/docker/*.sh && chmod +x multicloud_azure/*.sh
USER onap
ENTRYPOINT multicloud_azure/docker/docker-entrypoint.sh
