# -*- coding: utf-8 -*-
"""
Created on Sun Jan 07 18:49:58 2018

@author: Augustin
"""

import System as sys

#stdsave = sys.stdout
#fout = open(r'C:\Users\Augustin\Informatique\output.txt','w')
#sys.stdout = fout



import clr
clr.AddReference('ProtoGeometry')
clr.AddReference('RevitNodes')
clr.AddReference('DSCoreNodes')

from Autodesk.DesignScript.Geometry import *
from Revit import *
from DSCore import *

#Les entrées effectuées dans ce noeud sont stockées sous forme de liste dans les variables IN.
list_data1 = IN[0]
list_data2 = IN[1]
min_height = IN[2]
max_height = IN[3]
invalid = IN[4]

global min_height
global max_height
global invalid

 
# créer une liste d'objets HorizotalObject            
def generate_list(data_list):
	class_list = []
	for element in data_list:
		class_list.append(HorizontalObject(element))
	return class_list

# classe permettant l'exploitation des données plus facielement
class HorizontalObject:
    def __init__(self, object):
        self.geometry = object.Geometry()[0]
        self.id = object.Id
        self.level = object.GetParameterValueByName('Niveau').Id
        self.level_name = object.GetParameterValueByName('Niveau').Name
        self.point_down = BoundingBox.ByGeometry(self.geometry).MinPoint
        self.point_up = BoundingBox.ByGeometry(self.geometry).MaxPoint
        self.pseudo_geometry = self.geometry.Translate(Vector.ByCoordinates(0., 0., -self.point_down.Z))
        
    def dist_object(self, other):
    	dist1 = abs(self.point_down.Z - other.point_up.Z)
    	dist2 = abs(self.point_up.Z - other.point_down.Z)
    	return min(dist1, dist2)
    	
    def same_floor(self, other):
    	if self.level == other.level:
    		return True
    	return False
    
    def superpose(self, other):
        if Geometry.DoesIntersect(self.pseudo_geometry, other.pseudo_geometry):
            temp_inter = Geometry.Intersect(self.pseudo_geometry, other.pseudo_geometry)
            if isinstance(temp_inter[0], Solid):
                return True
        return False
        
    def check_wrap(self, distance):
		if distance < min_height:
			return True, "Plafond trop bas : {}m < {}m".format(distance, min_height)
		if distance > max_height:
			return True, "Plafond trop haut : {}m > {}m".format(distance, max_height)
		return False, "Hateur de {}m".format(distance)
        
    def check_list(self, other_list):
    	results = []
    	for element in other_list:
    		#print self.same_floor(element), self.superpose(element)
    		if self.same_floor(element) and self.superpose(element):
				id = (min(self.id, element.id), max(self.id, element.id))
				dist = self.dist_object(element)
				bloc = [id, self.level_name, dist]
				problem, msg = self.check_wrap(dist)
				if invalid and problem:
					bloc.append(msg)
				results.append(bloc)
		return results

	def check_item(self, other):
		result = []
		if self.same_floor(other) and self.superpose(other):
			id = (min(self.id, other.d), max(self.id, other.id))
			dist = self.dist_object(element)
			bloc = [id, self.level_name, dist]
			problem, msg = self.check_wrap(dist)
			if invalid and problem:
				bloc.append(msg)
			result.append(bloc)
		return result
		
	
    
        
def main(data1, data2):        
	list1 = generate_list(data1)
	list2 = generate_list(data2)
	
	results = []
	debug = []
	
	for element in list1:
		temp = element.check_list(list2)
		
		debug.append(temp)
		
		for bloc in temp:
			results.append(bloc)
			
	return results
	
def main_2(data1, data2)
	list1 = generate_list(data1)
	list2 = generate_list(data2)
	
	results = []
	
	for element in list1:
		for other_element in list2:
			temp = element.check_item(other_element)
			
			if temp != None:
				results.append(temp)
	
	return result

#OUT = generate_list(list_data2)
OUT = main_2(list_data1, list_data2)

#sys.stdout = stdsave
#fout.close()