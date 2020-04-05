# encoding=utf-8
from flask import Flask, request,jsonify,session
from flask_uploads import UploadSet, configure_uploads
from flask import render_template
import os
import numpy as np
from PIL import Image
from imgseg.Seg import seg
from trans import transtool

app = Flask(__name__)

app.config['UPLOAD_PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)),"files")
app.config['UPLOADS_DEFAULT_DEST'] = os.path.dirname(os.path.abspath(__file__))
uploaded_photos = UploadSet()
configure_uploads(app, uploaded_photos)

@app.route('/')
def index():
    return render_template('imageseg.html')

handling_filename=None
@app.route('/upload', methods=['POST'])
def flask_upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'code': -1, 'filename': '', 'msg': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'code': -1, 'filename': '', 'msg': 'No selected file'})
        else:
            try:
                global handling_filename
                handling_filename = uploaded_photos.save(file)
                return jsonify({'code': 0, 'filename': handling_filename, 'msg': uploaded_photos.url(handling_filename)})
            except Exception as e:
                return jsonify({'code': -1, 'filename': '', 'msg': 'Error occurred'})

@app.route('/files', methods=['GET'])
def show_photo():
    if request.method == 'GET':
        global handling_filename
        img=Image.open(os.path.join(app.config['UPLOAD_PATH'],handling_filename))
        img=img.resize((200,200))
        img.save(os.path.join(app.config['UPLOAD_PATH'],'test'+handling_filename))
        img_str = transtool().img2base64(img)
        return jsonify({'code': 200, 'img64': img_str})

myseg = seg()

@app.route('/seg', methods=['POST','GET'])
def colorizer():
    if request.method=='POST':
        global handling_filename
        npimg=np.array(Image.open(os.path.join(app.config['UPLOAD_PATH'],'test'+handling_filename))).astype(np.float32)
        imgbase64 =request.values.get('image').split(",")[1]
        left=float(request.values.get('left'))
        right=float(request.values.get('right'))
        up=float(request.values.get('up'))
        down=float(request.values.get('down'))
        mark= transtool().base64_to_rgb(imgbase64)
        
        mark=np.array(mark)
        markforcut=np.zeros(mark.shape[:2])
        
        markforcut[int(up)-1:int(down)+2,int(left)-1:int(right)+2]=myseg.P_fgd

        mark[int(up)-1:int(up)+2,:]=0
        mark[int(down) - 1:int(down) + 2, :] = 0
        mark[:,int(left)-1:int(left)+2]=0
        mark[:,int(right)-1:int(right)+2] = 0

        markforcut[np.where(mark[:, :, 0]>200)] = myseg.GT_fgd
        markforcut[np.where(mark[:, :, 1]>200)] = myseg.GT_bgd

        retimg=myseg(1,npimg,markforcut)
        img_str = transtool().img2base64(retimg)
        return jsonify({'code': 200, 'img64': img_str})

    if request.method=='GET':
        return jsonify({'code': 0, 'progress': 0})

if __name__ == '__main__':
#    app.debug = True
    app.run( host="0.0.0.0", port=3030, threaded=True)