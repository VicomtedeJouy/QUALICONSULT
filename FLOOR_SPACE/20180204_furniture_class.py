import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
#Les entrées effectuées dans ce noeud sont stockées sous forme de liste dans les variables IN.
input = IN[0]

class Furniture:
	def __init__(self, element):
		self.element = element
		self.solid = Solid.ByUnion(element.Geometry())
		self.id = element.Id
		self.point_down = BoundingBox.ByGeometry(self.solid).MinPoint
		self.point_up = BoundingBox.ByGeometry(self.solid).MaxPoint
		self.location = self.get_location()
		#self.pseudo_geometry = self.get_pseudo_geometry()
		
		
	def get_location(self):
		x = (self.point_up.X + self.point_down.X)/2.
		y = (self.point_up.Y + self.point_down.Y)/2.
		z = (self.point_up.Z + self.point_down.Z)/2.
		return Point.ByCoordinates(x, y, z)
		
	def get_pseudo_geometry(self):
		edges = self.solid.Edges
		crvs = [edge.CurveGeometry for edge in edges]
		plane = Plane.XY()
		dir = Vector.ByCoordinates(0, 0, -1)
		results = [crv.Project(plane, dir) for crv in crvs]
		return results
		

list = [Furniture(element) for element in input]
OUT = [element.location for element in list]