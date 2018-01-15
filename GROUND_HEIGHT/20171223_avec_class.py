# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 18:49:58 2017

@author: Augustin
"""


import clr
clr.AddReference('ProtoGeometry')
clr.AddReference('RevitNodes')
clr.AddReference('DSCoreNodes')
clr.AddReference('RevitAPIUI')

from Autodesk.DesignScript.Geometry import *
from Autodesk.Revit.UI import TaskDialog
from Revit import *
from DSCore import *

#Les entrées effectuées dans ce noeud sont stockées sous forme de liste dans les variables IN.
list_data = IN[0]
min_height = IN[1]
max_height = IN[2]
choice_value = IN[3]

 
""" FUNCTIONS """
def sort_list(test_list):
     #sort the list according to the avg height of the floor
	a = len(test_list)
	msg = str(a)
	msgBox = TaskDialog
	msgBox.Show('title', msg)
	
	sorted_list = []
	while len(test_list) > 1:
		min = test_list[0][1]
		for item in test_list:
			if item[1] < min:
				min = item
		sorted_list.append(min[0])
		test_list.remove(min)
	sorted_list.append(test_list[0][0])
	return sorted_list
	
def remove_duplicates(test_list):
     #remove duplicates and make an average height for each floors
	result = []
	for item in test_list:
          avg = 0
          test_value = item[0]
          new_item = [test_value]
          for item_test in test_list:
               if item_test[0] == test_value:
                    avg += item_test[1]
                    test_list.remove(item_test)
          new_item.append(avg)
          result.append(new_item)
	return result
    
def is_in_list(elem, list_test):
	if len(list_test) == 0:
           return False
	for elem_test in list_test:
		if elem == elem_test:
			return True
	return False
 
def build_level_list(data):
    niv = [[data[i].GetParameterValueByName('Niveau'), BoundingBox.ByGeometry(data[i].Geometry()[0]).MinPoint.Z] for i in range(len(data))]
    # builds the groundList by height
    level_list = [[niv[i][0].Id, niv[i][1]] for i in range(len(niv))]
    level_list = remove_duplicates(level_list)
    level_list = sort_list(level_list)
    return level_list
 
def build_ground_list(data, level_list):
    list_grounds = []
    for element in data:
        list_grounds.append(Ground(element, level_list))
    return list_grounds
          
def build_lists(list_grounds):
    list_results = []
    list_problems = []
    for ground in list_grounds:
    	ground.get_results(list_grounds)
        for module in ground.list_results:
            if not is_in_list(module, list_results):
                list_results.append(module)
                if module.problem == True:
            		list_problems.append(module) 
    return list_results, list_problems
    
def results_display(list_results):
    return [[module.id, module.level_info, module.distance] for module in list_results]
    
def problems_display(list_problems):
	return[[module.id, module.problem_type, module.level_info, module.geometry] for module in list_problems]
            

 
class Ground:
    def __init__(self, ground, level_list):
        self.geometry = ground.Geometry()[0]
        self.id_number = ground.Id
        self.level_index = self.level_index_ground(ground, level_list)
        self.level_name = self.level_name_ground(ground)
        self.point_down = BoundingBox.ByGeometry(self.geometry).MinPoint
        self.point_up = BoundingBox.ByGeometry(self.geometry).MaxPoint
        self.pseudo_geometry = self.geometry.Translate(Vector.ByCoordinates(0., 0., -self.point_down.Z))
        
    def level_index_ground(self, ground, level_list):
        return level_list.index(ground.GetParameterValueByName('Niveau').Id)
        
    def level_name_ground(self, ground):
        return ground.GetParameterValueByName('Niveau').Name
        
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
        
        
        
class DistModule:
    def __init__(self, ground1, ground2):
        self.id = (ground1.id_number, ground2.id_number)
        self.level_info = ground1.level_name + " to " + ground2.level_name
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
        dist1 = abs(ground1.point_down.Z - ground2.point_up.Z) / 1000
        dist2 = abs(ground1.point_up.Z - ground2.point_down.Z) / 1000
        return min(dist1, dist2)
        
    def set_state(self):
        if self.distance > max_height or self.distance < min_height:
            return True
        return False
        
    def set_pb_type(self):
        if self.distance > max_height:
            return "Trop haut : " + repr(self.distance)
        if self.distance < min_height:
            return "Trop bas : " + repr(self.distance)
        return "Aucun"
    
        


def main(list_data):       
    list_level = build_level_list(list_data)

    list_grounds = build_ground_list(list_data, list_level)

    list_results, list_problems = build_lists(list_grounds)

    if choice_value == "Résultats généraux":
        OUT = results_display(list_results)
    if choice_value == "Liste des problèmes":
        OUT = problems_display(list_problems)
        
    return OUT
    
OUT = main(list_data)