"""
UI module for Auto Shader Tool 

Author: Nieves Yashuang Lopez
Version: 1.0

"""

import maya.cmds as cmds
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, QUrl
from PySide2.QtGui import QDragEnterEvent, QDropEvent
import os
from shiboken2 import wrapInstance
try:
    from . import shaderMain as main
except ImportError:
    import shaderMain as main

#------------------------------------------------

def getMayaWindow():
    try:
        from maya import OpenMayaUI
        return wrapInstance(int(OpenMayaUI.MQtUtil.mainWindow()), QWidget)
    except:
        return None

#------------------------------------------------

class DragDropLineEdit(QLineEdit):
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.drag_callback = callback
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and len(urls) == 1:
                file_path = urls[0].toLocalFile()
                if os.path.isdir(file_path):
                    event.acceptProposedAction()
                    self.setStyleSheet(self.styleSheet() + "border: 2px solid #4682B4;")
                    return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.styleSheet().replace("border: 2px solid #4682B4;", ""))
        super().dragLeaveEvent(event)
    
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and len(urls) == 1:
                file_path = urls[0].toLocalFile()
                if os.path.isdir(file_path):
                    self.setText(file_path)
                    self.setStyleSheet(self.styleSheet().replace("border: 2px solid #4682B4;", ""))
                    if self.drag_callback:
                        self.drag_callback(file_path)
                    event.acceptProposedAction()
                    return
        event.ignore()

