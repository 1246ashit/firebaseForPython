import pyodbc

conn_params = {
    "Driver": "ODBC Driver 17 for SQL Server",
    "Server": "localhost,1433",
    "Database": "HomeSafty",
    "UID": "sa",
    "PWD": "LikeAndSubscribe1!",
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
    for i in reportType:
        reportTypeStr=''+i+','    
    data=(reportTime,nameStr[:-1],photo_address,reportTypeStr)
    sql = "INSERT INTO records (time,name,photoLocation,type) VALUES ( ? ,? ,? ,?)"
    cursor.execute(sql,data)
    cursor.commit()
    # 關閉連接
    conn.close()
    print("儲存成功")

#確認 LINEID 是否有登入
def LineUserComfirm(userId):
    conn = pyodbc.connect(**conn_params)
    cursor = conn.cursor()
    sql = "SET NOCOUNT ON SELECT * FROM lineUserId WHERE userId = ?"
    cursor.execute(sql,userId)
    records = cursor.fetchall()
    cursor.commit()
    # 關閉連接
    conn.close()
    if len(records)!= 0:
        print("確認為使用者")
        return True
    else:
        print("查無此人")
        return False

#USER註冊
def registUser(userId):
    conn = pyodbc.connect(**conn_params)
    cursor = conn.cursor()
    sql = "INSERT INTO lineUserId  (userId) VALUES ( ? )"
    data=(userId)
    cursor.execute(sql,data)
    cursor.commit()
    # 關閉連接
    conn.close()
    print("登入完成")
    return True

#取得所有使用者
def fatchAllUser():
    conn = pyodbc.connect(**conn_params)
    cursor = conn.cursor()
    sql = "SELECT userId FROM lineUserId "
    cursor.execute(sql)
    userIds = cursor.fetchall()
    cursor.commit()
    # 關閉連接
    conn.close()
    return userIds

#取得所有臉
def GetAllFace():
    conn=pyodbc.connect(**conn_params)
    cursor=conn.cursor()
    cursor.execute('SET NOCOUNT ON SELECT id,name,photo FROM face')
    records = cursor.fetchall()
    return records

#新增臉
def Addface(name,photo):
    conn = pyodbc.connect(**conn_params)
    cursor = conn.cursor()
    sql = "INSERT INTO face  (name,photo) VALUES ( ?,? )"
    data=(name,photo)
    cursor.execute(sql,data)
    cursor.commit()
    # 關閉連接
    conn.close()
    return True

#刪除臉
def Deleteface(id):
    conn = pyodbc.connect(**conn_params)
    cursor = conn.cursor()
    sql = "DELETE FROM face WHERE id = ?;"
    data=(id)
    cursor.execute(sql,data)
    cursor.commit()
    # 關閉連接
    conn.close()
    return True


#名子中文
def GetName():
    conn=pyodbc.connect(**conn_params)
    cursor=conn.cursor()
    cursor.execute('SET NOCOUNT ON SELECT name,photo FROM face')
    records = cursor.fetchall()
     # 將每條記錄轉換成字典的一部分
    return {photo: name for name, photo in records}



