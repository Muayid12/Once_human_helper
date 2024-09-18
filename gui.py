from pathlib import Path
from tkinter import Canvas, Entry, Button, PhotoImage, font,scrolledtext , messagebox
import tkinter as tk
import os
import sys


#-----------------------------------------------------------------calculator------------------------------------------------------------------------------------------
def open_calculator():
    def evaluate_expression():
        try:
            result = eval(entry_calculator.get())
            result_text = str(result)
            entry_calculator.config(state=tk.NORMAL)
            entry_calculator.delete(0, tk.END)
            entry_calculator.insert(tk.END, result_text)
            entry_calculator.config(fg='white')  # Set text color to white
            entry_calculator.config(state=tk.DISABLED)
        except Exception:
            entry_calculator.config(state=tk.NORMAL)
            entry_calculator.delete(0, tk.END)
            entry_calculator.insert(tk.END, "Error")
            entry_calculator.config(fg='red')  # Set text color to red on error
            entry_calculator.config(state=tk.DISABLED)

    def button_click(value):
        if entry_calculator.get() == "Error":
            entry_calculator.config(state=tk.NORMAL)
            entry_calculator.delete(0, tk.END)
            entry_calculator.config(fg='black')  # Reset color for new input
            entry_calculator.config(state=tk.DISABLED)
        
        entry_calculator.config(state=tk.NORMAL)
        current_text = entry_calculator.get()
        entry_calculator.delete(0, tk.END)
        entry_calculator.insert(tk.END, current_text + value)
        entry_calculator.config(fg='black')  # Set color to black for normal input
        entry_calculator.config(state=tk.DISABLED)

    def clear_entry():
        entry_calculator.config(state=tk.NORMAL)
        entry_calculator.delete(0, tk.END)
        entry_calculator.config(fg='black')  # Reset color
        entry_calculator.config(state=tk.DISABLED)

    def backspace():
        entry_calculator.config(state=tk.NORMAL)
        current_text = entry_calculator.get()
        entry_calculator.delete(0, tk.END)
        entry_calculator.insert(tk.END, current_text[:-1])
        entry_calculator.config(fg='black')  # Reset color
        entry_calculator.config(state=tk.DISABLED)

    def key_press(event):
        if entry_calculator.focus_get() == entry_calculator:
            key = event.char
            if key in '0123456789+-*/.':
                button_click(key)
            elif event.keysym == 'Return':  # Enter key
                evaluate_expression()
            elif event.keysym == 'BackSpace':  # Backspace key
                backspace()
            elif event.keysym == 'Escape':  # Escape key
                clear_entry()

    calc_window = tk.Toplevel(window)
    calc_window.title("Calculator")

    # Load and set the icon
    app_icon = load_image("appicon1.png")
    if app_icon:
        calc_window.iconphoto(False, app_icon)
    
    calc_window.resizable(False, False)

    button_font = font.Font(size=16)
    entry_font = font.Font(size=18)
    
    entry_calculator = tk.Entry(calc_window, width=20, borderwidth=2, font=entry_font, fg='black', bg='#f0f0f0', relief='flat', state=tk.DISABLED)
    entry_calculator.grid(row=0, column=0, columnspan=4, sticky='nsew')
    entry_calculator.bind("<Button-1>", lambda e: "break")  # Disable mouse clicks
    entry_calculator.bind("<FocusIn>", lambda e: entry_calculator.focus_set())  # Ensure focus is set correctly

    buttons = [
        ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
        ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
        ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
        ('0', 4, 0), ('.', 4, 1), ('+', 4, 2), ('=', 4, 3),
        ('C', 5, 0), ('⌫', 5, 1)  
    ]

    for (text, row, column) in buttons:
        if text == '=':
            button = tk.Button(calc_window, text=text, command=evaluate_expression, font=button_font, bg='#4CAF50', fg='white', relief='flat', bd=1)
        elif text == 'C':
            button = tk.Button(calc_window, text=text, command=clear_entry, font=button_font, bg='#f44336', fg='white', relief='flat', bd=1)
        elif text == '⌫':
            button = tk.Button(calc_window, text=text, command=backspace, font=button_font, bg='#FFC107', fg='black', relief='flat', bd=1)
        else:
            button = tk.Button(calc_window, text=text, command=lambda t=text: button_click(t), font=button_font, bg='#2196F3', fg='white', relief='flat', bd=1)
        button.grid(row=row, column=column, sticky='nsew')

    # Make backspace button span the width of '.' to '='
    calc_window.grid_columnconfigure(0, weight=1)
    calc_window.grid_columnconfigure(1, weight=1)
    calc_window.grid_columnconfigure(2, weight=1)
    calc_window.grid_columnconfigure(3, weight=1)
    calc_window.grid_rowconfigure(5, weight=1)  
    
    backspace_button = tk.Button(calc_window, text='⌫', command=backspace, font=button_font, bg='#FFC107', fg='black', relief='flat', bd=1)
    backspace_button.grid(row=5, column=1, columnspan=3, sticky='nsew')

    clear_button = tk.Button(calc_window, text='C', command=clear_entry, font=button_font, bg='#f44336', fg='white', relief='flat', bd=1)
    clear_button.grid(row=5, column=0, sticky='nsew')

    calc_window.bind('<KeyPress>', key_press)
    
    entry_calculator.focus_set()

