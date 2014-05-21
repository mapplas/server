# -*- encoding: utf-8 -*-
import os, re, sys, psycopg2, datetime

import numpy

from KnuthMorrisStringMatcher import knuth_morris
from datetime import date

def log(string, log_dict, logger, level):
#    print "[ %s ]%s" % (datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S:%f"), string)
    log_dict[logger][level](string)


def build_location_matrix(ner_array, entities_match, both_names_matches, cur):  
    
    # Conection to DB

    
    # Get latitude and longitude from geonames for given strings. Create dictionary. 
    place_position_array = []
    for ner_match in ner_array:

        # Only searching at 'name' column
        #try:    
        cur.execute("SELECT latitude, longitude FROM geonames WHERE name=%s", (ner_match, ))
        positions = cur.fetchall()
        cur.execute("SELECT lat,lon FROM google_places where name=%s", (ner_match, ))
        positions += cur.fetchall()
        
        if len(positions) > 0:         
            for position in positions:
                #position_array.append([float(position[0]), float(position[1])])
                place_position_array.append([float(position[0]), float(position[1]),ner_match])                   
    
        #except Exception, e:
            #print e
    
    # If there were any both name matches, we remove the entities that are not those and have same name if they do not contain each other
    for both_name_entity in both_names_matches:    
        for entity in entities_match:
            if entity[0] != both_name_entity[0] and (entity[1] == entity[1] or entity[1] == entity[2] or entity[2] == entity[1] or entity[2] == entity[2]) and not check_if_polygons_match(match, both_names_matches[0], cur):                
                entities_match.remove(entity) 
    result_matrix = numpy.zeros(len(entities_match)*len(place_position_array)).reshape((len(entities_match),len(place_position_array)))
    i = 0
    for entity in entities_match:
        j = 0
        for point in place_position_array:       
            #try:

            cur.execute("SELECT ST_SetSRID(ST_MakePoint(%s, %s), 4326)", (point[1],point[0],))
            gis_point =  cur.fetchone()
            cur.execute("SELECT ST_CONTAINS((select mpoly from entity_extractor_entities where id=%s), %s)", (entity[0], gis_point[0],))
            if cur.fetchone()[0]:
                result_matrix[i,j]=1
            #except Exception, e:
            #    print e
            j += 1
        i += 1
    return [result_matrix, place_position_array]


'''
Adds an entity to a tree-structure recursively
'''
def add_to_contain_tree(contain_tree, entity_to_insert, cur, check_names=False, in_loop=False):
    #If the tree has only one element, it's much simpler