class AutoShaderTool(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent or getMayaWindow())
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Auto Shader Tool")
        self.setFixedSize(650, 950)
        
        # Variables
        self.textureDirectory = ""
        self.useUdim = False
        self.updateUseUdim = False
        
        # Initialize shader creator
        try:
            self.shaderCreator = main.ArnoldShaderCreator()
        except:
            self.shaderCreator = None
        
        self.setupUi()
        self.setupConnections()

    def setupUi(self):
        self.setStyleSheet("""
            QDialog { background-color: #2e2e2e; color: white; }
            QPushButton { background-color: #4a4a4a; color: white; border-radius: 5px; 
                         padding: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #6a6a6a; }
            QPushButton#createButton { background-color: #4682B4; }
            QPushButton#createButton:hover { background-color: #5A9BD5; }
            QLineEdit { background-color: #3a3a3a; color: white; border: 1px solid #5a5a5a; 
                       border-radius: 3px; padding: 5px; }
            DragDropLineEdit { background-color: #3a3a3a; color: white; border: 1px solid #5a5a5a; 
                              border-radius: 3px; padding: 5px; }
            QGroupBox { font-weight: bold; border: 2px solid #5a5a5a; border-radius: 5px; 
                       margin-top: 10px; padding-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QRadioButton { color: white; spacing: 8px; }
            QRadioButton::indicator { width: 16px; height: 16px; }
            QRadioButton::indicator:unchecked { border: 2px solid #5a5a5a; border-radius: 8px; 
                                              background-color: #2a2a2a; }
            QRadioButton::indicator:checked { border: 2px solid #4682B4; border-radius: 8px; 
                                            background-color: #4682B4; }
            QLabel#dragHint { color: #888; font-style: italic; font-size: 11px; padding: 2px; }
        """)
        
        layout = QVBoxLayout(self)
        
        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self.createMaterialTab(), "Create material")
        tabs.addTab(self.createUpdateTab(), "Update textures")
        layout.addWidget(tabs)

    def createMaterialTab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Status
        self.statusLabel = QLabel("Please select a texture directory")
        self.statusLabel.setStyleSheet("padding: 10px; background-color: #3a3a3a;")
        layout.addWidget(self.statusLabel)
        
        # Directory section
        dirGroup = QGroupBox("Texture Directory")
        dirLayout = QVBoxLayout(dirGroup)
        
        dirRow = QHBoxLayout()
        self.directoryEdit = DragDropLineEdit(callback=self.onDirectoryDropped)
        self.directoryEdit.setPlaceholderText("Select texture directory or drag & drop folder here...")
        self.browseDirBtn = QPushButton("Browse")
        dirRow.addWidget(self.directoryEdit)
        dirRow.addWidget(self.browseDirBtn)
        dirLayout.addLayout(dirRow)
        
        # UV Mode
        uvGroup = QGroupBox("UV Mode")
        uvLayout = QHBoxLayout(uvGroup)
        self.uvButtonGroup = QButtonGroup()
        self.singleUvRadio = QRadioButton("Single UV (0-1)")
        self.udimRadio = QRadioButton("UDIM Tiles")
        self.singleUvRadio.setChecked(True)
        self.uvButtonGroup.addButton(self.singleUvRadio, 0)
        self.uvButtonGroup.addButton(self.udimRadio, 1)
        uvLayout.addWidget(self.singleUvRadio)
        uvLayout.addWidget(self.udimRadio)
        uvLayout.addStretch()
        dirLayout.addWidget(uvGroup)
        
        self.autoDetectBtn = QPushButton("Auto Detect Textures")
        dirLayout.addWidget(self.autoDetectBtn)
        layout.addWidget(dirGroup)
        
        # Material creation
        createGroup = QGroupBox("Create Material")
        createLayout = QVBoxLayout(createGroup)
        
        nameRow = QHBoxLayout()
        nameRow.addWidget(QLabel("Material Name:"))
        self.materialNameEdit = QLineEdit()
        self.materialNameEdit.setPlaceholderText("Enter material name")
        nameRow.addWidget(self.materialNameEdit)
        createLayout.addLayout(nameRow)
        
        # Texture fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(420)
        textureWidget = QWidget()
        textureLayout = QVBoxLayout(textureWidget)
        
        # Create texture fields dynamically
        self.textureTypes = ['diffuse', 'normal', 'roughness', 'metallic', 'specular', 
                             'opacity', 'emission', 'ao', 'displacement']
        self.textureLabels = ['Base Color:', 'Normal:', 'Roughness:', 'Metallic:', 
                              'Specular:', 'Opacity:', 'Emission:', 'AO:', 'Displacement:']
        
        for texType, label in zip(self.textureTypes, self.textureLabels):
            self.createTextureField(label, textureLayout, texType)
        
        scroll.setWidget(textureWidget)
        createLayout.addWidget(scroll)
        
        # Buttons
        btnRow = QHBoxLayout()
        self.clearPathsBtn = QPushButton("Clear All")
        self.createMaterialBtn = QPushButton("Create Material")
        self.createMaterialBtn.setObjectName("createButton")
        btnRow.addWidget(self.clearPathsBtn)
        btnRow.addWidget(self.createMaterialBtn)
        createLayout.addLayout(btnRow)
        
        layout.addWidget(createGroup)
        return widget

    def createUpdateTab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Update status
        self.updateStatusLabel = QLabel("Select an object with a material to update")
        self.updateStatusLabel.setStyleSheet("padding: 10px; background-color: #3a3a3a;")
        layout.addWidget(self.updateStatusLabel)
        
        # Material selection
        matGroup = QGroupBox("Select material to update")
        matLayout = QVBoxLayout(matGroup)
        
        selectRow = QHBoxLayout()
        selectRow.addWidget(QLabel("Selected Object:"))
        self.selectedObjectLabel = QLabel("No object selected")
        self.selectedObjectLabel.setStyleSheet("color: #ccc; font-style: italic;")
        selectRow.addWidget(self.selectedObjectLabel)
        selectRow.addStretch()
        self.refreshSelectionBtn = QPushButton("Refresh")
        self.refreshSelectionBtn.setMaximumWidth(100)
        selectRow.addWidget(self.refreshSelectionBtn)
        matLayout.addLayout(selectRow)
        
        self.currentMaterialLabel = QLabel("Material: None detected")
        self.currentMaterialLabel.setStyleSheet("color: #4682B4; font-weight: bold;")
        matLayout.addWidget(self.currentMaterialLabel)
        layout.addWidget(matGroup)
        
        # Update directory
        updateDirGroup = QGroupBox("Update Texture Directory")
        updateDirLayout = QVBoxLayout(updateDirGroup)
        
        updateDirRow = QHBoxLayout()
        self.updateDirectoryEdit = DragDropLineEdit(callback=self.onUpdateDirectoryDropped)
        self.updateDirectoryEdit.setPlaceholderText("Select directory with new textures or drag & drop folder here")
        self.updateBrowseDirBtn = QPushButton("Browse")
        updateDirRow.addWidget(self.updateDirectoryEdit)
        updateDirRow.addWidget(self.updateBrowseDirBtn)
        updateDirLayout.addLayout(updateDirRow)
        
        # Update UV Mode
        updateUvGroup = QGroupBox("UV Mode")
        updateUvLayout = QHBoxLayout(updateUvGroup)
        self.updateUvButtonGroup = QButtonGroup()
        self.updateSingleUvRadio = QRadioButton("Single UV (0-1)")
        self.updateUdimRadio = QRadioButton("UDIM Tiles")
        self.updateSingleUvRadio.setChecked(True)
        self.updateUvButtonGroup.addButton(self.updateSingleUvRadio, 0)
        self.updateUvButtonGroup.addButton(self.updateUdimRadio, 1)
        updateUvLayout.addWidget(self.updateSingleUvRadio)
        updateUvLayout.addWidget(self.updateUdimRadio)
        updateUvLayout.addStretch()
        updateDirLayout.addWidget(updateUvGroup)
        
        self.autoDetectUpdateBtn = QPushButton("Auto Detect New Textures")
        self.autoDetectUpdateBtn.setStyleSheet("background-color: #5A9BD5; padding: 10px;")
        updateDirLayout.addWidget(self.autoDetectUpdateBtn)
        layout.addWidget(updateDirGroup)
        
        # Update textures
        updateGroup = QGroupBox("Update Texture Maps")
        updateLayout = QVBoxLayout(updateGroup)
        
        updateScroll = QScrollArea()
        updateScroll.setWidgetResizable(True)
        updateScroll.setMaximumHeight(350)
        updateWidget = QWidget()
        updateTexLayout = QVBoxLayout(updateWidget)
        
        # Create update texture fields
        for texType, label in zip(self.textureTypes, self.textureLabels):
            self.createTextureField(label, updateTexLayout, f"update_{texType}")
        
        updateScroll.setWidget(updateWidget)
        updateLayout.addWidget(updateScroll)
        
        # Update buttons - CAMBIADO PARA SER IGUAL A LA PRIMERA PESTAÑA
        updateBtnRow = QHBoxLayout()
        self.clearUpdatePathsBtn = QPushButton("Clear All")
        self.updateMaterialBtn = QPushButton("Update Material")
        self.updateMaterialBtn.setObjectName("createButton")
        updateBtnRow.addWidget(self.clearUpdatePathsBtn)
        updateBtnRow.addWidget(self.updateMaterialBtn)
        updateLayout.addLayout(updateBtnRow)
        
        layout.addWidget(updateGroup)
        
        return widget

    def createTextureField(self, labelText, parentLayout, fieldName):
        row = QHBoxLayout()
        label = QLabel(labelText)
        label.setMinimumWidth(80)
        lineEdit = QLineEdit()
        lineEdit.setPlaceholderText("Auto-detected or manually select")
        browseBtn = QPushButton("...")
        browseBtn.setMaximumWidth(30)
        
        row.addWidget(label)
        row.addWidget(lineEdit)
        row.addWidget(browseBtn)
        parentLayout.addLayout(row)
        
        # Store references
        setattr(self, f"{fieldName}PathEdit", lineEdit)
        setattr(self, f"{fieldName}BrowseBtn", browseBtn)

    def setupConnections(self):
        # Create tab connections
        self.browseDirBtn.clicked.connect(self.browseDirectory)
        self.autoDetectBtn.clicked.connect(self.autoDetectTextures)
        self.createMaterialBtn.clicked.connect(self.createMaterial)
        self.clearPathsBtn.clicked.connect(self.clearAllPaths)
        self.uvButtonGroup.buttonClicked.connect(self.onUvModeChanged)
        
        # Update tab connections
        self.refreshSelectionBtn.clicked.connect(self.refreshSelectedObject)
        self.updateBrowseDirBtn.clicked.connect(self.browseUpdateDirectory)
        self.autoDetectUpdateBtn.clicked.connect(self.autoDetectForUpdate)
        self.clearUpdatePathsBtn.clicked.connect(self.clearUpdatePaths)
        self.updateMaterialBtn.clicked.connect(self.updateExistingMaterial)
        self.updateUvButtonGroup.buttonClicked.connect(self.onUpdateUvModeChanged)
        
        # Browse buttons - dynamic connection
        for texType in self.textureTypes:
            getattr(self, f"{texType}BrowseBtn").clicked.connect(
                lambda checked=False, t=texType: self.browseTexture(getattr(self, f"{t}PathEdit")))
            getattr(self, f"update_{texType}BrowseBtn").clicked.connect(
                lambda checked=False, t=texType: self.browseTexture(getattr(self, f"update_{t}PathEdit"), True))

    # Callbacks para drag & drop
    def onDirectoryDropped(self, directory):
        self.textureDirectory = directory
        self.updateStatus(f"Directory: {os.path.basename(directory)}")
        # Auto-detectar texturas si el shader creator está disponible
        if self.shaderCreator:
            self.autoDetectTextures()

    def onUpdateDirectoryDropped(self, directory):
        self.updateUpdateStatus(f"Update directory: {os.path.basename(directory)}")
        # Auto-detectar texturas para update si el shader creator está disponible
        if self.shaderCreator:
            self.autoDetectForUpdate()

    # Main functionality methods (simplified)
    def browseDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Texture Directory")
        if directory:
            self.textureDirectory = directory
            self.directoryEdit.setText(directory)
            self.updateStatus(f"Directory: {os.path.basename(directory)}")

    def browseUpdateDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Update Directory")
        if directory:
            self.updateDirectoryEdit.setText(directory)
            self.updateUpdateStatus(f"Update directory: {os.path.basename(directory)}")

    def browseTexture(self, lineEdit, forUpdate=False):
        startDir = (self.updateDirectoryEdit.text() if forUpdate else self.textureDirectory) or ""
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Select Texture File", startDir,
            "Image Files (*.jpg *.jpeg *.png *.tif *.tiff *.tga *.exr *.hdr *.tx)")
        if filePath:
            lineEdit.setText(filePath)
            if forUpdate and not self.updateDirectoryEdit.text():
                self.updateDirectoryEdit.setText(os.path.dirname(filePath))
            elif not forUpdate and not self.textureDirectory:
                self.textureDirectory = os.path.dirname(filePath)
                self.directoryEdit.setText(self.textureDirectory)

    def onUvModeChanged(self, button):
        self.useUdim = (button == self.udimRadio)

    def onUpdateUvModeChanged(self, button):
        self.updateUseUdim = (button == self.updateUdimRadio)

    def autoDetectTextures(self):
        if not self.shaderCreator or not self.textureDirectory:
            self.updateStatus("Please select a texture directory")
            return
        
        self.enhanceTexturePatterns()
        textures = self.shaderCreator.textureManager.findTextures(self.textureDirectory)
        
        # Map texture types
        typeMap = {'baseColor': 'diffuse', 'metalness': 'metallic'}
        found = []
        
        # Clear all fields first
        for field in self.textureTypes:
            getattr(self, f"{field}PathEdit").clear()
        
        # Fill found textures
        for texType, path in textures.items():
            fieldName = typeMap.get(texType, texType)
            if hasattr(self, f"{fieldName}PathEdit"):
                getattr(self, f"{fieldName}PathEdit").setText(path)
                found.append(texType)
        
        # Only show message if textures found or error
        if found:
            self.updateStatus(f"Found {len(found)} textures")
        else:
            self.updateStatus("No textures found in directory")

    def autoDetectForUpdate(self):
        updateDir = self.updateDirectoryEdit.text().strip()
        if not self.shaderCreator or not updateDir or not os.path.exists(updateDir):
            self.updateUpdateStatus("Please select a valid texture directory")
            return
        
        self.enhanceTexturePatterns()
        textures = self.shaderCreator.textureManager.findTextures(updateDir)
        
        typeMap = {'baseColor': 'diffuse', 'metalness': 'metallic'}
        found = []
        
        # Clear all update fields first
        for field in self.textureTypes:
            getattr(self, f"update_{field}PathEdit").clear()
        
        # Fill found textures
        for texType, path in textures.items():
            fieldName = typeMap.get(texType, texType)
            if hasattr(self, f"update_{fieldName}PathEdit"):
                getattr(self, f"update_{fieldName}PathEdit").setText(path)
                found.append(texType)
        
        # Only show message if textures found or error
        if found:
            self.updateUpdateStatus(f"Found {len(found)} textures for update")
        else:
            self.updateUpdateStatus("No textures found for update")

    def clearAllPaths(self):
        for field in self.textureTypes:
            getattr(self, f"{field}PathEdit").clear()

    def clearUpdatePaths(self):
        for field in self.textureTypes:
            getattr(self, f"update_{field}PathEdit").clear()

    def createMaterial(self):
        if not self.shaderCreator:
            self.updateStatus("Shader creator not initialized")
            return
        
        materialName = self.materialNameEdit.text().strip()
        selection = cmds.ls(selection=True)
        
        if not materialName:
            self.updateStatus("Please enter material name")
            return
        if not selection:
            self.updateStatus("Please select objects")
            return
        if not self.textureDirectory:
            self.updateStatus("Please choose texture directory")
            return
        
        try:
            if not cmds.pluginInfo('mtoa', query=True, loaded=True):
                cmds.loadPlugin('mtoa')
            
            self.shaderCreator.useUdimMode = self.useUdim
            self.shaderCreator.textureManager.textureDirectory = self.textureDirectory
            material = self.shaderCreator.createShaderNetwork(materialName, selection)
            
            # Success message handled by shader creator
            self.updateStatus(f"Material '{material}' created successfully!")
        except Exception as e:
            self.updateStatus(f"Error: {str(e)}")

    def refreshSelectedObject(self):
        selection = cmds.ls(selection=True)
        if not selection:
            self.selectedObjectLabel.setText("No object selected")
            self.currentMaterialLabel.setText("Material: None detected")
            self.updateUpdateStatus("Please select an object with a material")
            return
        
        obj = selection[0]
        self.selectedObjectLabel.setText(obj)
        self.selectedObjectLabel.setStyleSheet("color: #4682B4; font-weight: bold;")
        
        material = self.getObjectMaterial(obj)
        if material:
            self.currentMaterialLabel.setText(f"Material: {material}")
            self.currentMaterialLabel.setStyleSheet("color: #5A9BD5; font-weight: bold;")
            self.updateUpdateStatus(f"Ready to update '{material}'")
        else:
            self.currentMaterialLabel.setText("Material: None detected")
            self.currentMaterialLabel.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            self.updateUpdateStatus("No material found on selected object")

    def updateExistingMaterial(self):
        if not self.shaderCreator:
            self.updateUpdateStatus("Shader creator not initialized")
            return
        
        selection = cmds.ls(selection=True)
        if not selection:
            self.updateUpdateStatus("Please select an object")
            return
        
        material = self.getObjectMaterial(selection[0])
        if not material:
            self.updateUpdateStatus("No material found on selected object")
            return
        
        # Collect texture updates
        textureUpdates = {}
        typeMap = {'diffuse': 'baseColor', 'metallic': 'metalness'}
        
        for field in self.textureTypes:
            path = getattr(self, f"update_{field}PathEdit").text().strip()
            if path and os.path.exists(path):
                texType = typeMap.get(field, field)
                textureUpdates[texType] = path
        
        if not textureUpdates:
            self.updateUpdateStatus("No valid texture paths specified")
            return
        
        try:
            self.shaderCreator.updateMaterialTextures(material, textureUpdates, self.updateUdimRadio.isChecked())
    
            self.updateUpdateStatus(f"Material '{material}' updated successfully!")
            self.clearUpdatePaths()
        except Exception as e:
            self.updateUpdateStatus(f"Error: {str(e)}")

    def getObjectMaterial(self, obj):
        try:
            shape = cmds.listRelatives(obj, shapes=True)[0]
            shadingGroups = cmds.listConnections(shape, type='shadingEngine')
            if shadingGroups:
                materials = cmds.listConnections(shadingGroups[0] + '.surfaceShader')
                if materials:
                    return materials[0]
        except:
            pass
        return None

    def enhanceTexturePatterns(self):
        if self.shaderCreator and self.shaderCreator.textureManager:
            enhancedPatterns = {
                'baseColor': ['basecolor', 'color', 'albedo', 'diffuse', 'bc', 'base_color', 'diff', 'col', 'base', 'alb'],
                'metalness': ['metalness', 'metallic', 'metal', 'mtl', 'met', 'metallic_map'],
                'roughness': ['roughness', 'rough', 'rgh', 'rghns', 'specularroughness', 'roughness_map'],
                'normal': ['normal', 'nrm', 'nor', 'nrml', 'normalgl', 'normal_map', 'nmap', 'normalmap'],
                'specular': ['specular', 'spec', 'reflection', 'refl', 'specular_map'],
                'opacity': ['opacity', 'alpha', 'transparent', 'transparency', 'mask'],
                'emission': ['emission', 'emissive', 'glow', 'emit', 'emiss', 'selfillum'],
                'ao': ['ao', 'ambient_occlusion', 'ambientocclusion', 'occlusion'],
                'displacement': ['displacement', 'disp', 'height', 'dsp', 'hgt', 'heightmap']
            }
            self.shaderCreator.textureManager.texturePatterns.update(enhancedPatterns)

    def updateStatus(self, message):
        self.statusLabel.setText(message)

    def updateUpdateStatus(self, message):
        if hasattr(self, 'updateStatusLabel'):
            self.updateStatusLabel.setText(message)

# Global functions
def showAutoShaderTool():
    global autoShaderToolWindow
    try:
        autoShaderToolWindow.close()
        autoShaderToolWindow.deleteLater()
    except:
        pass
    autoShaderToolWindow = AutoShaderTool()
    autoShaderToolWindow.show()

if __name__ == "__main__":
    showAutoShaderTool()