#-----------------------------------------------------------------------------------------------------------------------------------------------------------
def show_formatted_report(report):
    def search_text():
        # Clear previous highlights
        text_widget.tag_remove("highlight", "1.0", tk.END)
        search_term = search_entry.get()
        
        if search_term:
            start_idx = "1.0"
            while True:
                start_idx = text_widget.search(search_term, start_idx, nocase=tk.TRUE, stopindex=tk.END)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(search_term)}c"
                text_widget.tag_add("highlight", start_idx, end_idx)
                start_idx = end_idx
            # Highlight all matched text
            text_widget.tag_configure("highlight", background="yellow")

    # Create a new Tkinter window
    report_window = tk.Toplevel(window)
    report_window.title("Total Requirements Report")
    report_window.resizable(False, False)
    app_icon = load_image("appicon1.png")
    if app_icon:
        report_window.iconphoto(False, app_icon)



    # Create a frame for better layout management
    frame = tk.Frame(report_window)
    frame.pack(padx=10, pady=10)

    # Create a ScrolledText widget
    text_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=20, font=("Helvetica", 12))
    text_widget.pack()

    # Define bold tag
    text_widget.tag_configure("bold", font=("Helvetica", 12, "bold"))

    # Insert the report text into the text widget
    text_widget.insert(tk.END, report)


    # Detect item names and apply bold formatting
    item_names = [
        "Stardust Mining", "Water Pump", "Requirements:", "Osmosis Water Purifier",
        "Super Refinery", "Rainwater", "Small Water Pump", "Brewing Barrel",
        "Water Tank", "Securement", "Normal Refinery", "Furnace", "Blue Light",
        "Radio", "ADVHydraulic", "ADVBiomass", "Deviation", "Overall Total", "Watt"
    ]

    start_idx = '1.0'
    while True:
        start_idx = text_widget.search('Watt', start_idx, nocase=True, stopindex=tk.END)
        if not start_idx:
            break
        end_idx = f"{start_idx}+4c"  # Length of 'Watt' is 4 characters
        text_widget.tag_add('red', start_idx, end_idx)
        start_idx = end_idx

    # Define the red color tag
    text_widget.tag_config('red', foreground='red')

    for item in item_names:
        start_idx = "1.0"
        while True:
            start_idx = text_widget.search(item, start_idx, nocase=tk.TRUE, stopindex=tk.END)
            if not start_idx:
                break
            end_idx = f"{start_idx}+{len(item)}c"
            text_widget.tag_add("bold", start_idx, end_idx)
            start_idx = end_idx

    # Make the text widget read-only
    text_widget.config(state=tk.DISABLED)

    # Create a search bar and button
    search_frame = tk.Frame(frame)
    search_frame.pack(pady=5, fill=tk.X)

    
    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side=tk.LEFT, padx=5)
    
    search_button = tk.Button(search_frame, text="Search", command=search_text)
    search_button.pack(side=tk.LEFT)

    # Add an OK button to close the window
    def close_window():
        report_window.destroy()

    ok_button = tk.Button(frame, text="OK", command=close_window)
    ok_button.pack(pady=5)

    # Start the Tkinter event loop
    
    report_window.mainloop()

# objects
#----------------------------------------------------------------------------------------------------------------------------------------------------------- 

class WaterPump:
    STEEL_INGOT = 25
    CARBON_FIBER_FABRIC = 20
    REFINED_PART = 20
    STANDARD_PART = 20
    ELECTRONIC_PART = 20
    WATT = 10

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Steel Ingot': self.STEEL_INGOT * self.quantity,
            'Carbon Fiber Fabric': self.CARBON_FIBER_FABRIC * self.quantity,
            'Refined Part': self.REFINED_PART * self.quantity,
            'Standard Part': self.STANDARD_PART * self.quantity,
            'Electronic Part': self.ELECTRONIC_PART * self.quantity,
            'Watt': self.WATT * self.quantity
            
        }



