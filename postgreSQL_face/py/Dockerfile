FROM python:3.6-slim-stretch

WORKDIR ./py
 
ADD . .


RUN sed -i 's/deb.debian.org/mirrors.tencent.com/' /etc/apt/sources.list &&  sed -i 's/security.debian.org/mirrors.ustc.edu.cn/' /etc/apt/sources.list 
RUN apt-get clean  && apt-get update 
RUN apt-get install -y --fix-missing  \
    build-essential \
    cmake \	
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    libpq-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    python-psycopg2 \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*	


RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.9' --single-branch https://github.com.cnpmjs.org/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS

RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt


CMD ["sh","-x", "./GPU.sh"]
CMD ["python3", "./src/facehttp.py"]
