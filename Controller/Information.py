from flask import (Blueprint,
                   render_template,redirect,
                   send_from_directory,request,
                   url_for,current_app
                   )
import Services.CallSql as CallSql
import os


InformationBP = Blueprint('Information', __name__)

#紀錄首頁
@InformationBP.route("/")
def getRecords():
    records=CallSql.SelectALL()
    return render_template("records.html",records=records)


#記錄 查看 編輯
@InformationBP.route('/detail/<id>' ,methods=['GET','POST'])
def detail(id):
    if request.method == 'GET':
        detail=CallSql.SelectOne(id)
        return render_template("detail.html",detail=detail)
    if request.method == 'POST':
        name = request.form.get('name')
        opration = request.form.get('opration')
        type=request.form.get('type')
        CallSql.DataUpdate(name,opration,id,type)
        return redirect(url_for('Information.detail', id=id))
    

@InformationBP.route('/detailDelete/<id>/<path:imgpath>' ,methods=['POST'])
def detailDelete(id,imgpath):
    try:
        os.remove("./static/photo/saveData/"+imgpath)
        #print("照片已成功刪除")
    except OSError as e:
        print(f"刪除照片時出現錯誤: {e}")
    if CallSql.DataDelete(id):
        return redirect(url_for('Information.getRecords'))