#     print contain_tree
#     print entity_to_insert
#     print check_names
    if len(contain_tree) == 1:      
        #print "len 1"  
        cur.execute("SELECT ST_CONTAINS((select mpoly from entity_extractor_entities where id=%s), (select mpoly from entity_extractor_entities where id=%s))", 
            (contain_tree[0][0][0],entity_to_insert[0],))
        #if first inside second
        if cur.fetchone()[0]:
            #print "contains"
            #in case there are no maximum matches, we wont store entities with repeated names, only top choice
            if check_names and (contain_tree[0][0][1] == entity_to_insert[1] or contain_tree[0][0][1] == entity_to_insert[2] or contain_tree[0][0][2] == entity_to_insert[1] or contain_tree[0][0][2] == entity_to_insert[2]):
                return contain_tree
            contain_tree[0].append([entity_to_insert])
            return contain_tree
        else:
            #print "not contains"
            cur.execute("SELECT ST_CONTAINS((select mpoly from entity_extractor_entities where id=%s), (select mpoly from entity_extractor_entities where id=%s))", 
                (entity_to_insert[0],contain_tree[0][0][0],))
            #if second inside first
            if cur.fetchone()[0]:
                #in case there are no maximum matches, we wont store entities with repeated names, only top choice
                if check_names and (contain_tree[0][0][1] == entity_to_insert[1] or contain_tree[0][0][1] == entity_to_insert[2] or contain_tree[0][0][2] == entity_to_insert[1] or contain_tree[0][0][2] == entity_to_insert[2]):
                    contain_tree[0][0] = entity_to_insert
                    return contain_tree
                return [entity_to_insert] + [contain_tree]
            else:
                #print "not contains other way"         
                if not in_loop:       
                    contain_tree += [[entity_to_insert]]
                    return contain_tree
                else:
                    return []
    #If the first element is not a list, it's an entity
    elif type(contain_tree[0]) != type([]):
        cur.execute("SELECT ST_CONTAINS((select mpoly from entity_extractor_entities where id=%s), (select mpoly from entity_extractor_entities where id=%s))", 
                (contain_tree[0][0],entity_to_insert[0],))
        if cur.fetchone()[0]:
            print "in"
            if check_names and (contain_tree[0][1] == entity_to_insert[1] or contain_tree[0][1] == entity_to_insert[2] or contain_tree[0][2] == entity_to_insert[1] or contain_tree[0][2] == entity_to_insert[2]):
                return []
            #pass the subtree to see if the entity fits there
            updated_sub_tree = add_to_contain_tree(contain_tree[1:][0], entity_to_insert, cur, check_names)
            if updated_sub_tree == []:
                contain_tree.append([entity_to_insert])
            else:
                contain_tree = [contain_tree[0]] + [updated_sub_tree]
            return contain_tree
        else:
            cur.execute("SELECT ST_CONTAINS((select mpoly from entity_extractor_entities where id=%s), (select mpoly from entity_extractor_entities where id=%s))", 
                (entity_to_insert[0],contain_tree[0][0],))
            if cur.fetchone()[0]:
                if check_names and (contain_tree[0][1] == entity_to_insert[1] or contain_tree[0][1] == entity_to_insert[2] or contain_tree[0][2] == entity_to_insert[1] or contain_tree[0][2] == entity_to_insert[2]):
                    contain_tree[0][0] = entity_to_insert
                    return contain_tree
                contain_tree = [entity_to_insert] + [contain_tree]
                return contain_tree
    #if the first entity is a list type, we iterate all elements on the same level
    elif type(contain_tree[0]) == type([]):
        for sub_tree in contain_tree:
            #call to self with each sub tree
            updated_sub_tree = add_to_contain_tree([sub_tree], entity_to_insert, cur, check_names,in_loop=True)
            if updated_sub_tree != []:
                sub_tree = updated_sub_tree
                return contain_tree
        contain_tree.append([entity_to_insert])
        return contain_tree    
    return []

'''
Given a tree returned by add_to_contain_tree(), this function
returns the entity to be positioned at
'''
def get_position_entity_from_tree(contain_tree):
    if len(contain_tree) == 1:
        return contain_tree[0]
    elif len(contain_tree) == 2 and type(contain_tree[1]) == type([]): 
        entity = get_position_entity_from_tree(contain_tree[1])
        if entity == False:
            return contain_tree[0]
        else:
            return entity
    elif len(contain_tree) > 2 and type(contain_tree[1]) == type([]):
        return contain_tree[0]
    elif len(contain_tree) > 1 and type(contain_tree[1]) != type([]):
        return False
    #Just in case....
    else:
        return False

