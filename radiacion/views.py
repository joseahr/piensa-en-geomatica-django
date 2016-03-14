# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.files import File

from radiacion.models import Document
from radiacion.forms import DocumentForm

from piensa_en_geomatica import settings

from pyGeo.Topografia import Radiacion3D, Azimut
from pyGeo.Geometrias import Punto3D, Punto2D, Angulo
from pyGeo.Ficheros import SHPWriter

from datetime import datetime

from os import path
from io import StringIO

import os

import random
import zipfile

def radiacion(request):
    #Document.objects.all().delete()
    def parseCSV(csv, name):
        #Document.objects.all().delete()
        indexEstaciones = -1
        indexReferencias = -1
        indexObservaciones = -1
        for index, linea in enumerate(csv):
            if 'ESTACIONES' in linea.decode('utf-8'):
                if indexEstaciones != -1:
                    indexEstaciones = -1
                    break
                indexEstaciones = index
            if 'REFERENCIAS' in linea.decode('utf-8'):
                if indexReferencias != -1:
                    indexReferencias = -1
                    break
                indexReferencias = index
            if 'OBSERVACIONES' in linea.decode('utf-8'):
                if indexObservaciones != -1:
                    indexObservaciones = -1
                    break
                indexObservaciones = index
        if indexObservaciones == -1 or indexEstaciones == -1 or indexReferencias == -1:
            return []
        indices = [indexEstaciones, indexReferencias, indexObservaciones]
        indices.sort()
        print(indices)
        try:
            indexEstaciones = [indexEstaciones + 1, indices[indices.index(indexEstaciones) + 1]]
        except:
            if indices.index(indexEstaciones) == len(indices) -1:
                indexEstaciones = [indexEstaciones + 1, len(csv)]
        try:
            indexReferencias = [indexReferencias + 1, indices[indices.index(indexReferencias) + 1]]
        except:
            if indices.index(indexReferencias) == len(indices) -1:
                indexReferencias = [indexReferencias + 1, len(csv)]
        try:
            indexObservaciones = [indexObservaciones + 1, indices[indices.index(indexObservaciones) + 1]]
        except:
            if indices.index(indexObservaciones) == len(indices) -1:
                indexObservaciones = [indexObservaciones + 1, len(csv)]
        estaciones = csv[indexEstaciones[0] : indexEstaciones[1]]
        referencias = csv[indexReferencias[0] : indexReferencias[1]]
        observaciones = csv[indexObservaciones[0] : indexObservaciones[1]]
        print(indexEstaciones, indexReferencias, indexObservaciones)
        #print (estaciones, referencias, observaciones)
        print(settings.UPLOAD_DIR + name.split('.')[0] + '.shp')
        shpWriter = SHPWriter.SHPWriter(settings.UPLOAD_DIR + name.split('.')[0] + '.shp')

        f = open(settings.UPLOAD_DIR + name.split('.')[0] + '.txt', 'w+')

        #print(type(f))

        for index__, est in enumerate(estaciones):
            print('estacion')

            hayReferencia = False
            est = est.decode('utf-8').strip().split(',')
            est = tuple([x for x in est if x])

            print (est)
            try:
                id_est, i_est, x_est, y_est, z_est  = est
                f.write('ESTACIÓN ' + id_est + '\n')
                f.write('---------------------------------' + '\n')
            except:
                return ''

            # Punto Estación
            p_est = Punto3D.Punto3D(float(x_est), float(y_est), float(z_est))

            shpWriter.addPunto(p_est, id_est)
            # Objeto Radiación 3D
            radiacion = Radiacion3D.Radiacion3D(p_est, 0, Angulo.Angulo(0, formato='centesimal'), Angulo.Angulo(0, formato='centesimal'))
            
            des_media = []
            
            azimut = Azimut.Azimut()
            azimut.setPuntoInicial(p_est)
            
            for index,ref in enumerate(referencias):

                ref = ref.decode('utf-8').strip().split(',')
                ref = tuple([x for x in ref if x])

                try:
                    id_ref, id_est_ref, x_ref, y_ref, lh_ref_ = ref
                except:
                    return []
                # Comprobamos que la referencia pertenece a la estación
                if id_est != id_est_ref and index != len(referencias) - 1:
                    continue
                elif id_est == id_est_ref:
                    hayReferencia = True

                    p_ref = Punto2D.Punto2D(float(x_ref), float(y_ref))

                    shpWriter.addPunto(p_ref, id_ref)

                    azimut.setPuntoFinal(p_ref)
                    lh_ref = Angulo.Angulo(float(lh_ref_), formato = 'centesimal')

                    lh_cent = Angulo.Angulo(float(lh_ref_), formato = 'centesimal')

                    lh_ref.Convertir('radian')
                    #print('azimut')
                    #print(azimut.getAzimut())
                    #print('LH')
                    #print(lh_ref)
                    #print('desorientacion')


                    azi_cent = Angulo.Angulo(float(azimut.getAzimut()), formato = 'radian')
                    azi_cent.Convertir('centesimal')
                    
                    #print('LH CENT')
                    #print(lh_cent.getAngulo())
                    #print('AZI CENT')
                    #print(azi_cent.getAngulo())

                    deso = azimut.getAzimut() - lh_ref.getAngulo()
                    #print('DESO_CENT')
                    deso_cent = Angulo.Angulo(float(deso), formato = 'radian')
                    deso_cent.Convertir('centesimal')
                    #print(deso_cent.getAngulo())

                    #print(deso)
                    des_media.append(deso)
                # Si hemos llegado al final de la lista referencias
                # Calculamos la radiación con las lecturas a los puntos visados
                # y la desorientación media que sacamos de visar las referencias
                if index == len(referencias) - 1:
                    if not hayReferencia:
                        return ''
                    des_media = sum(des_media) / float(len(des_media))
                    des_media_centesimal = Angulo.Angulo(des_media, formato='radian')
                    des_media_centesimal.Convertir('centesimal')

                    f.write('DESORIENTACIÓN MEDIA : ' + str(des_media_centesimal.getAngulo()) + '\n')
                    f.write('----------------------------------' + '\n')
                    f.write('RESULTADOS : ' + '\n')
                    f.write('----------------------------------' + '\n')
                    f.write('ID_PUNTO         X           Y           Z' + '\n')
                    f.write('---------------------------------------------------' + '\n')

                    print(des_media)
                    hayObsrvaciones = False
                    for index_, obs in enumerate(observaciones):
                        obs = obs.decode('utf-8').strip().split(',')
                        obs = tuple([x for x in obs if x])
                        print('observacion')
                        print(obs)
                        try:
                            id_est_obs, id_obs, lh, lv, dg, m = obs
                        except:
                            return ''
                        if id_est_obs != id_est and index != len(observaciones) - 1:
                            continue
                        elif id_est_obs == id_est:
                            lh = Angulo.Angulo(float(lh), formato = 'centesimal')
                            lh.Convertir('radian')

                            az = Angulo.Angulo(lh.getAngulo() + des_media, formato = 'radian')
                            az.Convertir('centesimal')

                            hayObsrvaciones = True
                            radiacion.setDistancia(float(dg))
                            radiacion.setAzimut(az)
                            radiacion.setAnguloVertical(Angulo.Angulo(float(lv), formato = 'centesimal'))
                            radiacion.setAlturaInstrumento(float(i_est))
                            radiacion.setAlturaMira(float(m))

                            p3 = radiacion.Radiacion3D()

                            shpWriter.addPunto(p3, id_obs)

                            f.write(id_obs + '    ' + str(p3.getX()) + ' ; ' + str(p3.getY()) + ' ; ' + str(p3.getZ()) + '\n')

                            print('SOL RADIACION')
                            print(str(p3.getX()) + ' ; ' + str(p3.getY()) + ' ; ' + str(p3.getZ()))
                        if index_ == len(observaciones) - 1 and index__ == len(estaciones) - 1:
                            if hayObsrvaciones:
                                a = shpWriter.save()
                                archivos_shp = [a.split('.')[0] + '.shp', a.split('.')[0] + '.dbf', a.split('.')[0] + '.shx']
                                zip = zipfile.ZipFile(settings.UPLOAD_DIR + name.split('.')[0] + '.zip', 'w', zipfile.ZIP_DEFLATED)
                                for fich in archivos_shp:
                                    zip.write(settings.UPLOAD_DIR + path.basename(fich), path.basename(fich), compress_type=zipfile.ZIP_DEFLATED)
                                    os.remove(settings.UPLOAD_DIR + path.basename(fich))
                                zip.close()
                                os.remove(settings.UPLOAD_DIR + path.basename(fich).split('.')[0] + '.txt')
                                print('SHP')
                                print(a)
                                return (File(f), '/media/radiaciones/' + name.split('.')[0] + '.zip')
                            else:
                                return ''

    # Manejar subida del fichero
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            documents = Document.objects.all()
            # Creamos un archivo a partir del que nos envían
            f_ = File(request.FILES['docfile'])
            ext = path.splitext(f_.name)
            ext = ext[len(ext) - 1]

            if '.csv' != ext:
                print(ext)
                return render_to_response(
                    'radiacion/radiacion.html',
                    {'form': form, 'error' : 'El fichero debe de tener formato CSV', 'documents' : documents},
                    context_instance=RequestContext(request)
                )
            # Lo abrimos en modo lectura
            f_.open(mode='r')
            # Almacenamos el contenido en una variable
            contenido = f_.readlines()
            #f_.close()
            #print(contenido)
            nombre_random = str(random.getrandbits(100)) + '_' + f_.name
            print(nombre_random)
            resultado = parseCSV(contenido, nombre_random)
            if resultado:
                #convertir fichero a SHP, crear modelo, guardar base de datos, mostrar lista al usuario
                print('resultado')
                print(resultado)
                result_file, result_shp = resultado
                solucion_files = Document(docfile = result_file, shp = result_shp, nombre_original = f_.name)
                solucion_files.save()
                pass
            # TODO: Comprobar que el archivo es CSV y calcular la radiación

            # Redirect to the document list after POST
            #return HttpResponseRedirect(reverse('radiacion.views.radiacion'))
    else:
        form = DocumentForm() # A empty, unbound form
    documents = Document.objects.all()
    # Render list page with the documents and the form
    return render_to_response(
        'radiacion/radiacion.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )