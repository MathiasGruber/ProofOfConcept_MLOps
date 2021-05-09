FROM nanomathias/vscode-devcontainer:release-1.0.9

# Anaconda installing
RUN wget -nv \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

# Set path to conda
ENV PATH /root/miniconda3/bin:$PATH

# Install linters & formatters
# hadolint ignore=SC2102
RUN pip install --no-cache-dir \
    yapf==0.30.0 \
    pylint==2.5.3 \
    pylint_django==2.4.2 \
    pre-commit==2.10.0 \
    prospector[with_mypy]==1.3.1 \
    safety==1.10.3 \
    BentoML==0.12.1 \
    psycopg2-binary==2.8.6 \
    notebook==6.3.0 \
    ipywidgets==7.6.3 \
    seldon-core==1.7.0

# Setting the ENTRYPOINT to docker-init.sh will configure non-root access to
# the Docker socket if "overrideCommand": false is set in devcontainer.json.
# The script will also execute CMD if you need to alter startup behaviors.
ENTRYPOINT [ "/usr/local/share/docker-init.sh" ]
CMD [ "sleep", "infinity" ]