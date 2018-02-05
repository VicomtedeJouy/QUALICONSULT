import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
#Les entrées effectuées dans ce noeud sont stockées sous forme de liste dans les variables IN.
input = IN[0]

geometry = []
normals = []
face_list = []

class Room:
	def __init__(self, element):
		self.room = element
		self.solid = Solid.ByUnion(element.Geometry())
		self.id = element.Id
		self.ground_srf = self.ground_srf()
		self.wall_srf = self.wall_srf()
		self.dimensions = self.surface_dim()
		self.division_points = self.divide_srf()
	
	def divide_srf(self):
		pt_list = []
		for i in range(len(self.dimensions)):
			distX, distY = self.dimensions[i]
			u = distX/250.
			v = distY/250.
			srf = self.ground_srf[i]
			for j in range(int(u)+1):
				for k in range(int(v)+1):
					pt = srf.PointAtParameter(j/u, k/v)
					if self.room.IsInsideRoom(pt):
						pt_list.append(pt)
		return pt_list
	
	def surface_dim(self):
		dims = []
		for srf in self.ground_srf:
			pt1 = srf.PointAtParameter(0., 0.)
			pt2 = srf.PointAtParameter(1., 1.)
			distX = abs(pt1.X - pt2.X)
			distY = abs(pt1.Y - pt2.Y)
			dims.append((distX, distY))
		return dims
	
	def ground_srf(self):
		faces = self.solid.Explode()
		ground_srf = []
		for srf in faces:
			vect = srf.NormalAtParameter(0.5, 0.5)
			if vect.Z < -0.5:
				ground_srf.append(srf)
		return ground_srf
		
	def wall_srf(self):
		faces = self.solid.Explode()
		wall_srf = []
		for srf in faces:
			vect = srf.NormalAtParameter(0.5, 0.5)
			if abs(vect.Z) < 0.1:
				wall_srf.append(srf)
		return wall_srf
	




room = [Room(element) for element in input]

#face_list = [ground_srf(solid) for solid in input]
#face_list = [divide_srf(srf[0]) for srf in face_list]

OUT = [_room.wall_srf for _room in room]