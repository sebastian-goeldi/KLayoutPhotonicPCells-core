from kppc.photonics import PhotDevice,PortCreation
from lygadgets.cell_translation import anyCell_to_anyCell as actac

class Device(PhotDevice):
        
    def __init__(self):
      PhotDevice.__init__(self)
      self.pcellinstances = []
      self.dev=None

    def device(self):
      self.dev = None
      #raise ImplentationError('This function must be implemented by the cell and define self.device as a phild.Device')
      
    def shapes(self):
      self.dev = None
      self.pcellinstances = []
      self.device()
      if self.dev is not None:
        actac(self.dev,self.cell)
    
    def create_param_inst(self):
      self.dev = None
      self.pcellinstances = []
      self.device()
      if self.dev is not None:
        ports = []
        for i in self.dev.ports:
          p = self.dev.ports[i]
          ports.append(PortCreation(p.midpoint[0],p.midpoint[1],int(p.orientation),p.width,name=i))
        return ports,self.pcellinstances
      else:
        return self.pcellinstances
        
    def add_pcell(self,params,n=1):
      instance = self.add_pcell_variant(params,number=n)
      self.pcellinstances.append(instance)
      return instance