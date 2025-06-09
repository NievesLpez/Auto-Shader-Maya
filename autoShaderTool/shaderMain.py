"""
Main module for Auto Shader Tool - Compact Version

Author: Nieves Yashuang Lopez
Version: 1.0

"""
#------------------------------------------------
import maya.cmds as cmds
import os

#------------------------------------------------
class ArnoldTextureManager:
    def __init__(self):
        self.textureDirectory = ""
        self.texturePatterns = {
            'baseColor': ['basecolor', 'color', 'albedo', 'diffuse', 'bc', 'base_color', 'diff', 'col', 'base', 'alb'],
            'metalness': ['metalness', 'metallic', 'metal', 'mtl', 'met', 'metallic_map'],
            'roughness': ['roughness', 'rough', 'rgh', 'rghns', 'specularroughness', 'roughness_map'],
            'normal': ['normal', 'nrm', 'nor', 'nrml', 'normalgl', 'normal_map', 'nmap', 'normalmap'],
            'bump': ['bump', 'bmp', 'bumpmap', 'relief', 'bump_map'],
            'displacement': ['displacement', 'disp', 'height', 'dsp', 'hgt', 'heightmap', 'displace'],
            'specular': ['specular', 'spec', 'reflection', 'refl', 'specular_map', 'spec_color'],
            'emission': ['emission', 'emissive', 'glow', 'emit', 'emiss', 'selfillum', 'emission_map'],
            'ao': ['ao', 'ambient_occlusion', 'ambientocclusion', 'occlusion', 'ambientOcclusion'],
            'opacity': ['opacity', 'alpha', 'transparent', 'transparency', 'mask']
        }
        self.validExtensions = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.tga', '.exr', '.hdr', '.tx']

    def findTextures(self, directory):
        if not os.path.exists(directory):
            return {}

        textures = {}
        allFiles = []
        
        for root, _, files in os.walk(directory):
            for filename in files:
                if any(filename.lower().endswith(ext) for ext in self.validExtensions):
                    allFiles.append((filename, os.path.join(root, filename)))

        allFiles.sort()

        for filename, filePath in allFiles:
            nameLower = os.path.splitext(filename.lower())[0]
            for texType, patterns in self.texturePatterns.items():
                if texType in textures:
                    continue
                if any(self._patternMatch(pattern, nameLower) for pattern in patterns):
                    textures[texType] = filePath
                    break

        return textures

    def _patternMatch(self, pattern, filename):
        p, f = pattern.lower(), filename.lower()
        return (p == f or f.startswith(p + '_') or f.startswith(p + '-') or
                f.endswith('_' + p) or f.endswith('-' + p) or
                ('_' + p + '_') in f or ('-' + p + '-') in f)

    def getTextureDirectory(self):
        if self.textureDirectory and os.path.exists(self.textureDirectory):
            return self.textureDirectory
            
        scenePath = cmds.file(q=True, sceneName=True)
        if scenePath:
            projectDir = cmds.workspace(q=True, rootDirectory=True)
            if projectDir:
                sourceimagesPath = os.path.join(projectDir, 'sourceimages')
                if os.path.exists(sourceimagesPath):
                    self.textureDirectory = sourceimagesPath
                    return sourceimagesPath
        
        selectedDir = cmds.fileDialog2(fileMode=2, dialogStyle=2, caption="Select Texture Directory")
        if selectedDir:
            self.textureDirectory = selectedDir[0]
            return selectedDir[0]
        return None

