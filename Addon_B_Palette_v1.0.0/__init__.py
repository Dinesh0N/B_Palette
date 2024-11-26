bl_info = {
    "name": "B Palette",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (2, 8, 0),
    "location": "File > Import/Export > B Palette",
    "description": "Import (GPL, ASE, ACO, PAL, CLR, CSV, CSS,TEXT), Export (GPL) Palettes",
    "category": "Import-Export",
}

import bpy
import os
import re
import struct
import csv

class PaletteParser:
    @staticmethod
    def parse_gpl(file_path):
        """Parse a GPL file and return colors and palette name."""
        colors = []
        palette_name = "Imported Palette"
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                if lines[0].strip() != "GIMP Palette":
                    raise ValueError("Not a valid GPL file.")

                for line in lines[1:]:
                    line = line.strip()
                    if line.startswith("Name:"):
                        palette_name = line.split(":", 1)[1].strip()
                    elif line and not line.startswith("#"):
                        try:
                            r, g, b, *name = line.split()
                            colors.append((float(r) / 255, float(g) / 255, float(b) / 255, 1.0))
                        except ValueError:
                            pass
        except Exception as e:
            print(f"Error reading GPL file: {e}")
        return palette_name, colors

    @staticmethod
    def parse_kpl(file_path):
        """Parse a KPL (KDE Palette) file."""
        colors = []
        palette_name = "Unnamed Palette"

        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith("#") or not line:
                        continue  # Ignore comments and empty lines
                    if line.startswith("Name="):
                        palette_name = line.split("=", 1)[1].strip()
                        continue
                    if line.startswith("["):
                        continue  # Ignore headers like [GimpPalette] or others
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            r = int(parts[0]) / 255.0
                            g = int(parts[1]) / 255.0
                            b = int(parts[2]) / 255.0
                            colors.append((r, g, b, 1.0))  # Alpha is always 1.0
                        except ValueError:
                            print(f"Skipping invalid color entry: {line}")
        except Exception as e:
            print(f"Error reading KPL file: {e}")

        return palette_name, colors
    
    @staticmethod
    def parse_ase(file_path):
        """Parse an ASE (Adobe Swatch Exchange) file."""
        colors = []
        palette_name = os.path.splitext(os.path.basename(file_path))[0]

        try:
            with open(file_path, "rb") as f:
                # Read header
                header = f.read(4)
                if header != b"ASEF" and header != b"ASE\x00":
                    raise ValueError("Not a valid ASE file.")

                version = struct.unpack(">HH", f.read(4))
                total_blocks = struct.unpack(">I", f.read(4))[0]

                # Process each block
                for _ in range(total_blocks):
                    block_type = struct.unpack(">H", f.read(2))[0]
                    block_length = struct.unpack(">I", f.read(4))[0]

                    if block_type == 0x0001:  # Color Entry
                        # Read color name
                        name_length = struct.unpack(">H", f.read(2))[0]
                        name = f.read(name_length * 2).decode("utf-16be").rstrip("\x00")

                        # Read color model
                        color_model = f.read(4).decode("ascii")
                        color_values = []

                        if color_model == "RGB ":
                            color_values = struct.unpack(">fff", f.read(12))
                        elif color_model == "CMYK":
                            color_values = struct.unpack(">ffff", f.read(16))[:3]  # Ignore K

                        # Skip padding
                        f.read(2)

                        # Append color to list
                        if color_values:
                            colors.append((color_values[0], color_values[1], color_values[2], 1.0))

                    else:
                        # Skip unsupported block
                        f.read(block_length)

        except Exception as e:
            print(f"Error parsing ASE file: {e}")

        return palette_name, colors

    @staticmethod
    def parse_aco(file_path):
        """Parse an ACO (Adobe Color) file and return colors and palette name."""
        colors = []
        palette_name = "ACO Palette"
        try:
            with open(file_path, "rb") as file:
                version = struct.unpack(">H", file.read(2))[0]
                if version not in (1, 2):
                    raise ValueError("Not a valid ACO file.")
                color_count = struct.unpack(">H", file.read(2))[0]

                for _ in range(color_count):
                    color_space = struct.unpack(">H", file.read(2))[0]
                    color_values = struct.unpack(">HHHH", file.read(8))
                    if color_space == 0:  # RGB
                        colors.append((
                            color_values[0] / 65535,
                            color_values[1] / 65535,
                            color_values[2] / 65535,
                            1.0,
                        ))
                    elif color_space in {1, 2, 3}:  # Unsupported spaces (CMYK, Lab, etc.)
                        continue
        except Exception as e:
            print(f"Error reading ACO file: {e}")
        return palette_name, colors

    @staticmethod
    def parse_pal(file_path):
        """Parse a PAL (JASC Palette) file and return colors and palette name."""
        colors = []
        palette_name = os.path.splitext(os.path.basename(file_path))[0]

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                if not lines[0].startswith("JASC-PAL"):
                    raise ValueError("Not a valid PAL file.")
                
                for line in lines[3:]:  # Skip the first 3 lines (header)
                    try:
                        r, g, b = map(int, line.split())
                        colors.append((r / 255.0, g / 255.0, b / 255.0, 1.0))
                    except ValueError:
                        pass
        except Exception as e:
            print(f"Error reading PAL file: {e}")

        return palette_name, colors

    @staticmethod
    def parse_clr(file_path):
        """Parse a CLR (Procreate) file and return colors and palette name."""
        colors = []
        palette_name = os.path.splitext(os.path.basename(file_path))[0]

        try:
            with open(file_path, "rb") as file:
                data = file.read()
                # CLR files store colors as RGBA (4 bytes each)
                color_count = len(data) // 4
                for i in range(color_count):
                    r, g, b, a = struct.unpack_from("BBBB", data, i * 4)
                    colors.append((r / 255.0, g / 255.0, b / 255.0, a / 255.0))
        except Exception as e:
            print(f"Error reading CLR file: {e}")

        return palette_name, colors

    @staticmethod
    def parse_csv(filepath):
        """Parse a CSV file to extract color codes."""
        colors = []
        palette_name = os.path.splitext(os.path.basename(filepath))[0]
        try:
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    for cell in row:
                        color = PaletteParser.detect_color_code(cell)
                        if color:
                            colors.append(color)
        except Exception as e:
            print(f"Error parsing CSV file: {e}")
        return palette_name, colors

    @staticmethod
    def parse_css(filepath):
        """Parse a CSS file to extract color codes."""
        colors = []
        palette_name = os.path.splitext(os.path.basename(filepath))[0]
        try:
            with open(filepath, encoding="utf-8") as cssfile:
                for line in cssfile:
                    color = PaletteParser.detect_color_code(line)
                    if color:
                        colors.append(color)
        except Exception as e:
            print(f"Error parsing CSS file: {e}")
        return palette_name, colors

    @staticmethod
    def parse_txt(file_path):
        """Parse a TXT file to extract color codes."""
        colors = []
        palette_name = os.path.splitext(os.path.basename(file_path))[0]

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    color = PaletteParser.detect_color_code(line)
                    if color:
                        colors.append(color)
        except Exception as e:
            print(f"Error parsing TXT file: {e}")

        return palette_name, colors
    
    @staticmethod
    def detect_color_code(text):
        """Detect color codes (HEX, RGB, HSL, FF-prefixed HEX) in a given text."""
        # FF-prefixed HEX: Match and strip the FF prefix
        ff_hex_match = re.search(r"FF([0-9a-fA-F]{6})", text)
        # Standard HEX: Support with or without '#' prefix
        hex_match = re.search(r"(#?[0-9a-fA-F]{6}|#?[0-9a-fA-F]{3})", text)
        rgb_match = re.search(r"rgb\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\)", text)
        hsl_match = re.search(r"hsl\((\d{1,3}),\s*(\d{1,3})%,\s*(\d{1,3})%\)", text)

        if ff_hex_match:
            hex_code = f"#{ff_hex_match.group(1)}"  # Strip "FF" and prepend "#"
            return PaletteParser.hex_to_rgb(hex_code)
        elif hex_match:
            hex_code = hex_match.group(1)
            if not hex_code.startswith("#"):
                hex_code = f"#{hex_code}"
            return PaletteParser.hex_to_rgb(hex_code)
        elif rgb_match:
            r, g, b = map(int, rgb_match.groups())
            return r / 255, g / 255, b / 255, 1.0
        elif hsl_match:
            h, s, l = map(int, hsl_match.groups())
            return PaletteParser.hsl_to_rgb(h, s, l)
        return None

    @staticmethod
    def hex_to_rgb(hex_code):
        """Convert HEX to RGB."""
        hex_code = hex_code.lstrip("#")
        if len(hex_code) == 3:
            hex_code = "".join([c * 2 for c in hex_code])
        r, g, b = tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))
        return r / 255, g / 255, b / 255, 1.0

    @staticmethod
    def hsl_to_rgb(h, s, l):
        """Convert HSL to RGB."""
        s /= 100
        l /= 100

        def hue_to_rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1 / 6:
                return p + (q - p) * 6 * t
            if t < 1 / 2:
                return q
            if t < 2 / 3:
                return p + (q - p) * (2 / 3 - t) * 6
            return p

        q = l + s - l * s if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h / 360 + 1 / 3)
        g = hue_to_rgb(p, q, h / 360)
        b = hue_to_rgb(p, q, h / 360 - 1 / 3)
        return r, g, b, 1.0

