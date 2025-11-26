import util
import math 
class Ground:
    def __init__(self,height:int,id:str):
        self.height = height
        self.renderer = util.getRenderer()
        self.id = id
        # self.renderer.ResizeTexture(self.id,(0,height),True,True)
    def renderGround(self):
        self.renderer.render([self.id],[(0,100)])
    def isTouchingGround(self,y):
        return y >= self.height-10 #10px buffer