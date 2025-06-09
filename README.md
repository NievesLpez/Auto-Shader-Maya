# Auto Shader Tool for Maya

# Description

An advanced Maya tool for automating Arnold shader networks with intelligent texture mapping and UDIM support.

---

## Features

- Automatic texture detection
  
- UDIM and single UV support
  
- Drag & drop folder functionality
  
- Material creation and updating

---

## Requirements

- Maya 2020 or newer
  
- Arnold for Maya
  
- PySide2
  
- Python 3.7+
  
---

# Usage

## Create new materials

1. Select texture source:

- Drag and drop texture folder directly into the directory field, OR
- Use the "Browse" button to manually select directory


2. Choose UV mode:

- Select Single UV (0-1) for standard UV layout
- Select UDIM Tiles for UDIM workflow


3. Detect textures:

- Press "Auto Detect" to automatically find textures
- Found textures will appear next to their respective map names
- If auto-detection fails, manually select textures using the "..." button


4. Create material:

- Select your target object(s) in Maya
- Enter a material name
- Click "Create Material"
---
<img src="https://github.com/user-attachments/assets/f707b757-58f9-45c3-8641-517a21d2e972" width="400" alt="Create Material Interface" style="border: 1px solid #ddd; border-radius: 8px; margin: 20px 0;">

---

## Update textures

1. Select target:

- Select the object with the material you want to update
- Press "Refresh" to detect the current material


2. Choose new textures:

- Drag and drop the new texture folder, OR
- Manually browse to the new texture directory
- Press "Auto Detect" to find new textures


3. Update material:

- Click "Update Material" to apply new textures to the selected object
  
---

<img src="https://github.com/user-attachments/assets/e0e9e0db-a10c-48ee-83b2-4943197c166b" width="400" alt="Update Material Interface" style="border: 1px solid #ddd; border-radius: 8px; margin: 20px 0;">

---

## Module installation

1. Download the autoShaderTool folder
  
3. Copy to your Maya version scripts directory

> Windows: Documents/maya/[version]/scripts/
> 
> Mac: ~/Library/Preferences/Autodesk/maya/[version]/scripts/
> 
> Linux: ~/maya/[version]/scripts/

5. Run in Maya Script Editor the following ( Drag and drop the code to your Maya shelf for quick access )

```python
import autoShaderTool
autoShaderTool.showTool()
```
---

## Author

Author: Nieves Yashuang Lopez

Email: nieveslpez.p@gmail.com

## Bug report

Encountered any bugs, errors or have any requests? Feel free to reach out.
Please include image of the error displayed.

## License

autoShaderTool is licensed under the MIT License.