'''
Positions app at a given point. If it's a single point, it creates a buffer of 500m and insert it to the entities.
If there are multiple points, it calculates the centroid of all those points and creates a point here again, with a buffer of 500m.
We then position the app at that newly created entity.
'''
def position_app_at_point(detail, point, parent_entity, multiple_points, log_dict, cur, conn):
    log("POSITIONING AT POINT!!!!!",log_dict, 'gen_logger', 'info')
    if not multiple_points:
        #print point
        #print parent_entity
        cur.execute("INSERT INTO entity_extractor_entities (name1,name2,mpoly,parent,region_type_id) VALUES (%s,%s,\
            (\
            SELECT ST_Multi(ST_Collect(ST_BUFFER(ST_MakePoint(%s,%s)::geography,500)::geometry)::geometry)::geometry\
            ),%s,'po')", 
            (point[2],str(point[0])+str(point[1]), point[0], point[1], parent_entity[0],))
        conn.commit()
        cur.execute("SELECT id,name1,name2,parent, region_type_id, storefront_id from entity_extractor_entities where name1=%s and name2=%s", 
            (point[2],str(point[0])+str(point[1]),))
        entity = cur.fetchone()
        position_app_at_entity(detail, entity, log_dict, cur, conn)
    else:
        # We need to make several points and calculate the centroid to position it there
        make_point="ST_MAKEPOINT(%s,%s)" % (point[0][0],point[0][1])
        #print point
        for p in point[1:]:
            make_point += ", ST_MAKEPOINT(%s,%s)" % (p[0],p[1])
        #print make_point
        cur.execute("INSERT INTO entity_extractor_entities (name1,mpoly,parent,region_type_id) VALUES (%s,%s,\
            (\
            SELECT ST_BUFFER(ST_CENTROID(ST_COLLECT(%s))::geography,500)::geometry\
            ),%s,'po')",
            (detail[0], make_point, parent_entity[0],))
        conn.commit()
        cur.execute("SELECT id,name1,name2,parent, region_type_id, storefront_id from entity_extractor_entities where name1=%s and name2=%s", 
            (detail[0],))
        entity = cur.fetchone()
        position_app_at_entity(detail, entity, log_dict, cur, conn)
                       
'''
Given a tree structure, returns the longest branch

'''
def get_position_branch(contain_tree, depth):
    if depth == 0:
        branch_length_list = []
        for sub_tree in contain_tree:
            branch_length_list.append(get_position_branch(sub_tree, 1))
        #print branch_length_list
        branch_length_list = numpy.array(branch_length_list)
        max_length_index = branch_length_list.argmax()
        if branch_length_list[max_length_index] == 1:    
            return []
        else:
            max_indexes = numpy.transpose((branch_length_list == branch_length_list[max_length_index]).nonzero())
            #print max_length_index
            #print max_indexes
            if len(max_indexes) == 1:
                return contain_tree[max_indexes]
            else:
                return []
    else:
        if len(contain_tree) == 1:
            #print contain_tree
            return depth
        else:
            for sub_tree in contain_tree[1:]:
                return get_position_branch(sub_tree, depth+1)
                
        
'''
LOOP APP DETAILS WITH GIVEN ENTITIES
    detail[0] --> app_id
    detail[1] --> title
    detail[2] --> description

    entity[0] --> id
    entity[1] --> name1
    entity[2] --> name2
    entity[3] --> parent_id
    entity[4] --> region_type_id
    entity[5] --> storefront_id
    entity[6] --> is_limbo
'''
def check_matches_and_position(matches, place_list, loc_matrix, detail, country_matches, cur, log_dict, conn):
    added_results = numpy.sum(loc_matrix, axis=1)
    max_index = added_results.argmax()
#     print "Entity matches:"
#     print matches
#     print "Place list"
#     print place_list
#     print "Loc_matrix"
#     print loc_matrix
    contain_tree = []
    # We have just 1 match!
    if len(matches) == 1 and not matches[0][6] and matches[0][4] != 'S':
        # There's no point inside match, position at entity if not S!
        if country_matches != []:
            do_country_match = False
            for country in country_matches:
                cur.execute("SELECT ST_CONTAINS((SELECT mpoly from entity_extractor_entities where id=%s)::geometry,\
                    (SELECT mpoly from entity_extractor_entities where id=%s)::geometry)" , (country[0],matches[0][0]))
                if cur.fetchone()[0]:
                    do_country_match = True
                    break
        else:
            do_country_match = True
        if added_results[0]==0 and do_country_match:
            position_app_at_entity(detail, matches[max_index], log_dict, cur, conn)
            return 1
        # 1 point inside match, position at point!
        elif added_results[0] == 1 and do_country_match:
            cur.execute("select * from english_dictionary where word=%s", (place_list[loc_matrix[max_index].argmax()][2].lower(),))
            if cur.fetchone() is None:
                position_app_at_point(detail, place_list[loc_matrix[0].argmax()], matches[max_index], False, log_dict, cur, conn)
                return 1
            else:
                position_app_at_entity(detail, matches[max_index], log_dict, cur, conn)
                return 1
        # N points inside match 
        elif added_results[0] > 1 and do_country_match:
            matched_places = []
            max_indexes_places = numpy.transpose((loc_matrix[0] == 1).nonzero())
            for i in range(0,len(max_indexes_places)):
                cur.execute("select * from english_dictionary where word=%s", (place_list[max_indexes_places[i]][2].lower(),))
                if cur.fetchone() is None:
                    matched_places.append(place_list[max_indexes_places[i]])
                        
            if matched_places != []:
                # position at median point! (multiple_points=True)
                if len(matched_places)==1:
                    matched_places = matched_places[0]
                    multipoint = False
                else:
                    multipoint = True
                position_app_at_point(detail, matched_places, matches[max_index], multipoint, log_dict, cur, conn)
                return 1
            else:
                position_app_at_entity(detail, matches[max_index], log_dict, cur, conn)
                return 1
        else:
