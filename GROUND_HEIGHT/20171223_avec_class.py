# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 18:49:58 2017

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
    list_def = [list_test[0]]
    for new_elem in list_test:
    	id_1 = new_elem[0]
    	id_2 = new_elem[1]
    	for elem in list_def:
    		if id_1 == elem[0] and id_2 == elem[1]:
    			break
    		list_def.append(elem)
    return list_def
 
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
    temp = []
    for ground in list_grounds:
        ground.get_results(list_grounds)
        temp.append(ground.list_results)
        for i in range(len(temp)):
            list_results.append(temp[i])
    list_results = organise(list_results)
    return list_results
    
def build_list_problems(list_results):
    list_problems= []
    for elem in list_results:
        if elem[2] > max_height or elem[2] < min_height:
            list_problems.append(elem)
    return list_problems
    
        
            

 
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
                temp_1.append(ground)
                dist = self.distance_to(ground)
                self.list_results.append([ground.id_number, self.id_number, dist, self.geometry, ground.geometry])
            if ground.level_index == self.level_index+1 and self.does_superpose(ground):
                temp_2.append(ground)
                dist = self.distance_to(ground)
                self.list_results.append([self.id_number, ground.id_number, dist, self.geometry, ground.geometry])
        
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
                dist = self.distance_to(ground)
                self.results.append([self.id_number, ground.id_number, dist, self.geometry, ground.geometry])
        if len(self.surrounding_grounds[1]) > 0:
            for ground in self.surrounding_grounds:
                dist = self.distance_to(ground)
                self.results.append([min(self.id_number, ground.id_number), max(self.id_number, ground.id_number), dist, ground.geometry, self.geometry])
        
        
list_level = build_level_list(list_data)

list_grounds = build_ground_list(list_data, list_level)

list_results = build_list_results(list_grounds)

list_problems = build_list_problems(list_results)

if choice_value == "Résultats généraux":
    OUT = list_results
if choice_value == "Listes des problèmes":
    OUT = list_problems