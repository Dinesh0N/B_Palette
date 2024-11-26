# B Palette

---
[![Software License](https://img.shields.io/badge/license-GPL-brightgreen.svg?style=flat-square)](LICENSE.md)
<p>
    <a href="#table"><img alt="Blender"
            src="https://img.shields.io/badge/Blender-gray?logo=blender&style=flat-square" /></a>
</p>

## B Palette Addon
 B Palette is a versatile tool for Blender users who work with color palettes. It allows seamless import and export of palettes in multiple formats. The addon supports importing GPL, ASE, ACO, PAL, CLR, CSV, CSS, and TXT files, enabling you to bring in color schemes from external tools like Adobe Photoshop, GIMP, and Procreate. You can also export palettes in the GPL format for use in other applications. 

    Location: File > Import/Export > B Palette

![B palette_Page 1](https://github.com/user-attachments/assets/78db5df2-3d20-462c-928f-058c56fce4c9)

---

## How to Use

 **Importing Palettes:**
- Go to File > Import > B Palette.
- Select a file in a supported format (GPL, ASE, ACO, PAL, CLR, CSV, CSS, and TXT).
- The palette will be imported and added to Blender's palette list.

 **Exporting Palettes:**
- Go to File > Export > B Palette.
- Choose the palette you want to export from the dropdown menu.
- Save the palette as a GPL file for external use.

---
## **CSV File Structure**
A **CSV (Comma-Separated Values)** file can support various formats to describe colors. Supported structures include:

1. **Hexadecimal Notation (with or without `#`):**
   ```
   #FF5733, #C70039, #900C3F
   FFC300, DAF7A6, 581845
   ```

2. **RGB Values (0–255):**
   ```
   255, 87, 51
   199, 0, 57
   144, 12, 63
   ```

3. **Mixed (HEX and RGB):**
   ```
   #FF5733
   199, 0, 57
   #DAF7A6
   ```

- **Parsing Notes:**  
  Each row or clum can represent a single color, or multiple comma-separated color codes. Any non-color text is ignored.  

---

## **CSS File Structure**
A **CSS (Cascading Style Sheets)** file can contain color codes in styles or inline formats. Supported formats include:

1. **Hexadecimal Colors:**
   ```css
   background-color: #FF5733;
   color: #C70039;
   ```

2. **RGB Colors:**
   ```css
   border-color: rgb(255, 87, 51);
   ```

3. **HSL Colors (Converted to RGB):**
   ```css
   background: hsl(340, 100%, 50%);
   ```

4. **HEX Prefixed with `FF` (Stripping the `FF`):**
   ```css
   border: 1px solid FF5733;
   ```

- **Parsing Notes:**  
  Any valid color in a CSS file, regardless of the surrounding properties, is detected. Commented lines (e.g., `/* this is a comment */`) and other non-color data are ignored.

---

## **TXT File Structure**
A **TXT** file supports flexible formats to store color codes. Supported structures include:

1. **Hexadecimal Colors:**
   ```
   #FF5733
   C70039
   ```

2. **RGB Values:**
   ```
   255, 87, 51
   199 0 57
   ```

3. **HSL Values (Converted to RGB):**
   ```
   hsl(340, 100%, 50%)
   ```

4. **Prefixed HEX Colors (`FF` prefix):**
   ```
   FF5733
   ```

5. **Mixed Formats:**
   ```
   #FF5733
   255, 87, 51
   hsl(340, 100%, 50%)
   ```

- **Parsing Notes:**  
  Each line in the TXT file is scanned for a valid color. Unsupported lines or text are skipped.  
---
