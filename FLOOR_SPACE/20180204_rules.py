import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
#Les entrées effectuées dans ce noeud sont stockées sous forme de liste dans les variables IN.

room_data = IN[0]
furniture_data = IN[1]


class Room:
	def __init__(self, element):
		self.room = element
		self.solid = Solid.ByUnion(element.Geometry())
		self.id = element.Id
		self.ground_srf = self.ground_srf()
		self.wall_srf = self.wall_srf()
		self.dimensions = self.surface_dim()
	
	#divise la surface selon sa dimension
	def divide_srf(self, dimX = 250., dimY = 250.):
		pt_list = []
		for i in range(len(self.dimensions)):
			distX, distY = self.dimensions[i]
			u = distX/dimX
			v = distY/dimY
			srf = self.ground_srf[i]
			for j in range(int(u)+1):
				for k in range(int(v)+1):
					pt = srf.PointAtParameter(j/u, k/v)
					if self.room.IsInsideRoom(pt):
						pt_list.append(pt)
		return pt_list
	
	#retourne les dimensions de la surfaces données SI CELLE-CI EST CARRE
	def surface_dim(self):
		dims = []
		for srf in self.ground_srf:
			pt1 = srf.PointAtParameter(0., 0.)
			pt2 = srf.PointAtParameter(1., 1.)
			distX = abs(pt1.X - pt2.X)
			distY = abs(pt1.Y - pt2.Y)
			dims.append((distX, distY))
		return dims
	
	#retroune la surface du sol (ayant une normale négative)
	def ground_srf(self):
		faces = self.solid.Explode()
		ground_srf = []
		for srf in faces:
			vect = srf.NormalAtParameter(0.5, 0.5)
			if vect.Z < -0.5:
				ground_srf.append(srf)
		return ground_srf
	
	#retourne la liste de surface des murs (ayant une normale horizontale)
	def wall_srf(self):
		faces = self.solid.Explode()
		wall_srf = []
		for srf in faces:
			vect = srf.NormalAtParameter(0.5, 0.5)
			if abs(vect.Z) < 0.1:
				wall_srf.append(srf)
		return wall_srf
		
	#associe les "fournitures" dans la pièce"
	def get_furniture(self, furniture_list):
		self.furniture = []
		for element in furniture_list:
			if self.room.IsInsideRoom(element.location):
				self.furniture.append(element)
	
	#retourne les points à checker avec le cercle	
	def get_check_points(self, radius):
		pts = self.divide_srf(radius)
		for srf in self.wall_srf:
			for pt in pts:
				if srf.DistanceTo(pt) < radius:
					pts.remove(pt)
		return pts
	
	#renvoie les résultats du check de cercle général
	def circle_check(self, radius):
		pts = self.get_check_points(radius)
		
		for pt in pts:
			state = True		
			cle = Circle.ByCenterPointRadius(pt, radius)
			dir = Vector.ByCoordinates(0., 0., 1500.)
			cle = cle.Extrude(dir)
			# vérifie que le cercle ne touche pas un mur
			for srf in self.wall_srf:
				if cle.DoesIntersect(srf):
					state = False
					break
			
			# vérifie que le cercle ne touche pas de furniture
			if len(self.furniture) != 0:
				for element in self.furniture:
					if cle.DoesIntersect(element.solid):
						state = False
						break
			
			if state == True:
				return cle
		return 
		
	#renvoie le cercle de 150 devant les composants
	#def circle_in_front_of_component(self):
		
	#lance les vérificatiions
	def check(self, radius = 750):
		circle_result = self.circle_check(radius)
		
		if circle_result == None:
			return "La règle n'est pas respectée"
		else:
			if len(self.furniture) != 0:
				return "Ce cercle convient", circle_result
			else:
				return "La largeur de l'espace est suffisante"
		
class Furniture:
	def __init__(self, element):
		self.furniture = element
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
		

furnitures = [Furniture(element) for element in furniture_data]

rooms = [Room(element) for element in room_data]

results = []

for room in rooms:
	room.get_furniture(furnitures)
	results.append(["Pièce : {}".format(room.id), room.check()])
	
OUT = results
