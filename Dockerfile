#docker build -t test-python .
FROM python:3.11.5 

# 安裝微軟ODBC驅動前的依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    gnupg2 \
    gnupg1 \
    curl

# 添加Microsoft的key和repo
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

# 更新源並安裝ODBC Driver 17
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    msodbcsql17

# 清理不需要的文件
RUN apt-get clean && rm -rf /var/lib/apt/lists/*



# 安裝 libgl1-mesa-glx 以解決 libGL.so.1 相關的問題 # 給opencv 的解決方案
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*


# 設置容器內的工作目錄
WORKDIR /app

# 將當前目錄下的所有文件複製到容器中的/app目錄
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./app.py"]