class SuperRefinery:
    BRONZE_INGOT = 25
    COPPER_INGOT = 10
    ELECTRONIC_PART = 5
    STANDARD_PART = 10
    WATT = 15

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Bronze Ingot': self.BRONZE_INGOT * self.quantity,
            'Copper Ingot': self.COPPER_INGOT * self.quantity,
            'Electronic Part': self.ELECTRONIC_PART * self.quantity,
            'Standard Part': self.STANDARD_PART * self.quantity,
            'Watt': self.WATT * self.quantity
            
        }

class OsmosisWaterPurifier:
    AUTOMATIC_PART = 20
    ADHESIVE = 20
    ELECTRONIC_PART = 15
    METAL_SCRAPS = 15
    RUBBERS = 10
    TUNGSTEN_INGOT = 10
    WATT = 10

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Automatic Part': self.AUTOMATIC_PART * self.quantity,
            'Adhesive': self.ADHESIVE * self.quantity,
            'Electronic Part': self.ELECTRONIC_PART * self.quantity,
            'Metal Scraps': self.METAL_SCRAPS * self.quantity,
            'Rubbers': self.RUBBERS * self.quantity,
            'Tungsten Ingot': self.TUNGSTEN_INGOT * self.quantity,
            'Watt': self.WATT * self.quantity
            
        }

class Rainwater:
    LOG = 30
    SHABBY_FABRIC = 15
    RUBBER = 5

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Log': self.LOG * self.quantity,
            'Shabby Fabric': self.SHABBY_FABRIC * self.quantity,
            'Rubber': self.RUBBER * self.quantity
        }

class SmallWaterPump:
    REFINED_PART = 10
    STEEL_INGOT = 30
    ELECTRONIC_PART = 2
    WATT = 1

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Refined Part': self.REFINED_PART * self.quantity,
            'Steel Ingot': self.STEEL_INGOT * self.quantity,
            'Electronic Part': self.ELECTRONIC_PART * self.quantity,
            'Watt': self.WATT * self.quantity
            
        }

class BrewingBarrel:
    LOG = 50
    ADHESIVE = 20
    ALUMINUM_INGOT = 20
    RUBBERS = 20
    ACID = 15
    WATT = 10

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Log': self.LOG * self.quantity,
            'Adhesive': self.ADHESIVE * self.quantity,
            'Aluminum Ingot': self.ALUMINUM_INGOT * self.quantity,
            'Rubbers': self.RUBBERS * self.quantity,
            'Acid': self.ACID * self.quantity,
            'Watt': self.WATT * self.quantity
        }

class WaterTank:
    METAL_SCRAPS = 15
    LOG = 50
    ADHESIVE = 5

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Metal Scraps': self.METAL_SCRAPS * self.quantity,
            'Log': self.LOG * self.quantity,
            'Adhesive': self.ADHESIVE * self.quantity
            
            
        }

class Securement:
    METAL_SCRAPS = 20
    COPPER_INGOT = 15
    GLASS = 10

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Metal Scraps': self.METAL_SCRAPS * self.quantity,
            'Copper Ingot': self.COPPER_INGOT * self.quantity,
            'Glass': self.GLASS * self.quantity
        }

class NormalRefinery:
    BRONZE_INGOT = 25
    COPPER_INGOT = 10
    ELECTRONIC_PART = 5
    STANDARD_PART = 10
    WATT = 10

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Bronze Ingot': self.BRONZE_INGOT * self.quantity,
            'Copper Ingot': self.COPPER_INGOT * self.quantity,
            'Electronic Part': self.ELECTRONIC_PART * self.quantity,
            'Standard Part': self.STANDARD_PART * self.quantity,
            'Watt': self.WATT * self.quantity
            
        }

class StardustMining:
    TUNGSTEN_INGOT = 25
    ADHESIVE = 15
    STARDUST_SOURCE = 50
    RUBBERS = 20
    METAL_SCRAPS = 15
    ELECTRONIC_PART = 30
    BATTERY = 4
    WATT = 15

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Tungsten Ingot': self.TUNGSTEN_INGOT * self.quantity,
            'Adhesive': self.ADHESIVE * self.quantity,
            'Stardust Source': self.STARDUST_SOURCE * self.quantity,
            'Rubbers': self.RUBBERS * self.quantity,
            'Metal Scraps': self.METAL_SCRAPS * self.quantity,
            'Electronic Part': self.ELECTRONIC_PART * self.quantity,
            'Battery': self.BATTERY * self.quantity,
            'Watt': self.WATT * self.quantity,
            
        }

