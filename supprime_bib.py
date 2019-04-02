#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import json
import re
import requests
from mail import mail
from Alma_Apis_Interface import Alma_Apis
import time

def get_job_parameters(file_name):
    dossier = os.path.dirname(os.path.abspath(__file__))
    file_name = dossier + '/' + file_name
    with open(file_name, 'r',encoding='utf-8') as file:
        job_parameters = json.load(file)
    return job_parameters

def get_job(job_id,instance_id):
    #Interroge un job toutes les 2 minutes et retourne le rapport quand ce dernier est terminé
    detail_service = api.get_job_instances(job_id,instance_id)
    statut = detail_service['status']['value']
    print(statut)
    if statut=='RUNNING' or statut=='INITIALIZING':
        progression=detail_service['progress']
        print("\tTraitement en cours déxecution ({}%)".format(progression))
        time.sleep(120)
        get_job(job_id,instance_id)
    elif statut == 'COMPLETED_SUCCESS':
        return detail_service
    else:
        raise Exception("Statut du job inconnu !") 

def post_job(job_id,job_parameters):
    #Lance un job et retourne l'id de l'instance
    job_reponse = api.post_job(job_id,json.dumps(job_parameters))
    #Récupère l'identifiant du service
    job_service = (job_reponse['additional_info']['link'])
    a = re.search("jobs\/(.*?)\/instances\/(.*)",job_service)
    job_instance_id = a.group(2)
    return job_instance_id

# Initilalisation des paramétres 
null=None
api = Alma_Apis.Alma(apikey=os.getenv('TEST_NETWORK_API'), region='EU', service='Delete_Bib')

#On lance le job qui permet d'identifier depuis la NZ les notices sans inventaires
identifie_bib_job_id='M58'
identifie_bib_job_parameters = get_job_parameters('Identifie_notices_Job_Paramater.json')
identifie_bib_job_instance_id = post_job(identifie_bib_job_id,identifie_bib_job_parameters)
# identifie_bib_job_instance_id='2988022360004671'
print('Identifiant de l''instance du job M58 : {}'.format(identifie_bib_job_instance_id))

#On attend la fin du job et on récupère le nom du set qui a été créé
time.sleep(120)
identifie_bib_job_rapport = get_job(identifie_bib_job_id,identifie_bib_job_instance_id)

set_name = identifie_bib_job_rapport['counter'][0]['value']
print('Nom du set des notices à supprimer : {}'.format(set_name))

#On récupère l'identifiant du set
search_set_id = api.get_set_id(set_name)
print('Identifiant du set des notices à supprimer : {}'.format(search_set_id))

#On lance la suppression des notices du set
suppr_bib_job_id='M28'
suppr_bib_job_parameters = get_job_parameters('Supprime_notices_Job_Paramater.json')
suppr_bib_job_parameters['parameter'][2]['value'] = search_set_id
suppr_bib_job_instance_id = post_job(suppr_bib_job_id,suppr_bib_job_parameters)
# suppr_bib_job_instance_id = '2988077480004671'
print('Identifiant de l''instance du job M28 : {}'.format(suppr_bib_job_instance_id))

#On attend la fin du job et on récupère le nombre de notices supprimées
time.sleep(120)
suppr_bib_job_rapport = get_job(suppr_bib_job_id,suppr_bib_job_instance_id)

print(suppr_bib_job_rapport['counter'][0]['value'])
text = '''Service Delete_Bib terminé avec succès.
    * {} notice(s) supprimée(s)
    * {} notice(s) non supprimée(s) car liées à un inventaire
    * {} notice(s) non supprimée(s) car liées à une commande
    * {} notice(s) non supprimée(s) car liées à d'autres notices\
'''.format(suppr_bib_job_rapport['counter'][0]['value'],
        suppr_bib_job_rapport['counter'][1]['value'],
        suppr_bib_job_rapport['counter'][2]['value'],
        suppr_bib_job_rapport['counter'][3]['value'])
message = mail.Mail()
statut = message.envoie(os.getenv('ADMIN_MAIL'), os.getenv('ADMIN_MAIL'), 'Delete_bib Succés', text)
print(statut)
print(text)