# -*- coding: utf-8 -*-
"""
Created on Sun Jan 07 18:49:58 2018

@author: Augustin
"""

import clr
clr.AddReference('ProtoGeometry')
clr.AddReference('RevitNodes')
clr.AddReference('DSCoreNodes')

from Autodesk.DesignScript.Geometry import *
from Revit import *
from DSCore import *

#Les entrées effectuées dans ce noeud sont stockées sous forme de liste dans les variables IN.
list_data = IN[0]
min_height = IN[1]
max_height = IN[2]
choice_value = IN[3]

 
""" FUNCTIONS """
def sort_list(test_list):
	sorted_list = []
	while len(test_list) > 1:
		min = test_list[0]
		index_min = 0
		for item in test_list:
			if item < min:
				min = item
				index_min = test_list.index(item)
		sorted_list.append(min)
		test_list.pop(index_min)
	sorted_list.append(test_list[0])
	return sorted_list
	
def remove_duplicates(test_list):
	result = []
	duplicate = []
	for item in test_list:
		if item not in duplicate:
			duplicate.append(item)
			result.append(item)
	return result
 
def organise(list_test):
    list_def = [list_test[0][0]]
    for new_elem in list_test[0]:
        id_1 = new_elem[0]
        id_2 = new_elem[1]
    for elem in list_def:
        if id_1 == elem[0] and id_2 == elem[1]:
            break
        list_def.append(elem)
    return list_def
    
def is_in_list(elem, list_test):
	if len(list_test) == 0:
		return False
	for elem_test in list_test:
		if elem == elem_test:
			return True
	return False
 
def build_level_list(data):
    niv = [data[i].GetParameterValueByName('Niveau') for i in range(len(data))]
    # builds the groundList by height
    level_list = [niv[i].Id for i in range(len(niv))]
    level_list = remove_duplicates(level_list)
    level_list = sort_list(level_list)
    return level_list
 
def build_ground_list(data, level_list):
    list_grounds = []
    for element in data:
        list_grounds.append(Ground(element, level_list))
    return list_grounds
          
def build_list_results(list_grounds):
    list_results = []
    for ground in list_grounds:
    	ground.get_results(list_grounds)
        for module in ground.list_results:
            if not is_in_list(module, list_results):
                list_results.append(module)
    return list_results
    
def build_list_problems(list_results):
    list_problems= []
    for module in list_results:
        if module.problem == True:
            list_problems.append(module)
    return list_problems
    
def results_display(list_results):
    return [[module.id, module.distance] for module in list_results]
    
def problems_display(list_problems):
	return[[module.id, module.problem_type, module.geometry] for module in list_problems]
            

 
class Ground:
    def __init__(self, ground, level_list):
        self.geometry = ground.Geometry()[0]
        self.id_number = ground.Id
        self.level_index = self.level_index_ground(ground, level_list)
        self.point_down = BoundingBox.ByGeometry(self.geometry).MinPoint
        self.point_up = BoundingBox.ByGeometry(self.geometry).MaxPoint
        self.pseudo_geometry = self.geometry.Translate(Vector.ByCoordinates(0., 0., -self.point_down.Z))
        
    def level_index_ground(self, ground, level_list):
        return level_list.index(ground.GetParameterValueByName('Niveau').Id)
        
    def get_results(self, list_grounds):
        self.list_results = []
        for ground in list_grounds:
            temp_1 = []
            temp_2 = []
            if ground.level_index == self.level_index-1 and self.does_superpose(ground):
                self.list_results.append(DistModule(ground, self))
            if ground.level_index == self.level_index+1 and self.does_superpose(ground):
                self.list_results.append(DistModule(self, ground))
        
    def does_superpose(self, ground):
        if Geometry.DoesIntersect(self.pseudo_geometry, ground.pseudo_geometry):
            temp_inter = Geometry.Intersect(self.pseudo_geometry, ground.pseudo_geometry)
            if isinstance(temp_inter[0], Solid):
                return True
        return False
        
    def distance_to(self, ground):
        dist1 = abs(self.point_down.Z - ground.point_up.Z)
        dist2 = abs(self.point_up.Z - ground.point_down.Z)
        return min(dist1, dist2)
        
    def get_results_old(self):
        self.results = []
        if len(self.surrounding_grounds[0]) > 0:
            for ground in self.surrounding_grounds:
            	self.results.append(DistModule(self, ground))
        if len(self.surrounding_grounds[1]) > 0:
            for ground in self.surrounding_grounds:
                self.results.append(DistModule(ground, self))
        
        
class DistModule:
    def __init__(self, ground1, ground2):
        self.id = (ground1.id_number, ground2.id_number)
        self.distance = self.set_distance(ground1, ground2)
        self.geometry = (ground1.geometry, ground2.geometry)
        self.problem = self.set_state()
        self.problem_type = self.set_pb_type()
		
    def __eq__(self, other):
        if self.id[0] == other.id[0] and self.id[1] == other.id[1]:
            return True
        if self.id[0] == other.id[1] and self.id[1] == other.id[0]:
            return True
        return False
		
    def set_distance(self, ground1, ground2):
        dist1 = abs(ground1.point_down.Z - ground2.point_up.Z)
        dist2 = abs(ground1.point_up.Z - ground2.point_down.Z)
        return min(dist1, dist2)
        
    def set_state(self):
        if self.distance > max_height or self.distance < min_height:
            return True
        return False
        
    def set_pb_type(self):
        if self.distance > max_height:
            return "Trop haut"
        if self.distance < min_height:
            return "Trop bas"
        return "Aucun"
    
        
        
list_level = build_level_list(list_data)

list_grounds = build_ground_list(list_data, list_level)

list_results = build_list_results(list_grounds)

list_problems = build_list_problems(list_results)

if choice_value == "Résultats généraux":
    OUT = results_display(list_results)
if choice_value == "Liste des problèmes":
    OUT = problems_display(list_problems)