class Furnace:
    COPPER_ORE = 20
    GRAVEL = 30

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Copper Ore': self.COPPER_ORE * self.quantity,
            'Gravel': self.GRAVEL * self.quantity
        }

class BlueLight:
    LOG = 15
    ADHESIVE = 5
    ELECTRONIC_PART = 1
    RUBBERS = 10

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Log': self.LOG * self.quantity,
            'Adhesive': self.ADHESIVE * self.quantity,
            'Electronic Part': self.ELECTRONIC_PART * self.quantity,
            'Rubbers': self.RUBBERS * self.quantity
        }

class Radio:
    LOG = 10
    RUSTED_PART = 4
    ELECTRONIC_PART = 1
    WASTED_PLASTIC = 3
    COPPER_INGOT = 2

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Log': self.LOG * self.quantity,
            'Rusted Part': self.RUSTED_PART * self.quantity,
            'Electronic Part': self.ELECTRONIC_PART * self.quantity,
            'Wasted Plastic': self.WASTED_PLASTIC * self.quantity,
            'Copper Ingot': self.COPPER_INGOT * self.quantity
        }

class ADVHydraulic:
    TUNGSTEN_INGOT = 40
    AUTOMATIC_PART = 30
    ELECTRONIC_PART = 30
    SPECIAL_PLASTIC = 30
    LOG = 75
    FUSE = 8

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Tungsten Ingot': self.TUNGSTEN_INGOT * self.quantity,
            'Automatic Part': self.AUTOMATIC_PART * self.quantity,
            'Electronic Part': self.ELECTRONIC_PART * self.quantity,
            'Special Plastic': self.SPECIAL_PLASTIC * self.quantity,
            'Log': self.LOG * self.quantity,
            'Fuse': self.FUSE * self.quantity
        }

class ADVBiomass:
    TUNGSTEN_INGOT = 20
    AUTOMATIC_PART = 15
    ELECTRONIC_PART = 30
    SPECIAL_PLASTIC = 15
    COPPER_INGOT = 16
    FUSE = 5

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Tungsten Ingot': self.TUNGSTEN_INGOT * self.quantity,
            'Automatic Part': self.AUTOMATIC_PART * self.quantity,
            'Electronic Part': self.ELECTRONIC_PART * self.quantity,
            'Special Plastic': self.SPECIAL_PLASTIC * self.quantity,
            'Copper Ingot': self.COPPER_INGOT * self.quantity,
            'Fuse': self.FUSE * self.quantity
        }

class Deviation:
    TUNGSTEN_INGOT = 100
    AUTOMATIC_PART = 40
    ELECTRONIC_PART = 40
    SPECIAL_PLASTIC = 40
    STARDUST_SOURCE = 100
    FUSE = 8

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Tungsten Ingot': self.TUNGSTEN_INGOT * self.quantity,
            'Automatic Part': self.AUTOMATIC_PART * self.quantity,
            'Electronic Part': self.ELECTRONIC_PART * self.quantity,
            'Special Plastic': self.SPECIAL_PLASTIC * self.quantity,
            'Stardust Source': self.STARDUST_SOURCE * self.quantity,
            'Fuse': self.FUSE * self.quantity
        }


