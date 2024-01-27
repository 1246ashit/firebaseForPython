
from flask import (Blueprint,
                   render_template,redirect,
                   send_from_directory,request,
                   url_for,current_app
                   )
import Services.CallSql as CallSql
import os


settings_blueprint = Blueprint('Settings', __name__)
namedic=CallSql.GetName()

#設定畫面
@settings_blueprint.route('/', methods=['GET'])
def Settings():
    faces=CallSql.GetAllFace()
    return render_template('setting.html',faces=faces)


#加入人像
@settings_blueprint.route('/AddFace', methods=['POST'])
def AddFace():
    global namedic
    file = request.files['faceImage']
    name = request.form.get('name')
    if file.filename !="" and name!="":
        file.save(os.path.join(current_app.config['FACE_LOCATION'], file.filename))
        CallSql.Addface(name,file.filename)
        namedic=CallSql.GetName()
        try:
            os.remove(r"function\faceData\representations_facenet512.pkl")
        except FileNotFoundError:
            pass
    return redirect(url_for('Settings.Settings'))


#給前端圖像
@settings_blueprint.route('/FaceData/<filename>')
def FaceData(filename):
    return send_from_directory(current_app.config['FACE_LOCATION'], filename)

#delete人像
@settings_blueprint.route('/DeleteFace/<id>/<photo>', methods=['POST'])
def DeleteFace(id,photo):
    global namedic
    if CallSql.Deleteface(id) :
        os.remove(current_app.config['FACE_LOCATION']+"/"+ photo)
        namedic=CallSql.GetName()
        try:
            os.remove(r"function\faceData\representations_facenet512.pkl")
        except FileNotFoundError:
            pass
    return redirect(url_for('Settings.Settings'))