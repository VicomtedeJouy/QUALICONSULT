# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 18:26:28 2017

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
input = IN[0]
min_height = IN[1]
max_height = IN[2]

#for tests
instance_solid = input[0]

# list that will be used to store the problematic grounds
problem_grounds = []
global problem_grounds

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

def build_level_list(niv):
	# builds the groundList by height
	level_list = [niv[i].Id for i in range(len(niv))]
	level_list = remove_duplicates(level_list)
	level_list = sort_list(level_list)
	return level_list
		
def build_ground_list(list, niv):
	# builds the list of grounds classified by floors
	list_ground = [[] for i in range(len(niv))]
	for ground in list:
		level = ground.GetParameterValueByName('Niveau').Id
		index = niv.index(level)
		list_ground[index].append(ground.Geometry()[0])
	return list_ground
		
def distanceTo(ground_up, ground_down):
	point_down = BoundingBox.ByGeometry(ground_down).MaxPoint
	point_up = BoundingBox.ByGeometry(ground_up).MinPoint
	dist = point_up.Z - point_down.Z
	dist = dist/1000.
	check_height(ground_down, ground_up, dist) 
	return dist
	
def does_superpose(ground_up, ground_down):
	h_up = BoundingBox.ByGeometry(ground_up).MinPoint.Z
	h_down = BoundingBox.ByGeometry(ground_down).MinPoint.Z
	temp_ground_up = ground_up.Translate(Vector.ByCoordinates(0., 0., -h_up))
	temp_ground_down = ground_down.Translate(Vector.ByCoordinates(0., 0., -h_down))
	if Geometry.DoesIntersect(temp_ground_up, temp_ground_down):
		temp_inter = Geometry.Intersect(temp_ground_up, temp_ground_down)
		if isinstance(temp_inter[0], Solid):
			return True
	return False

def upper_level_dist(ground_down, list_ground):
	# return the distance between ground and the grounds from the upper level that are superposed
	list_dist = []
	for ground_up in list_ground:
		if does_superpose(ground_up, ground_down):
			list_dist.append(distanceTo(ground_up, ground_down))
	return list_dist

def check_height(ground_down, ground_up, dist):
	if dist < min_height:
		problem_grounds.append([ground_down, ground_up])
	if dist > max_height:
		problem_grounds.append([ground_down, ground_up])

def main(input):
	niv = [input[i].GetParameterValueByName('Niveau') for i in range(len(input))]
	# list of the different sotries
	list_level = build_level_list(niv)
	# organised list of the geometry
	list_ground = build_ground_list(input, list_level)
	# number of stories
	N = len(list_level)
	list_dist = [[] for i in range(N-1)]
	
	for i in range(N-1):
		for ground_down in list_ground[i]:
			list_dist[i].append(upper_level_dist(ground_down, list_ground[i+1]))
			
	return list_dist

list_dist = main(input)

display = IN[3]
if display == "Liste des distances":
	OUT = list_dist
if display == "Liste des solides":
	OUT = problem_grounds