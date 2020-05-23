from flask import Flask,flash,render_template,request,redirect,url_for
from PIL import ImageTk, Image
from flask_nav import Nav
from flask_nav.elements import Navbar,Subgroup,View,Link,Text,Separator
import math
import os
import requests
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS ={'bmp'}
#flask link part 
app = Flask(__name__)
nav=Nav(app)
Bootstrap(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

nav.register_element('my_navbar',Navbar(
    
    View('Home', 'index'),
    View('Encrypt','encryptselect'),
    View('Decrypt','decuploadpage')
    ));



# Only works with PNG images due to JPG compression issues messing up the message
#script part 
def encodeMessage(image, message,name):
     # img.show()
    imgcpy = image.copy()
    
    if len(message) == 0:
        raise Exception("Data is empty")
    message += " /// "
    mess8bit = To8bitBin(message)
    '''
    i = int(input("please enter the x coordinate of the starting pixel: "))
    j = int(input("please enter the y coordinate of the starting pixel: "))
    if i == "":
        i = 0
    if j == "":
        j = 0
    '''
    i = 0
    j = 0
    getPixEncode(mess8bit, imgcpy, name, j, i)
    print("Encryption Complete!")
    img = Image.open("new" + name[:-3] + "bmp")
    # img.show()


def To8bitBin(mess):
    binmess = []
    for i in mess:
        binmess.append(format(ord(i), '08b'))
    return binmess


'''
Encodes the picture with the message
Algorithm:
    1: each pixel it switches which value it manipulates
        first the R value
        second the G value
        third the B value
        repeat
    2: Uses two least significant bits to encode the message two bytes at a time
'''


def getPixEncode(mess8bit, img, name, i=0, j=0):
    pixelmap = img.load()
    rgb = 0
    for k in mess8bit:
        l = 0
        while l < 8:
            pixel = pixelmap[i, j]
            # print("pixelmap1:",pixelmap[i,j])
            # print("pixel:",pixel)
            p = str(format(int(pixel[rgb]), '08b'))    #08 formats the number to eight digits zero-padded on the left and 'b' converts to binary
            # print("p:",p)
            newpix = p[0:6] + k[l:l + 2]
            # print("newpix1:", newpix)
            l += 2
            newpix = int(newpix, 2)
            # print("newpix2:",newpix)
            if rgb == 0:   #insert to the red part
                pixelmap[i, j] = (newpix, int(pixel[1]), int(pixel[2]))   
            elif rgb == 1:              #insert to the green part 
                pixelmap[i, j] = (int(pixel[0]), newpix, int(pixel[2]))
            else:                  #insert to the blue part
                pixelmap[i, j] = (int(pixel[0]), int(pixel[1]), newpix)
            # print("pixelmap2:",pixelmap[i,j])   
          #looping conditions for the pixel array's iterator (rgb)
            if rgb == 2:
                rgb = 0
            else:
                rgb += 1
            j += 1
            if j == img.size[1]:
                j = 0
                i += 1

    img.save("new" + name[:-3] + "bmp")
    
    return render_template('encresult.html',te=img.show())


def decodeMessage(img):
    i=0
    j=0
   
    # img = Image.open(name)
    # img.show()
    st = getPixDecode(img, i, j)
    return(st[0:len(st) - 5])


def getPixDecode(img, i=0, j=0):
    pixelmap = img.load()
    rgb = 0
    f = 1
    temp = ""
    st = ""
    while i < img.size[0]:
        # print("i: ", i)
        while j < img.size[1]:
            pixel = pixelmap[i, j]
            # print("pixel:",pixel)
            p = str(format(int(pixel[rgb]), '08b'))
            # print("p:",p)
            rgb += 1
            temp += p[6:8]
            # print("temp:",temp)
            if rgb == 3:
                rgb = 0
            if f == 4:
                num = int(temp, 2)
                # print("num:",num)
                ch = chr(num)
                # print("ch:",ch)
                st = st + ch
                # print("st: ",st[-1:])
                f = 0
                temp = ""
                num = check(st)
                if num == 1:
                    return st
            f += 1
            j += 1
        j = 0
        i += 1

    return "***NO HIDDEN MESSAGE PRESENT***     "


def check(s):
    # print s
    if s[len(s) - 5:len(s)] == " /// ":
        return 1
    else:
        return 0


#landing page 
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/btnclicke',methods=['GET','POST'])
def encryptselect():
    return render_template('home.html')
    
@app.route('/send', methods=['GET','POST'])
def formdata():
   if request.method=='POST':
       text=request.form['hidetext']
       f= request.files['file']
       f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
       encodeMessage(Image.open(f,mode='r'), text, f.filename)
       return render_template('encresult.html')
@app.route('/btnclickd', methods=['GET','POST'])
def decuploadpage():
    return render_template('filedecrypt.html')
@app.route('/decupload',methods=['GET','POST'])
def decryptimg():
    im=request.files['file']
    decodemsg=decodeMessage(Image.open(im,mode='r'))
    text=decodemsg
    
    return render_template('text.html',text=text)

if __name__== '__main__':

    app.run(debug=True)