#             print "entity does not match country!"
            return 0
    # N matches, some points in matches
    elif added_results[max_index] != 0:
#         print "not checking names"
        # we get the indexes of the maximum value in added_results
        max_indexes = numpy.transpose((added_results == added_results[max_index]).nonzero())
        # One maximum match
        if len(max_indexes) == 1:
            # if value is 1, only 1 point
            if added_results[max_index] == 1:
                if matches[max_index][6]:
                    cur.execute("select * from english_dictionary where word=%s", (place_list[loc_matrix[max_index].argmax()][2].lower(),))
                    if cur.fetchone() is None:
                        position_app_at_point(detail, place_list[loc_matrix[max_index].argmax()], matches[max_index], False, log_dict, cur, conn)
                        return 1
                    #print "GEonames is limboooooo"
                else: 
                    cur.execute("select * from english_dictionary where word=%s", (place_list[loc_matrix[max_index].argmax()][2].lower(),))
                    if cur.fetchone() is None:
                        position_app_at_point(detail, place_list[loc_matrix[max_index].argmax()], matches[max_index], False, log_dict, cur, conn)
                        return 1
                    else:
                        position_app_at_entity(detail, matches[max_index], log_dict, cur, conn)
            # N points
            else:
                if matches[max_index][4] != 'S':
                    #We get all points that are inside the entity
                    matched_places = []
                    max_indexes_places = numpy.transpose((loc_matrix[0] == 1).nonzero())
                    for i in range(0,len(max_indexes_places)):
                        cur.execute("select * from english_dictionary where word=%s", (place_list[max_indexes_places[i]][2].lower(),))
                        if cur.fetchone() is None:
                            matched_places.append(place_list[max_indexes_places[i]])
                    # If the matched names were limbo (i.e. are in the english dictionary) we wont place app there
                    if matched_places != []:
                        #And position app at centroid of the points (multiple_points=True)
                        position_app_at_point(detail, matched_places, matches[max_index], True, log_dict, cur, conn)
                    else:
                        position_app_at_entity(detail, matches[max_index], log_dict, cur, conn)
                    return 1
        # N maximum matches
        else:
            # Build contain tree
            finished = False
            contain_tree = []
            for i in range(1,len(max_indexes)):
                current_child = matches[max_indexes[i][0]]
                if contain_tree == []:
                    contain_tree = [[current_child]]
                else:
                    # Since we're using entities that have a matching point, we don't need to check for equal names
                    contain_tree = add_to_contain_tree(contain_tree, current_child, cur, check_names=False)
#             print "RESULTTTREE N matches, some points in matches"
#             print contain_tree
            # There's only one main root in the tree
            if len(contain_tree) == 1:
                entity_to_position = get_position_entity_from_tree(contain_tree[0])               
                position_app_at_entity(detail, entity_to_position, log_dict, cur, conn)
                return 1              
    else:       
