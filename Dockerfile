FROM python:3.12

RUN pip install setuptools
COPY requirements.txt .
RUN pip install -r requirements.txt


ARG MULTIQC_VERSION=multiqctest
ARG MULTIQC_PLUGIN_VERSION=v2.0.0

LABEL author="SEGLH GSTT Bioinformatics Team" \
      description="MultiQC ${MULTIQC_VERSION} with SEGLH plugin" \
      maintainer="gstt.mokaguys@nhs.net"

# Install MultiQC
RUN git clone https://github.com/millardkieron/MultiQC.git --branch ${MULTIQC_VERSION} && \
    cd MultiQC && \
    pip install .

# Add plugin and install
COPY . multiqc_plugins
RUN cd multiqc_plugins && \
    pip install .


# uncomment this if the dockerfile is distributed outside of this repository 
#RUN git clone https://github.com/moka-guys/multiqc_plugins.git --branch main && \
#    cd multiqc_plugins && \
#    python setup.py install

RUN mkdir -p /data
WORKDIR /data

ENTRYPOINT [ "multiqc" ]
CMD [ "." ]
