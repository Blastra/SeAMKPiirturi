#!/usr/bin/env python3.5

#Visuaalisen käyttöliittymän tekeminen piirtolaitteelle -web-sovellus

#Toteutusalusta: Flask

#Kun ohjelma on valmis julkiseen verkkoon: flask run --host=0.0.0.0

from flask import Flask, request, redirect, url_for, render_template, send_from_directory, make_response
import webbrowser
from werkzeug.utils import secure_filename
import os
import subprocess
#import pygame
import sys



#os.getcwd()
#print(moduuliPolku)

#Huom. moduulia svg2gcode on muokattu moduulipolkujen ja
#tiedostopolkujen osalta soveltuvammaksi SeAMK:n ympäristöön
#import svg2gcode

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


#Määritellään Flask-applikaatio-objekti
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

#Valmistellaan funktio moduulipolkujen
#tarkistamista varten
def moduuliTarkistus(moduuliPolku):
    if moduuliPolku not in sys.path:
        sys.path.append(moduuliPolku)
        print("Moduulipolku "+str(moduuliPolku)+" lisätty")

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
            # Tarkistetaan, onko POST-pyynnössä mukana tiedosto
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # Käsitellään tapaus, jossa käyttäjä ei
            # anna tiedostoa
            if file.filename == '':                
                return 'Ei valittua tiedostoa'
            #Tarkistetaan, onko tiedosto sallittua tyyppiä
            if file and allowed_file(file.filename):                
                filename = secure_filename(file.filename)
                debug("filename: "+str(filename),"nimenTarkistus")
                #dump(file)
                savPath = os.path.join(piirt.config['UPLOAD_FOLDER'], filename)
                #Tallennetaan tiedosto paikallisesti määriteltyyn polkuun
                file.save(savPath)
                
                return redirect(url_for('uploaded_file',filepath=savPath, filename=filename))
        return render_template("FileSubmitPage.html")

@piirt.route('/static/upload/<filename>', methods=["GET","POST"])
def uploaded_file(filename):
    if request.method == "GET":
        #Tallennetaan svg-tiedoston nimi myöhempää käyttöä varten
        piirt.tiedNimi = filename
        return render_template("UploadedImg.html", filepath="/static/"+filename)

@piirt.route('/gengcode')
def gengcode():    

    #Tallennetaan muuttujaan polkurunko, joka johtaa ohjelman kansioon
    polkuRunko = os.path.split(__file__)[0]
    
    #Määritetään polku, josta löytyy muuntoskripti svg:stä g-koodiksi
    svgConvPath = os.path.join(os.path.join(polkuRunko, "SvgGCODEMuunnin","__init.py__"))

    #Määritellään polku, josta svg-kuvat löytyvät
    svgKuvaKansio = os.path.join(polkuRunko, "static")

    #Haetaan applikaatio-objektiin tallennettu tiedostonimi
    kohdeSVG = piirt.tiedNimi

    #Varastoidaan moduulipolut 
    moduuliPolut = []
    moduuliPolut.append(os.path.join(os.path.split(__file__)[0],"SvgGCODEMuunnin"))
    moduuliPolut.append(os.path.join(moduuliPolut[0],"lib"))

    #Lisätään moduulipolut sys.path-muuttujaan tarvittaessa
    for moduuliPolku in moduuliPolut:
        moduuliTarkistus(moduuliPolku)

    #Otetaan käyttöön svg:nmuuntomoduuli
    from svg2gcode import generate_gcode, test

    #Generoidaan G-koodi ja varastoidaan se tiedostoon
    generate_gcode(os.path.join(svgKuvaKansio, kohdeSVG))

    return "G-koodi generoitu palvelimella\n ja koneen valvojalle on lähetetty tulostuspyyntö"


piirt.run()