class PaletteImporter:
    @staticmethod
    def create_palette(palette_name, colors):
        """Create a Blender palette with the given name and colors."""
        palette = bpy.data.palettes.new(palette_name)
        for color in colors:
            color_entry = palette.colors.new()
            # Use only the RGB values (exclude alpha)
            color_entry.color = color[:3]

class PaletteImportOperator(bpy.types.Operator):
    """Operator for importing palettes."""
    bl_idname = "palette.import"
    bl_label = "Import Palette"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(
        default="*.gpl;*.ase;*.aco;*.pal;*.clr;*.csv;*.css;*.txt",
        options={'HIDDEN'}
    )

    def execute(self, context):
        if self.filepath.lower().endswith(".gpl"):
            palette_name, colors = PaletteParser.parse_gpl(self.filepath)
        elif self.filepath.lower().endswith(".ase"):
            palette_name, colors = PaletteParser.parse_ase(self.filepath)
        elif self.filepath.lower().endswith(".aco"):
            palette_name, colors = PaletteParser.parse_aco(self.filepath)
        elif self.filepath.lower().endswith(".pal"):
            palette_name, colors = PaletteParser.parse_pal(self.filepath)
        elif self.filepath.lower().endswith(".clr"):
            palette_name, colors = PaletteParser.parse_clr(self.filepath)
        elif self.filepath.lower().endswith(".csv"):
            palette_name, colors = PaletteParser.parse_csv(self.filepath)
        elif self.filepath.lower().endswith(".css"):
            palette_name, colors = PaletteParser.parse_css(self.filepath)
        elif self.filepath.lower().endswith(".txt"):
            palette_name, colors = PaletteParser.parse_txt(self.filepath)

        else:
            self.report({'ERROR'}, "Unsupported file format.")
            return {'CANCELLED'}

        if colors:
            PaletteImporter.create_palette(palette_name, colors)
            self.report({'INFO'}, f"Imported palette: {palette_name}")
        else:
            self.report({'ERROR'}, "Failed to import palette.")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_import(self, context):
    self.layout.operator(PaletteImportOperator.bl_idname, text="B Palette")