#         print "checking names" 
        limbo_entities = []
        for match in matches:
            # We only add to the tree if it's not a limbo entity
            # Since there are no point matches, limbo entities will be ignored
            if len(contain_tree) == 0 and not match[6]:
                contain_tree.append([match])
            elif not match[6]:           
                contain_tree = add_to_contain_tree(contain_tree, match, cur, check_names=True)     
            elif match[6]:
                limbo_entities.append(match)    
        # After building the contain tree, we check if there are any limbo entities inside those and if so, add them.   
        for limbo_entity in limbo_entities:
            for sub_tree in contain_tree:            
                cur.execute("SELECT ST_CONTAINS((SELECT mpoly from entity_extractor_entities where id=%s)::geometry,\
                    (SELECT mpoly from entity_extractor_entities where id=%s)::geometry)" , (sub_tree[0][0],limbo_entity[0]))
                limbo_in_tree = cur.fetchone()[0]
                if limbo_in_tree:
                    sub_tree = add_to_contain_tree([sub_tree], limbo_entity, cur, check_names=True)
                    break
                else:
                    cur.execute("SELECT ST_CONTAINS((SELECT mpoly from entity_extractor_entities where id=%s)::geometry,\
                        (SELECT mpoly from entity_extractor_entities where id=%s)::geometry)" , (limbo_entity[0],sub_tree[0][0]))
                    tree_in_limbo = cur.fetchone()[0]
                    if tree_in_limbo:
                        sub_tree = [limbo_entity] + [sub_tree]
                        break
                
#         print "RESULTTTREE in else"
#         print contain_tree
        # len function only checks first level, so, if there's only 1 entity in top level
        if len(contain_tree) == 1 and contain_tree[0][0][4] != 'S':
            entity_to_position = get_position_entity_from_tree(contain_tree[0])
            # Check if there are any country matches. IF there are, position only if it intersects with our entity!
            if country_matches != []:
                for country in country_matches:
                    cur.execute("SELECT ST_CONTAINS((SELECT mpoly from entity_extractor_entities where id=%s)::geometry,\
                    (SELECT mpoly from entity_extractor_entities where id=%s)::geometry)" , (country[0],entity_to_position[0]))
                    if cur.fetchone()[0]:
                        position_app_at_entity(detail, entity_to_position, log_dict, cur, conn)
                        return 1
                    else:
                        return 0
            else:
                # If now country matches, we just position 
                position_app_at_entity(detail, entity_to_position, log_dict, cur, conn)
                return 1
        # We removed all limbo entities and there are no more entities
        elif len(contain_tree) == 0:
            log("LIMBO WITHOUT PLACE MATCHES! for app %s" % detail[0],log_dict, 'gen_logger', 'info')
            return 0
        
    # If function has not returned anything until now, we still try to position
    # Current state:
    # Limbo or no limo, contain tree has N same-level roots
    parents_ids_equal = True
    check_parent_ids = type(contain_tree[0]) == type([])
    first_parent_id = ''
    entities_with_country_match = []
    entity_in_title = None
    check_title = False
    i = 0
    for entity in contain_tree:
        # Check parent_id
        if check_parent_ids:
            if i!=0 and entity[0][3] != first_parent_id and entity[0][3] != 0:
                parents_ids_equal = False  
            if i == 0:
                first_parent_id = contain_tree[0][0][3]
                i = 1              
        # Check if current entity can be found in title                
        if check_title and(entity[0][1] in detail[1] or (entity[0][2]!='' and entity[0][2] in detail[1])):
            if entity_in_title is None:
                entity_in_title = entity[0]
            elif entity_in_title[1] == entity[0][1] or entity_in_title[1] == entity[0][2] or entity_in_title[2] == entity[0][1] or entity_in_title[2] == entity[0][2]:
                entity_in_title = None
                check_title = False
        # Check if there are any country matches and, if so, store the matched entities that are inside them
        if country_matches != [] and entity[0][4] != 'S':
            for country in country_matches:
                cur.execute("SELECT ST_CONTAINS((SELECT mpoly from entity_extractor_entities where id=%s)::geometry,\
                    (SELECT mpoly from entity_extractor_entities where id=%s)::geometry)" , (country[0],entity[0][0]))
                if cur.fetchone()[0]:
                    entities_with_country_match.append(entity[0])        
    # After loop, check results               
    if entity_in_title is not None and not entity_in_title[6]:
        # Some entity is in title, position there!
        if entity_in_title[4] != 'S':
            position_app_at_entity(detail, entity_in_title, log_dict, cur, conn)
            return 1
        else:
            return 0
    # If all entities' parents ids are equal, position at parent only if parent not State
    elif check_parent_ids and parents_ids_equal and contain_tree != []:
        cur.execute("select id,name1,name2,parent,region_type_id,storefront_id from entity_extractor_entities where id=%s" 
                    , (contain_tree[0][0][3],))
        parent_entity = cur.fetchone()