#============================================================================================
# get all values from object instance then calculate
def calculate_requirements():
    try:
        # Retrieve quantities from user input
        quantities = {
            'WaterPump': int(entry_widgets[0].get() or 0),
            'SuperRefinery': int(entry_widgets[11].get() or 0),
            'OsmosisWaterPurifier': int(entry_widgets[14].get() or 0),
            'Rainwater': int(entry_widgets[13].get() or 0),
            'SmallWaterPump': int(entry_widgets[12].get() or 0),
            'BrewingBarrel': int(entry_widgets[10].get() or 0),
            'WaterTank': int(entry_widgets[9].get() or 0),
            'Securement': int(entry_widgets[8].get() or 0),
            'NormalRefinery': int(entry_widgets[15].get() or 0),
            'StardustMining': int(entry_widgets[4].get() or 0),
            'Furnace': int(entry_widgets[5].get() or 0),
            'BlueLight': int(entry_widgets[6].get() or 0),
            'Radio': int(entry_widgets[7].get() or 0),
            'ADVHydraulic': int(entry_widgets[3].get() or 0),
            'ADVBiomass': int(entry_widgets[1].get() or 0),
            'Deviation': int(entry_widgets[2].get() or 0)
        }

        # Create instances and compute totals
        instances = {
            'Water Pump': WaterPump(quantities['WaterPump']),
            'Super Refinery': SuperRefinery(quantities['SuperRefinery']),
            'Osmosis Water Purifier': OsmosisWaterPurifier(quantities['OsmosisWaterPurifier']),
            'Rainwater': Rainwater(quantities['Rainwater']),
            'Small Water Pump': SmallWaterPump(quantities['SmallWaterPump']),
            'Brewing Barrel': BrewingBarrel(quantities['BrewingBarrel']),
            'Water Tank': WaterTank(quantities['WaterTank']),
            'Securement': Securement(quantities['Securement']),
            'Normal Refinery': NormalRefinery(quantities['NormalRefinery']),
            'Stardust Mining': StardustMining(quantities['StardustMining']),
            'Furnace': Furnace(quantities['Furnace']),
            'Blue Light': BlueLight(quantities['BlueLight']),
            'Radio': Radio(quantities['Radio']),
            'ADVHydraulic': ADVHydraulic(quantities['ADVHydraulic']),
            'ADVBiomass': ADVBiomass(quantities['ADVBiomass']),
            'Deviation': Deviation(quantities['Deviation'])
        }

        combined_totals = {}
        detailed_report = ""

        for name, obj in instances.items():
            requirements = obj.total_requirements()
            if any(amount > 0 for amount in requirements.values()):  
                detailed_report += f"{name} Requirements:\n"
                # Ensure "Watt" is listed at the end
                items = [item for item in requirements.items() if item[0] != 'Watt']
                watt = requirements.get('Watt', 0)
                
                for material, amount in items:
                    if amount > 0:
                        if material in combined_totals:
                            combined_totals[material] += amount
                        else:
                            combined_totals[material] = amount
                        detailed_report += f"{material}: {amount}\n"
                
                if watt > 0:
                    if 'Watt' in combined_totals:
                        combined_totals['Watt'] += watt
                    else:
                        combined_totals['Watt'] = watt
                    detailed_report += f"Watt: {watt}\n"

                detailed_report += "\n"

        filtered_totals = {k: v for k, v in combined_totals.items() if v > 0}

        detailed_report += "\nOverall Total Requirements:\n"
        total_watt = filtered_totals.pop('Watt', 0)  # Extract 'Watt' if present

        for material, amount in filtered_totals.items():
            detailed_report += f"{material}: {amount}\n"

        # Add Watt last, formatted in red
        if total_watt > 0:
            detailed_report += f"Watt: {total_watt}\n"

        if detailed_report:
            show_formatted_report(detailed_report)
        else:
            tk.messagebox.showinfo("Total Requirements", "No requirements to show.")

    except ValueError:
        tk.messagebox.showerror("Invalid Input", "Please enter valid numbers for all quantities.")

# main menu gui
#=====================================================================================
# Helper functions
def relative_to_assets(path):
    """Return the path to the asset, relative to the current script's location."""
    if getattr(sys, 'frozen', False):
        # If the application is frozen (i.e., running from a bundled executable)
        base_path = getattr(sys, '_MEIPASS', Path(__file__).parent)
    else:
        # If running in a normal Python environment
        base_path = Path(__file__).parent
    return str(Path(base_path) / path)

def load_image(image_path):
    """Load an image from a path."""
    try:
        image = PhotoImage(file=relative_to_assets(image_path))
        return image
    except Exception as e:
        tk.messagebox.showerror(f"Error loading image {image_path}: {e}")
        print(f"Exception: {e}")  # Debugging statement
        return None

window = tk.Tk()
window.geometry("1348x785")
window.configure(bg="#FFFFFF")
bold_font = font.Font(weight="bold")
window.title("Once Human Tool Helper By Avery")

# Load images after creating the root window
app_icon = load_image("appicon1.png")
main_images = [load_image(f"image_{i}.png") for i in range(1, 18)]
entry_images = [load_image(f"entry_{i}.png") for i in range(1, 17)]
button_image = load_image("button_1.png")


# Set up icon if possible
if app_icon:
    window.iconphoto(False, app_icon)

