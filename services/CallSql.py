import pyodbc

conn_params = {
    "Driver": "SQL Server",
    "Server": "MSI",
    "Database": "HomeSafty",
    "UID": "sa",
    "PWD": "123456",
}


def SelectALL():
    conn=pyodbc.connect(**conn_params)
    cursor=conn.cursor()
    cursor.execute('SET NOCOUNT ON SELECT * FROM records ORDER BY time DESC')
    records = cursor.fetchall()
    return records

def SelectOne(id):
    conn=pyodbc.connect(**conn_params)
    cursor=conn.cursor()
    cursor.execute("SET NOCOUNT ON SELECT * FROM records WHERE id= ?", id)
    detail = cursor.fetchone()
    return detail

def DataUpdate(name,opration,id,type):
    conn=pyodbc.connect(**conn_params)
    cursor=conn.cursor()
    sql = "UPDATE records SET "
    if name=='' and opration=='':
        return False
    if name!='':
        sql += "name = '%s' , " % name
    if opration!='':
        sql += "detail = '%s' , " % opration
    if type!='':
        sql += "type = '%s' , " % type
        # 去除最後一個逗號和空格
    sql = sql[:-2]
    sql += " WHERE id = '%s'" % id
    cursor.execute(sql)
    conn.commit()
    conn.close()
    return True

def DataDelete(id):
    conn = pyodbc.connect(**conn_params)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records WHERE id = ?", id)
    conn.commit()
    conn.close()
    return True


def SaveInSql(reportTime,names,photo_address,reportType):
    conn = pyodbc.connect(**conn_params)
    cursor = conn.cursor()
    nameStr=''
    for i in names:
        nameStr=''+i+','
    data=(reportTime,nameStr[:-1],photo_address,reportType)
    sql = "INSERT INTO records (time,name,photoLocation,type) VALUES ( ? ,? ,? ,?)"
    cursor.execute(sql,data)
    cursor.commit()
    # 關閉連接
    conn.close()
    print("儲存成功")