#         print "parent entity"
#         print parent_entity
        if parent_entity[4] != 'S':
            position_app_at_entity(detail, parent_entity, log_dict, cur, conn)
            return 1
        else:
            #TODO: Position at all places?
            log("STATE",log_dict, 'gen_logger', 'info')
    # If there's only 1 entity that matches with a matched country, position there
    elif len(entities_with_country_match) == 1:
        position_app_at_entity(detail, entities_with_country_match[0], log_dict, cur, conn)
        return 1        
    # Get the longest branch to position on!
    elif contain_tree != [] and len(contain_tree) < 5:        
        # If N entities match in matched countries, only find longest branch in there
        if len(entities_with_country_match) >= 1:
            contain_tree = entities_with_country_match            
        root_to_position = get_position_branch(contain_tree,0)       
#         print "root to position %s " % root_to_position         
        if root_to_position != []:
            entity_to_position = get_position_entity_from_tree(root_to_position) if type(root_to_position) == type([]) else root_to_position
#            print entity_to_position
            if entity_to_position[4] != 'S':
                position_app_at_entity(detail, entity_to_position, log_dict, cur, conn)
                return 1
            else:
                return 0
    return 0


'''
Gets a string and checks if 4 digit numbers appears on it. (year)
If matches only one number, compares it with current year and 2008. If between both, returns false.
If matches more than a number, if all are smaller than current year and bigger than 2008, returns false.
'''
def is_valid_title_checking_years(title):

    year_2008 = 2008
    current_year = date.today().year
    
    pattern = re.compile('(\d{4})+')
    matches = pattern.findall(title)
    
    number_of_matches = len(matches)
    
    if number_of_matches != 0:
    
        # One match
        if number_of_matches == 1:
            if int(matches[0]) >= year_2008 and int(matches[0]) < int(current_year):
                return False
            else:
                return True
            
        # More than one match
        else:
        
             for match in matches:
                 if int(matches[0]) >= year_2008 and int(match) >= int(current_year):
                     return True
             
             return False
    else:
        return True

    

'''
Loops into entities with title or description.
'''
def loop_into_title_and_description_and_get_matches(entities, detail, log_dict):
#     print "LOOP    MATCHES START %s: %s" % (is_title, datetime.datetime.now())
    
    
    matches = []
    both_names_match_array = []
    string_matches = []
    to_search = detail[1]+". "+detail[2]
    for entity in entities:                
    
        first_name_match = False
        both_names_match = False

        entity_name1 = entity[1]
        entity_name2 = entity[2]
        
#         if entity_name1 in string_matches or entity_name2 in string_matches:
#             matches.append(entity)
#             continue
    
        # Check match for entity name1
        matched_entity_name = knuth_morris(entity[1], to_search)
        if matched_entity_name != '':
            first_name_match = True
            
            string_matches.append(matched_entity_name)
        
            if entity not in matches:
                append = True
                for match in matches:
                    if entity[1] in match[1] and entity[1] != match[1]:
                        append=False
                        break
                    elif match[1] in entity[1] and match[1] != entity[1]:
                        for inner_match in matches:
                            if inner_match[1] == match[1]:
                                matches.remove(inner_match)
                if append:        
                    matches.append(entity)
               
            else:
                break
                
        
        # Check name2 if entity is not a state (US, ES, MX...)
        if entity_name2 != '' and entity[4] != 'S':
            # Check match for entity name2
            matched_entity_name2 = knuth_morris(entity[2], to_search)
            if matched_entity_name2 != '':
            
                string_matches.append(matched_entity_name2)
            
                if first_name_match:
                    both_names_match = True
            
                if entity not in matches:
                    matches.append(entity)                   
                else:
                    break
        
        if both_names_match:
            both_names_match_array.append(entity)
    log( "finished matches in title and description for %s" % detail[0],log_dict, 'gen_logger', 'info')
    log(matches,log_dict, 'gen_logger', 'info')
