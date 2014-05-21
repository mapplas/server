# -*- encoding: utf-8 -*-
import os, re, sys, psycopg2, datetime, logging
import nltk
from emaily import notice_email
import nlp_extractor_helper,numpy

'''
DB LOG OPEN
'''
def open_log(logger_name, filename, level):
    try:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        fh = logging.FileHandler(filename)
        fh.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger
    except:
        raise Exception("Error opening log file!")

'''
DB CONNECTION
'''
def connect(log_dict):

    # Conection to DB
    try:
        conn = psycopg2.connect('host=54.216.237.226 dbname=mapplas_postgis user=postgres password=admin')
        return conn
    except:
        log('Connection Failed', log_dict, "gen_logger", "critical")
        
        
def log(string, log_dict, logger, level):
#    print "[ %s ]%s" % (datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S:%f"), string)
    log_dict[logger][level](string)

        
##############
###  MAIN  ###
##############
def main(args):

    variable = args[0]
    continue_loop = True
    n = 0
    log_file = open("/home/ubuntu/server/mapplas_server/entity_extractor/data/srpc/cities/log.txt", "a+")
    gen_log_file = open_log("extractorLogger", "data/logs/nlp_extractor_%s.log" % os.getpid(), "DEBUG")
    log_dict = {
        'gen_logger' : {
            'debug' : gen_log_file.debug,
            'critical' : gen_log_file.critical,
            'info' : gen_log_file.info
        }
    }    

    # Conection to DB
    conn = connect(log_dict)
    cur = conn.cursor()
    
    
    # Get entity names
    try:
        cur.execute("SELECT id, name1, name2, parent, region_type_id, storefront_id,is_limbo FROM entity_extractor_entities WHERE region_type_id='S' OR region_type_id='R' OR region_type_id='P' OR region_type_id='CC' OR region_type_id='WC' OR region_type_id='po'")
        entities = cur.fetchall()
    except Exception, e:
        log(e, log_dict, 'gen_logger', 'critical')
    
    while continue_loop:
    
        offset = (int(variable) + (4 * n)) * 1000
    
        log("offset: %s" % offset, log_dict, 'gen_logger', 'info')
        log("LOOP START: %s" % datetime.datetime.now(), log_dict, 'gen_logger', 'info')
    
        # Get app details for wanted app genres
        try:
            wanted_app_cathegories = ['BUSINESS', 'COMMUNICATION', 'EDUCATION', 'ENTERTAINMENT', 'FINANCE', 'HEALTH_AND_FITNESS', 'LIFESTYLE', 'PHOTOGRAPHY', 'MEDICAL', 'PRODUCTIVITY', 'SHOPPING', 'SOCIAL', 'SPORTS', 'TOOLS', 'TRANSPORTATION', 'TRAVEL_AND_LOCAL', 'WEATHER']
            
            developer_black_list = ['Mortgage Mapp', 'Kitchen Cat', 'Kitchen Cat i', 'Gold Cup Games']
            
            ######
            ###### TODO!
            ######
            # Spanish apps
            cur.execute("SELECT d.app_id, d.title, e.engdesc FROM rest_api_appdetails d inner join rest_api_appenglishdesc e on d.app_id = e.app_id inner join scraper.play_apps_index p on p.app=d.app_id WHERE p.algorithm=FALSE AND d.app_id IN (SELECT app_id FROM rest_api_application WHERE genre_id = ANY(%s)) AND d.app_id NOT IN (SELECT app_id FROM rest_api_application WHERE developer_id = ANY (%s)) ORDER BY app_id LIMIT 1000 OFFSET %s;", (wanted_app_cathegories, developer_black_list, offset, ))
            #cur.execute("select app_id, title, description FROM rest_api_appdetails WHERE app_id=%s", ("air.MAINGFREE",))
            app_details = cur.fetchall()
            
            if len(app_details) == 0:
                continue_loop = False
            
            log(len(app_details), log_dict, 'gen_logger', 'info')
            
        except Exception, e:
            log(e, log_dict, 'gen_logger', 'critical')
        
        # Remove not wanted words like 'wallpaper' or 'widget'
        app_details_without_not_wanted_stopwords = nlp_extractor_helper.remove_not_wanted_stopwords(app_details)    
        # Loop
        for detail in app_details_without_not_wanted_stopwords:
            try:
                # Check year in title
                if nlp_extractor_helper.is_valid_title_checking_years(detail[1]):
            
                    # Loop into detail title to find matches                
                    matches = nlp_extractor_helper.loop_into_title_and_description_and_get_matches(entities, detail, log_dict)
                    both_names_matches = matches[0]        
                    matches = matches[1]              
                    if len(matches) > 0:
                        ner_list = []
                        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(detail[1]+". "+detail[2])), binary=True):
                            if hasattr(chunk, 'node'):
                                ner_word = ' '.join(c[0].decode('utf-8') for c in chunk.leaves())
                                cur.execute("SELECT word FROM english_dictionary where word=%s" , (ner_word,))
                                if cur.fetchone() is not None:
                                    ner_list.append(ner_word)
                        flagged_for_remove = []
                        exact_matches = []
                        match_name_list = []
                        for match in matches:
                            match_name_list.append(match[1])
                            if match[2] != '':
                                match_name_list.append(match[2])
                            if match[6]:
                                for ner in ner_list:
                                    if match[1] == ner or match[2] == ner:
                                        exact_matches.append(match)
                                        break
                                    elif (match[1] in ner and match[1]!=ner) or (match[2] != '' and match[2] in ner and match[2]!=ner):                                    
                                        flagged_for_remove.append(match)      
                        limbo_entities_to_remove = set(flagged_for_remove) - set(exact_matches)
                        country_matches = []
                        for match in matches:
                            if match[4] == 'S':
                                country_matches.append(match)
                        matches = set(matches) - set(country_matches)
                        matches = matches - set(limbo_entities_to_remove)
                        matches = list(matches)                            
                        if len(matches) == 0:
                            log("No more matches after removing!",log_dict, 'gen_logger', 'info')
                            continue
                        else:
                            ner_list = set(ner_list) - set(list(match_name_list))                        
                            loc_matrix_result = nlp_extractor_helper.build_location_matrix(ner_list,matches, both_names_matches, cur)
                            loc_matrix = loc_matrix_result[0]
                            place_list = loc_matrix_result[1]
                            nlp_extractor_helper.check_matches_and_position(matches, place_list, loc_matrix, detail, country_matches, cur, log_dict, conn)                   
            except Exception, e:
                notice_email("belen@mapplas.com", "8jovaca0@", "belen@mapplas.com", "belen@mapplas.com", "CRITICAL on %s! %s"  % (detail[0],e,))
                log(e, log_dict, 'gen_logger', 'critical')
                log(detail[0], log_dict, 'gen_logger', 'critical')
                pass

        n = n + 1
        
        
    log('FIN',log_dict, 'gen_logger', 'info')

if __name__ == "__main__":
   main(sys.argv[1:])