class GPLExporter:
    @staticmethod
    def export_gpl(file_path, palette):
        """Export the selected palette to a GPL file."""
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                # Write GPL header
                file.write("GIMP Palette\n")
                file.write(f"Name: {palette.name}\n")
                file.write("#\n")

                # Write color entries
                for color in palette.colors:
                    r, g, b = [int(c * 255) for c in color.color]
                    file.write(f"{r:3d} {g:3d} {b:3d} Untitled\n")
        except Exception as e:
            print(f"Error exporting GPL file: {e}")
            raise

class PaletteExportGPL(bpy.types.Operator):
    """Export Blender Palette to GPL Format"""
    bl_idname = "export_palette.gpl"
    bl_label = "Export GPL Palette"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.gpl", options={'HIDDEN'})
    palette_name: bpy.props.EnumProperty(
        name="Palette",
        description="Choose a palette to export",
        items=lambda self, context: [
            (p.name, p.name, "") for p in bpy.data.palettes
        ],
    )

    def execute(self, context):
        # Get the selected palette
        palette = bpy.data.palettes.get(self.palette_name)
        if not palette:
            self.report({'ERROR'}, f"Palette '{self.palette_name}' not found.")
            return {'CANCELLED'}

        # Export the palette
        try:
            GPLExporter.export_gpl(self.filepath, palette)
            self.report({'INFO'}, f"Exported palette: {self.filepath}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to export palette: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        if not bpy.data.palettes:
            self.report({'ERROR'}, "No palettes available to export.")
            return {'CANCELLED'}

        # Default file name
        self.filepath = os.path.join(
            os.path.expanduser("~"), f"{self.palette_name or 'palette'}.gpl"
        )
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}  # Correct return value

def menu_func_export(self, context):
    self.layout.operator(PaletteExportGPL.bl_idname, text="B Palette(.gpl)")

def register():
    bpy.utils.register_class(PaletteImportOperator)
    bpy.utils.register_class(PaletteExportGPL)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(PaletteImportOperator)
    bpy.utils.unregister_class(PaletteExportGPL)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