#     print "LOOP    MATCHES END %s: %s" % (is_title, datetime.datetime.now())
    return [both_names_match_array, matches]


'''
Position app.
'''
def position_app_at_entity(detail, entity, log_dict, cur, conn):

    try:        
        cur.execute("INSERT INTO rest_api_geometry (app_id, entity_id, origin, storefront_id, enabled) VALUES (%s, %s, %s, %s, %s)", (detail[0], entity[0], entity[4], entity[5], 1,))
        conn.commit()
    except Exception, e:
        log(e,log_dict, 'gen_logger', 'info')

    log('POSITIONED',log_dict, 'gen_logger', 'info')
    log("%s -> %s" % (detail[0],entity[0]) ,log_dict, 'gen_logger', 'info')
#     log_file.write("POSITIONED")
        

'''
Given 2 entities, checks if one contains each other. (polygons)
'''
def check_if_polygons_match(entity_1, entity_2, cur):

    try:
        cur.execute("SELECT ST_Contains((SELECT mpoly FROM entity_extractor_entities WHERE id=%s), ST_CENTROID((SELECT mpoly FROM entity_extractor_entities WHERE id=%s))) OR ST_Contains((SELECT mpoly FROM entity_extractor_entities WHERE id=%s), ST_CENTROID((SELECT mpoly FROM entity_extractor_entities WHERE id=%s)));", (entity_1[0], entity_2[0], entity_2[0], entity_1[0],))
        return cur.fetchone()[0]

    except Exception, e:
        raise e
        

'''
Finds parent entity between two related entities
'''
def get_parent_entity_id(entity_1, entity_2):

    entity_type_dict = {'R' : 4, 'P' : 3, 'CC' : 2, 'WC' : 1, 'S' : 0}

    entity_1_region_type_id = entity_1[4]
    entity_2_region_type_id = entity_2[4]
        
    if entity_type_dict[entity_1_region_type_id] > entity_type_dict[entity_2_region_type_id]:
        return entity_1
    else:
        return entity_2


'''
Returns index of top entity type
'''
def get_top_entity_type(entity_type_list):
    
    entity_type_dict = {'R' : 4, 'P' : 3, 'CC' : 2, 'WC' : 2, 'S' : 0}
    
    entity_type_number_list = []
    i = 0
    
    for element in entity_type_list:
        entity_type_number_list.append(entity_type_dict[element])
        i = i + 1
        
    return entity_type_number_list.index(max(entity_type_number_list))


'''
Returns index of bottom entity type
'''
def get_bottom_entity_type(entity_type_list):
    
    entity_type_dict = {'S' : 5, 'R' : 4, 'P' : 3, 'CC' : 2, 'WC' : 2}
    
    entity_type_number_list = []
    i = 0
    
    for element in entity_type_list:
        entity_type_number_list.append(entity_type_dict[element])
        i = i + 1
        
    return entity_type_number_list.index(min(entity_type_number_list))        


'''
Creates regex for given string
'''
def create_regex(string_to_compare):
    pattern = r'.*(\b%s\b).*' % string_to_compare
    regex = re.compile(pattern, re.IGNORECASE)
    return regex
    
    
'''
Receives appDetails array and checks if word 'wallpaper' or 'wallpapers' is present
'''
def remove_not_wanted_stopwords(app_details):

    words = ['widget', 'widgets', 'wallpaper', 'wallpapers', 'ringtone', 'ringtones']
    
    app_ids_with_stopwords = []
    #print 'app details'
    #print len(app_details)
    found = False
    
    for detail in app_details:
        for word in words:
            if knuth_morris(word, detail[1]) != '' or knuth_morris(word, detail[2]) != '':
                app_ids_with_stopwords.append(detail[0])
                found = True
                break
            
        found = False
        
    
    # Remove from app_detail list apps whose ids are in app_ids_with_stopwords
    good_apps = []
    for detail in app_details:
        if detail[0] in app_ids_with_stopwords:
            #print detail[0]
            pass
        else:
            good_apps.append(detail)
    
    #print 'good apps'
    #print len(good_apps)                
    return good_apps