canvas = Canvas(
    window, bg="#FFFFFF", height=785, width=1348, bd=0,
    highlightthickness=0, relief="ridge"
)
canvas.place(x=0, y=0)

# Set up images on the canvas
image_positions = [
    (141.0, 223.0, main_images[0]),
    (291.0, 223.0, main_images[1]),
    (674.0, 65.0, main_images[2]),
    (441.0, 222.0, main_images[3]),
    (593.0, 222.0, main_images[4]),
    (736.0, 222.0, main_images[5]),
    (889.0, 223.0, main_images[6]),
    (1042.0, 222.0, main_images[7]),
    (1189.0, 223.0, main_images[8]),
    (1045.0, 447.0, main_images[9]),
    (139.0, 445.0, main_images[10]),
    (295.0, 445.0, main_images[11]),
    (436.0, 445.0, main_images[12]),
    (593.0, 445.0, main_images[13]),
    (738.0, 447.0, main_images[14]),
    (892.0, 447.0, main_images[15]),
    (1194.0, 448.0, main_images[16])
]
for x, y, img in image_positions:
    if img:
        canvas.create_image(x, y, image=img)

# Set up entry widgets on the canvas
entry_positions = [
    (141.0, 332.0, entry_images[0]),
    (1045.0, 555.0, entry_images[1]),
    (1192.0, 558.0, entry_images[2]),
    (891.0, 557.0, entry_images[3]),
    (295.0, 554.0, entry_images[4]),
    (434.0, 554.0, entry_images[5]),
    (593.0, 554.0, entry_images[6]),
    (736.0, 555.0, entry_images[7]),
    (1192.0, 332.0, entry_images[8]),
    (1042.0, 332.0, entry_images[9]),
    (888.0, 332.0, entry_images[10]),
    (737.0, 332.0, entry_images[11]),
    (593.0, 331.0, entry_images[12]),
    (440.0, 332.0, entry_images[13]),
    (292.0, 331.0, entry_images[14]),
    (140.0, 555.0, entry_images[15])
]

entry_widgets = []  # List to keep references to entry widgets

for x, y, img in entry_positions:
    if img:
        canvas.create_image(x, y, image=img)
        entry = Entry(
            bd=0, bg="#535353", fg="#FFFFFF",
            highlightthickness=0, font=bold_font, justify='center'
        )
        entry.place(x=x - 31, y=y - 23, width=62.0, height=40.0)
        entry_widgets.append(entry)

# Set up text labels on the canvas
text_labels = [
    (112.0, 285.0, "Quantity"),
    (1017.0, 508.0, "Quantity"),
    (1164.0, 511.0, "Quantity"),
    (862.0, 510.0, "Quantity"),
    (265.0, 508.0, "Quantity"),
    (112.0, 508.0, "Quantity"),
    (406.0, 508.0, "Quantity"),
    (566.0, 508.0, "Quantity"),
    (708.0, 509.0, "Quantity"),
    (1165.0, 285.0, "Quantity"),
    (1014.0, 285.0, "Quantity"),
    (859.0, 285.0, "Quantity"),
    (710.0, 285.0, "Quantity"),
    (562.0, 285.0, "Quantity"),
    (412.0, 285.0, "Quantity"),
    (263.0, 285.0, "Quantity")
]
for x, y, text in text_labels:
    canvas.create_text(x, y, anchor="nw", text=text, fill="#4069D5", font=("Inter Bold", 13))

canvas.create_text(395.0, 43.0, anchor="nw", text="Alt Base Materials Calculator ", fill="#FFFFFF", font=("Inter Bold", 40 * -1))

# Set up buttons on the window
if button_image:
    Button(
        window, image=button_image, borderwidth=0,
        highlightthickness=0, command=calculate_requirements,
        relief="flat"
    ).place(x=375.0, y=634.0, width=588.0, height=85.0)

calc_button = tk.Button(window, text="Open Calculator", command=open_calculator)
calc_button.place(x=1230, y=50)

additional_images = [
    (1045.0, 447.0, "image_10.png"),
    (139.0, 445.0, "image_11.png"),
    (295.0, 445.0, "image_12.png"),
    (436.0, 445.0, "image_13.png"),
    (593.0, 445.0, "image_14.png"),
    (738.0, 447.0, "image_15.png"),
    (892.0, 447.0, "image_16.png"),
    (1194.0, 448.0, "image_17.png")
]



for x, y, img_file in additional_images:
    img = load_image(img_file)
    if img:
        canvas.create_image(x, y, image=img)

window.resizable(False, False)
window.mainloop()
