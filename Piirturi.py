

#Visuaalisen käyttöliittymän tekeminen piirtolaitteelle -web-sovellus

#Toteutusalusta: Flask

#Kun ohjelma on valmis julkiseen verkkoon: flask run --host=0.0.0.0

from flask import Flask, request, redirect, url_for, render_template, send_from_directory, make_response
import webbrowser
from werkzeug.utils import secure_filename
import os

#Debug-kategorioita voi kääntää päälle ja pois
#tarpeen mukaan

debugCategories = []

#debugCategories.append("palvelinSisalto")
debugCategories.append("tiedostonLahetys")
debugCategories.append("nimenTarkistus")

#Määritellään aluksi, ollaanko julkisessa verkossa,
#(esimerkiksi debug-toiminnot eivät ole tietoturvallisia)

def debug(msg, cat):
    if cat in debugCategories:
        print("DEBUG: "+str(msg))



piirt = Flask(__name__)

online = True

debug("Palvelimen sisältö: "+str(dir(piirt)),"palvelinSisalto")

#HUOM! Muista kääntää flaskin debug pois päältä,
#kun siirrytään julkiseen verkkoon

julkisessaVerkossa = False

if julkisessaVerkossa == False:
    piirt.debug = True

#Varastoidaan tämän skriptitiedoston polku
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

#Määritellään kansio, jonne verkon kautta
#palvelimelle kopioidut tiedostot tallennetaan

tallennusKansio = os.path.join(APP_ROOT, "static")

piirt.config["UPLOAD_FOLDER"] = tallennusKansio


#Rajataan tallennus vain tietyille tiedostotyypeille

sallitutTiedostoTyypit = set(["svg"])


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in sallitutTiedostoTyypit

@piirt.route("/profile/<name>")
def profile(name):
    
    return render_template("TestiTervehdysKuva.html", name=name)

def allowed_file(filename):
    debug("sallitutTiedostoTyypit: "+str(sallitutTiedostoTyypit),"nimenTarkistus")
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in sallitutTiedostoTyypit

@piirt.route("/", methods=['GET', 'POST'])
def upload_file():
    if online == True:
        debug("Server reacted","tiedostonLahetys")
        if request.method == 'POST':
            debug("Post received, request.files == "+str(request.files),"tiedostonLahetys")
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                debug("filename: "+str(filename),"nimenTarkistus")
                #dump(file)
                savPath = os.path.join(piirt.config['UPLOAD_FOLDER'], filename)
                file.save(savPath)
                
                return redirect(url_for('uploaded_file',filename=filename))
        return '''
    <!doctype html>
    <title>Piirturin etäohjaus</title>
    <h1>Anna piirturille svg-tiedosto</h1>
    <form method=post enctype=multipart/form-data>
    <p><input type=file name=file>
    <input type=submit value=Upload>
    </form>
    '''

@piirt.route('/static/upload/<filename>')
def uploaded_file(filename):
    return render_template("UploadedImg.html", filename="/static/"+filename)

piirt.run()


"""
@piirt.route("/")
def index():
    pass


@piirt.route("/login")
def login():
    pass



@piirt.route("/user/<username>")
def profile(username):
    pass

#with piirt.test_request_context():
#    print(url_for('index'))
#    print(url_for('login'))
#    print(url_for('login', next='/'))
#    print(url_for('profile', username='John Doe'))

piirt.run()


kertyma = "Moro"

piirt = Flask(__name__)

@piirt.route("/")
def ohai(kertyma):
    kertyma += "ror"
    return kertyma

    with piirt.test_request_context("/hello", method="POST"):


        assert request.path == "/hello"
        assert request.method == "POST"
                                
    


#name = "Kalmari"

piirt.run()
"""
