#!/bin/bash
my_date=`date +%Y%m%d`
# my_script_rep="/home/scoopadmin/Workspace/Notices_sans_exemplaires/"
my_log_file=/var/tmp/Alma_script/supprime_bib_$my_date.log
python3 ./supprime_bib.py > $my_log_file
#perl /home/scoopadmin/Workspace/Transf_quality/test.pl 2> $my_log_file
if [ $? -ne 0 ]
	then echo -e "Bonjour,\n Le programme de suppression des notices sans exemplaires  s'est arrété sur un échec. Pour un savoir plus voir les logs sous $my_log_file" | mail -s "Supprime Notices sans exemplaires -- EREUR" alexandre.faure@u-bordeaux.fr
fi
exit 0