"""
Auto Shader Tool for Maya

An advanced Maya tool for automating Arnold shader networks with intelligent texture mapping and UDIM support.

Version__ = "1.0"
Author__ = "Nieves Yashuang Lopez"
Email__ = "nieveslpez.p@gmail.com"
License__ = "MIT"
Maya_version__ = "2020+"
Renderer__ = "Arnold"

"""

from . import shaderMain
from . import shaderUi

autoShaderUi = None

#Initialize and avoid duplicates
def showTool():
    global autoShaderUi
    try:
        if autoShaderUi:
            autoShaderUi.close()
            autoShaderUi.deleteLater()
    except:
        pass
    
    autoShaderUi = shaderUi.AutoShaderTool()
    autoShaderUi.show()

"""
Usage:
import autoShaderTool
autoShaderTool.showTool()

"""