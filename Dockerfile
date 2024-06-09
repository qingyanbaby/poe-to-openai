FROM python:3.11-slim-bookworm

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt --no-cache-dir

ENV TZ Asia/Shanghai

COPY . /app

VOLUME /root/.cache

VOLUME /var/log/openai

RUN chmod +x /app/run.sh

EXPOSE 39527

CMD /app/run.sh