#------------------------------------------------
class ArnoldShaderCreator:
    def __init__(self):
        self.textureManager = ArnoldTextureManager()
        self.useUdimMode = False
    
    def createShaderNetwork(self, shaderName, selection):
        if not selection:
            raise RuntimeError("No objects selected")
        
        if not cmds.pluginInfo('mtoa', query=True, loaded=True):
            cmds.loadPlugin('mtoa')
        
        textureDir = self.textureManager.getTextureDirectory()
        if not textureDir:
            raise RuntimeError("No texture directory selected")
        
        textures = self.textureManager.findTextures(textureDir)
        if not textures:
            raise RuntimeError(f"No textures found in: {textureDir}")
        
        # Create material
        materialName = self._getUniqueName(shaderName + "_SHD")
        material = cmds.shadingNode('aiStandardSurface', asShader=True, name=materialName)
        shadingGroup = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName + "_SG")
        cmds.connectAttr(material + ".outColor", shadingGroup + ".surfaceShader")
        
        # Connect textures
        textureCount = 0
        for texType, texturePath in textures.items():
            if self._connectTexture(texType, texturePath, shaderName, material, shadingGroup):
                textureCount += 1

        # Assign to objects
        for obj in selection:
            try:
                cmds.sets(obj, e=True, forceElement=shadingGroup)
            except:
                pass
        
        modeText = "UDIM" if self.useUdimMode else "Standard"
        cmds.inViewMessage(amg=f"Material '{material}' created successfully with {textureCount} textures ({modeText})",
                          pos='midCenter', fade=True)
        return material

    def _connectTexture(self, texType, texturePath, shaderName, material, shadingGroup):
        # Create file node
        fileNode = cmds.shadingNode('file', asTexture=True, name=f"{shaderName}_{texType}")
        cmds.setAttr(fileNode + ".fileTextureName", texturePath, type="string")
        cmds.setAttr(fileNode + ".uvTilingMode", 3 if self.useUdimMode else 0)
        
        # Direct place2d connection (simplified)
        place2d = cmds.shadingNode('place2dTexture', asUtility=True, name=f"{shaderName}_{texType}_place2d")
        cmds.connectAttr(place2d + ".outUV", fileNode + ".uvCoord")
        cmds.connectAttr(place2d + ".outUvFilterSize", fileNode + ".uvFilterSize")
        
        # Connection logic based on texture type
        if texType == 'baseColor':
            cmds.setAttr(fileNode + ".colorSpace", "sRGB", type="string")
            cmds.connectAttr(fileNode + ".outColor", material + ".baseColor")
        elif texType == 'emission':
            cmds.setAttr(fileNode + ".colorSpace", "sRGB", type="string")
            cmds.connectAttr(fileNode + ".outColor", material + ".emissionColor")
        elif texType in ['metalness', 'roughness', 'specular', 'opacity']:
            cmds.setAttr(fileNode + ".colorSpace", "Raw", type="string")
            attrMap = {'metalness': 'metalness', 'roughness': 'specularRoughness', 
                      'specular': 'specular', 'opacity': 'opacity'}
            cmds.connectAttr(fileNode + ".outColorR", material + "." + attrMap[texType])
        elif texType == 'normal':
            cmds.setAttr(fileNode + ".colorSpace", "Raw", type="string")
            try:
                normalNode = cmds.shadingNode('aiNormalMap', asUtility=True, name=f"{shaderName}_normal_normalMap")
                cmds.connectAttr(fileNode + ".outColor", normalNode + ".input")
                cmds.connectAttr(normalNode + ".outValue", material + ".normalCamera")
            except:
                bumpNode = cmds.shadingNode('aiBump2d', asUtility=True, name=f"{shaderName}_normal_bump2d")
                cmds.setAttr(bumpNode + ".bumpHeight", 1.0)
                cmds.connectAttr(fileNode + ".outColor", bumpNode + ".bumpMap", force=True)
                cmds.connectAttr(bumpNode + ".outValue", material + ".normalCamera")
        elif texType == 'bump':
            cmds.setAttr(fileNode + ".colorSpace", "Raw", type="string")
            bumpNode = cmds.shadingNode('aiBump2d', asUtility=True, name=f"{shaderName}_bump_bump2d")
            cmds.setAttr(bumpNode + ".bumpHeight", 0.3)
            cmds.connectAttr(fileNode + ".outColorR", bumpNode + ".bumpMap")
            cmds.connectAttr(bumpNode + ".outValue", material + ".normalCamera")
        elif texType == 'displacement':
            cmds.setAttr(fileNode + ".colorSpace", "Raw", type="string")
            dispNode = cmds.shadingNode('displacementShader', asShader=True, name=f"{shaderName}_disp_shader")
            cmds.setAttr(dispNode + ".scale", 0.1)
            cmds.connectAttr(fileNode + ".outAlpha", dispNode + ".displacement")
            cmds.connectAttr(dispNode + ".displacement", shadingGroup + ".displacementShader")
        else:
            return False
        
        return True

    def _getUniqueName(self, baseName):
        if not cmds.objExists(baseName):
            return baseName
        counter = 1
        while cmds.objExists(f"{baseName}_{counter}"):
            counter += 1
        return f"{baseName}_{counter}"

    def setUdimMode(self, enableUdim):
        self.useUdimMode = enableUdim

    def updateMaterialTextures(self, materialName, textureUpdates, useUdim=False):
        if not cmds.objExists(materialName):
            raise RuntimeError(f"Material '{materialName}' does not exist")
        
        updatedCount = 0
        for texType, texturePath in textureUpdates.items():
            if not os.path.exists(texturePath):
                continue
            
            # Find existing file node
            existingFileNode = self._findConnectedFileNode(materialName, texType)
            if existingFileNode:
                cmds.setAttr(existingFileNode + ".fileTextureName", texturePath, type="string")
                cmds.setAttr(existingFileNode + ".uvTilingMode", 3 if useUdim else 0)
                updatedCount += 1
        
        cmds.inViewMessage(amg=f"Updated {updatedCount} texture maps on '{materialName}'",
                          pos='midCenter', fade=True)

    def _findConnectedFileNode(self, material, texType):
        attrMap = {'baseColor': 'baseColor', 'metalness': 'metalness',
                  'roughness': 'specularRoughness', 'normal': 'normalCamera',
                  'specular': 'specular', 'emission': 'emissionColor', 'opacity': 'opacity'}
        
        if texType not in attrMap:
            return None
        
        connections = cmds.listConnections(f"{material}.{attrMap[texType]}", source=True, destination=False)
        if connections:
            for node in connections:
                if cmds.nodeType(node) == 'file':
                    return node
                upstream = cmds.listConnections(node, source=True, destination=False)
                if upstream:
                    for upNode in upstream:
                        if cmds.nodeType(upNode) == 'file':
                            return upNode
        return None

#------------------------------------------------
# Global functions
def createArnoldMaterial(materialName, textureDirectory=None, selection=None, useUdim=False):
    if selection is None:
        selection = cmds.ls(selection=True)
    
    creator = ArnoldShaderCreator()
    creator.setUdimMode(useUdim)
    
    if textureDirectory:
        creator.textureManager.textureDirectory = textureDirectory
    
    return creator.createShaderNetwork(materialName, selection)

def findTexturesInDirectory(directory):
    manager = ArnoldTextureManager()
    return manager.findTextures(directory)