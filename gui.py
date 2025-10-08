from pathlib import Path
from tkinter import Canvas, Entry, Button, PhotoImage, font,scrolledtext , messagebox
from tkinter import ttk
import tkinter as tk
import os
import sys
import re
from PIL import Image, ImageTk

MATERIAL_COSTS = {
    'Steel Ingot': 50,
    'Carbon Fiber Fabric': 5,
    'Refined Part': 5,
    'Standard Part': 5,
    'Electronic Part': 5,
    'Watt': 0,
    'Bronze Ingot': 40,
    'Copper Ingot': 20,
    'Automatic Part': 15,
    'Adhesive': 5,
    'Metal Scraps': 5,
    'Rubber': 5,
    'Tungsten Ingot': 80,
    'Log': 1,
    'Shabby Fabric': 5,
    'Aluminum Ingot': 60,
    'Acid': 8,
    'Glass': 10,
    'Battery': 500,
    'Rusted Part': 5,
    'Special Plastic': 10,
    'Wasted Plastic': 5,
    'Stardust Source': 3,
    'Fuse': 20,
    'Copper Ore': 3,
    'Gravel': 1
}

# Track which materials should show transfer costs (enabled by default for materials with cost > 0)
SHOW_TRANSFER_FOR = {material: (cost > 0) for material, cost in MATERIAL_COSTS.items()}

#-----------------------------------------------------------------------------------------------------------------------------------------------------------
def show_formatted_report(report, show_transfer_button=False, raw_data=None):
    """Enhanced report window with live updates"""
    
    def regenerate_report():
        """Regenerate the report with current SHOW_TRANSFER_FOR settings"""
        if not raw_data:
            return report
        
        # Start with item details if available
        detailed_report = raw_data.get('item_details', '')
        
        detailed_report += "\nOverall Total Requirements:\n"
        filtered_totals = raw_data['filtered_totals'].copy()
        total_watt = filtered_totals.pop('Watt', 0)
        show_costs = raw_data['show_costs']
        
        # Separate materials based on current SHOW_TRANSFER_FOR settings
        materials_with_transfer = {}
        materials_without_transfer = {}
        
        for material, amount in filtered_totals.items():
            if SHOW_TRANSFER_FOR.get(material, False) and MATERIAL_COSTS.get(material, 0) > 0:
                materials_with_transfer[material] = amount
            else:
                materials_without_transfer[material] = amount
        
        # Calculate total cost
        total_cost = 0
        if show_costs:
            for material, amount in materials_with_transfer.items():
                cost = MATERIAL_COSTS.get(material, 0)
                total_cost += amount * cost
        
        # Show materials with transfer cost
        for material, amount in materials_with_transfer.items():
            if show_costs:
                cost = MATERIAL_COSTS.get(material, 0)
                total = amount * cost
                detailed_report += f"{material}: {amount} → [COST]{total}[/COST]\n"
            else:
                detailed_report += f"{material}: {amount}\n"
        
        # Show materials without transfer cost
        for material, amount in materials_without_transfer.items():
            detailed_report += f"{material}: {amount}\n"
        
        # Add Watt
        if total_watt > 0:
            detailed_report += f"Watt: {total_watt}\n"
        
        # Add total cost with smart character splitting
        if show_costs and total_cost > 0:
            if total_cost > 20000:
                import math
                
                detailed_report += f"\n{'='*50}\n"
                detailed_report += f"[WARNING]⚠ Total Transfer Cost: {total_cost:,} (exceeds 20,000 limit)[/WARNING]\n"
                detailed_report += f"{'='*50}\n\n"
                
                # Create list of (material, amount, unit_cost, total_cost) tuples
                material_list = []
                for material, amount in materials_with_transfer.items():
                    unit_cost = MATERIAL_COSTS.get(material, 0)
                    mat_total = amount * unit_cost
                    material_list.append({
                        'name': material,
                        'amount': amount,
                        'unit_cost': unit_cost,
                        'total_cost': mat_total
                    })
                
                # Sort by total cost (descending) for better filling
                material_list.sort(key=lambda x: x['total_cost'], reverse=True)
                
                # Split into characters
                characters = []
                current_char = {'materials': [], 'total_cost': 0}
                
                for mat in material_list:
                    remaining_amount = mat['amount']
                    
                    while remaining_amount > 0:
                        # Calculate how much we can fit in current character
                        space_left = 20000 - current_char['total_cost']
                        
                        # Calculate max quantity that fits in remaining space
                        max_qty = space_left // mat['unit_cost'] if mat['unit_cost'] > 0 else remaining_amount
                        
                        # Take the minimum of what's needed and what fits
                        qty_to_add = min(remaining_amount, max_qty)
                        
                        if qty_to_add > 0:
                            cost_to_add = qty_to_add * mat['unit_cost']
                            current_char['materials'].append({
                                'name': mat['name'],
                                'amount': qty_to_add,
                                'cost': cost_to_add
                            })
                            current_char['total_cost'] += cost_to_add
                            remaining_amount -= qty_to_add
                        
                        # If character is full or no more room, start new character
                        if remaining_amount > 0 or current_char['total_cost'] >= 19900:  # Leave small buffer
                            if current_char['materials']:  # Only save if has materials
                                characters.append(current_char)
                            current_char = {'materials': [], 'total_cost': 0}
                
                # Add last character if has materials
                if current_char['materials']:
                    characters.append(current_char)
                
                # Display character assignments
                detailed_report += f"[TOTAL]📦 Split across {len(characters)} character(s):[/TOTAL]\n\n"
                
                for idx, char in enumerate(characters, 1):
                    detailed_report += f"[SECTION]Character {idx} (Total: {char['total_cost']:,}):[/SECTION]\n"
                    for mat in char['materials']:
                        detailed_report += f"  {mat['name']}: {mat['amount']} → [COST]{mat['cost']:,}[/COST]\n"
                    detailed_report += "\n"
                
            else:
                detailed_report += f"[TOTAL]Total Transfer Cost: {total_cost:,}[/TOTAL]\n"
        
        return detailed_report
    
    def refresh_display():
        """Refresh the text display with updated report"""
        new_report = regenerate_report()
        text_widget.config(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, new_report)
        
        # Reapply all formatting
        apply_formatting()
        
        text_widget.config(state=tk.DISABLED)
        
        # Scroll to Overall Total Requirements section
        overall_pos = text_widget.search('Overall Total Requirements', '1.0', stopindex=tk.END)
        
        if overall_pos:
            # Scroll to show the overall section
            text_widget.see(overall_pos)
            # Move up a bit to show some context
            line_num = int(overall_pos.split('.')[0])
            if line_num > 3:
                text_widget.see(f"{line_num - 3}.0")
        else:
            # If not found, scroll to the bottom
            text_widget.see(tk.END)
    
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

    # Create a new Tkinter window with modern gray styling
    report_window = tk.Toplevel(window)
    report_window.title("Total Requirements Report")
    report_window.geometry("750x700")
    report_window.resizable(False, False)
    report_window.configure(bg="#F3F4F6")
    
    # Set initial state for always on top
    report_window.attributes('-topmost', False)
    # Set initial window opacity to 100% (fully opaque)
    report_window.attributes('-alpha', 1.0)
    
    app_icon = load_image("appicon1.png")
    if app_icon:
        report_window.iconphoto(False, app_icon)

    # Create header frame with gray theme
    header_frame = tk.Frame(report_window, bg="#374151", height=70)
    header_frame.pack(fill=tk.X)
    header_frame.pack_propagate(False)
    
    # Header title (left side)
    header_label = tk.Label(
        header_frame, 
        text="📊 Total Requirements Report",
        bg="#374151",
        fg="#F9FAFB",
        font=("Segoe UI", 20, "bold")
    )
    header_label.pack(side=tk.LEFT, padx=20, pady=20)
    
    # Controls container (right side initially, will be centered when title is hidden)
    controls_frame = tk.Frame(header_frame, bg="#374151")
    controls_frame.pack(side=tk.RIGHT, padx=20, pady=20)
    
    # Always on top toggle
    always_on_top_var = tk.BooleanVar(value=False)
    
    # Store references to elements that need to be hidden/shown
    elements_to_hide = []
    
    def toggle_always_on_top():
        is_on_top = always_on_top_var.get()
        report_window.attributes('-topmost', is_on_top)
        # Hide/show title bar based on always on top state
        if is_on_top:
            report_window.overrideredirect(True)  # Hide title bar
            topmost_btn.config(bg="#059669")  # Green when on top
            # Enable opacity controls
            opacity_active[0] = True
            # Show transparency controls
            transparency_frame.pack(side=tk.LEFT)
            # Hide header title text
            header_label.pack_forget()
            # Recenter controls now that title is hidden
            controls_frame.pack_forget()
            controls_frame.pack(expand=True, pady=20)
            # Hide search frame, separator, and buttons frame
            for element in elements_to_hide:
                element.pack_forget()
            # Resize window to be smaller (remove ~150px for hidden elements and title bar)
            report_window.geometry("420x520")
        else:
            report_window.overrideredirect(False)  # Show title bar
            topmost_btn.config(bg="#6B7280")  # Gray when normal
            # Disable opacity controls and reset to 100%
            opacity_active[0] = False
            current_opacity[0] = 1.0
            report_window.attributes('-alpha', 1.0)
            update_transparency_label()
            # Hide transparency controls
            transparency_frame.pack_forget()
            # Show header title text
            header_label.pack(side=tk.LEFT, padx=20, pady=20)
            # Move controls back to the right
            controls_frame.pack_forget()
            controls_frame.pack(side=tk.RIGHT, padx=20, pady=20)
            # Show search frame, separator, and buttons frame
            if len(elements_to_hide) >= 3:
                elements_to_hide[0].pack(pady=(0, 10), fill=tk.X)  # search_frame
                elements_to_hide[1].pack(fill=tk.X, pady=(0, 15))  # separator
                elements_to_hide[2].pack(pady=0)  # buttons_frame
            # Resize window back to normal size
            report_window.geometry("750x700")
    
    topmost_btn = tk.Button(
        controls_frame,
        text="📌",
        command=toggle_always_on_top,
        bg="#6B7280",
        fg="#F9FAFB",
        font=("Segoe UI", 12, "bold"),
        relief="flat",
        cursor="hand2",
        width=2,
        height=1
    )
    topmost_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    # Update the button state
    def update_topmost_button():
        always_on_top_var.set(not always_on_top_var.get())
        toggle_always_on_top()
    
    topmost_btn.config(command=update_topmost_button)
    
    # Add hover effect for topmost button
    def on_enter_topmost(e):
        current_bg = topmost_btn.cget("bg")
        if current_bg == "#059669":  # Green (On Top)
            topmost_btn.config(bg="#047857")
        else:  # Gray (Normal)
            topmost_btn.config(bg="#4B5563")
    
    def on_leave_topmost(e):
        if always_on_top_var.get():
            topmost_btn.config(bg="#059669")
        else:
            topmost_btn.config(bg="#6B7280")
    
    topmost_btn.bind("<Enter>", on_enter_topmost)
    topmost_btn.bind("<Leave>", on_leave_topmost)
    
    # Transparency controls (widgets only, functions defined later)
    transparency_frame = tk.Frame(controls_frame, bg="#374151")
    # Don't pack initially - will be shown when "Always on Top" is enabled
    
    transparency_label = tk.Label(
        transparency_frame,
        text="Opacity:",
        bg="#374151",
        fg="#F9FAFB",
        font=("Segoe UI", 10)
    )
    transparency_label.pack(side=tk.LEFT, padx=(0, 5))
    
    # Store current window opacity (0.0 to 1.0)
    current_opacity = [1.0]  # Using list to allow modification in nested functions
    # Store whether opacity controls are active
    opacity_active = [False]

    # Create main content frame with gray theme
    frame = tk.Frame(report_window, bg="#F3F4F6")
    frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    # Create a card-like container for the text widget (don't expand to leave room for buttons)
    text_container = tk.Frame(frame, bg="#FFFFFF", relief="flat", borderwidth=0)
    text_container.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
    
    # Add subtle shadow effect with multiple frames
    shadow_frame = tk.Frame(frame, bg="#D1D5DB", relief="flat")
    shadow_frame.place(in_=text_container, relx=0.005, rely=0.005, relwidth=1, relheight=1)
    text_container.lift()
    
    # Create a ScrolledText widget with enhanced styling (fixed height)
    text_widget = scrolledtext.ScrolledText(
        text_container, 
        wrap=tk.WORD, 
        width=80, 
        height=20, 
        font=("Segoe UI", 12), 
        bg="#FFFFFF",
        fg="#1F2937",
        relief="flat",
        borderwidth=0,
        padx=15,
        pady=15,
        insertbackground="#3B82F6",
        selectbackground="#DBEAFE",
        selectforeground="#1E40AF"
    )
    text_widget.pack(fill=tk.BOTH, expand=False, padx=2, pady=2)

    # Now define transparency functions after text_widget is created
    def update_window_opacity():
        """Update the entire window opacity (only when always on top is active)"""
        if opacity_active[0]:
            report_window.attributes('-alpha', current_opacity[0])
    
    def decrease_transparency():
        if opacity_active[0]:
            current_opacity[0] = max(0.2, current_opacity[0] - 0.05)  # Minimum 20% opacity
            update_window_opacity()
            update_transparency_label()
    
    def increase_transparency():
        if opacity_active[0]:
            current_opacity[0] = min(1.0, current_opacity[0] + 0.05)  # Maximum 100% opacity
            update_window_opacity()
            update_transparency_label()
    
    def update_transparency_label():
        percentage = int(current_opacity[0] * 100)
        transparency_value_label.config(text=f"{percentage}%")
    
    # Create transparency control buttons
    # Decrease opacity button (more transparent)
    decrease_btn = tk.Button(
        transparency_frame,
        text="−",
        command=decrease_transparency,
        bg="#4B5563",
        fg="#F9FAFB",
        font=("Segoe UI", 14, "bold"),
        relief="flat",
        cursor="hand2",
        width=2,
        height=1
    )
    decrease_btn.pack(side=tk.LEFT, padx=2)
    
    # Opacity percentage display
    transparency_value_label = tk.Label(
        transparency_frame,
        text="100%",
        bg="#374151",
        fg="#F9FAFB",
        font=("Segoe UI", 11, "bold"),
        width=5
    )
    transparency_value_label.pack(side=tk.LEFT, padx=5)
    
    # Increase opacity button (less transparent)
    increase_btn = tk.Button(
        transparency_frame,
        text="+",
        command=increase_transparency,
        bg="#4B5563",
        fg="#F9FAFB",
        font=("Segoe UI", 14, "bold"),
        relief="flat",
        cursor="hand2",
        width=2,
        height=1
    )
    increase_btn.pack(side=tk.LEFT, padx=2)
    
    # Add hover effects for transparency buttons
    def on_enter_decrease(e):
        decrease_btn.config(bg="#6B7280")
    
    def on_leave_decrease(e):
        decrease_btn.config(bg="#4B5563")
    
    def on_enter_increase(e):
        increase_btn.config(bg="#6B7280")
    
    def on_leave_increase(e):
        increase_btn.config(bg="#4B5563")
    
    decrease_btn.bind("<Enter>", on_enter_decrease)
    decrease_btn.bind("<Leave>", on_leave_decrease)
    increase_btn.bind("<Enter>", on_enter_increase)
    increase_btn.bind("<Leave>", on_leave_increase)

    # Define tags with larger, more readable fonts
    text_widget.tag_configure("bold", font=("Segoe UI", 13, "bold"))
    text_widget.tag_configure("item_header", font=("Segoe UI", 14, "bold"), foreground="#1976D2")
    text_widget.tag_configure("section_header", font=("Segoe UI", 16, "bold"), foreground="#0D47A1")
    text_widget.tag_configure("cost_color", foreground="#F59E0B", font=("Segoe UI", 14, "bold"))  # Orange/amber for transfer costs
    text_widget.tag_configure("total_color", foreground="#059669", font=("Segoe UI", 17, "bold"))  # Green for total transfer cost
    text_widget.tag_configure("warning_color", foreground="#DC2626", font=("Segoe UI", 13, "bold"))
    text_widget.tag_configure("red_color", foreground="#D32F2F", font=("Segoe UI", 14, "bold"))
    text_widget.tag_configure("green_color", foreground="#388E3C", font=("Segoe UI", 14, "bold"))
    text_widget.tag_configure("highlight", background="#FFEB3B")
    text_widget.tag_configure("red", foreground="#D32F2F", font=("Segoe UI", 14, "bold"))
    text_widget.tag_configure("material_name", font=("Segoe UI", 12, "bold"), foreground="#424242")
    text_widget.tag_configure("number", font=("Segoe UI", 13, "bold"), foreground="#3B82F6")  # Blue for regular numbers

    def apply_formatting():
        """Apply all color formatting to the text"""
        # First apply generic number formatting to all numbers
        content = text_widget.get('1.0', tk.END)
        lines = content.split('\n')
        for line_num, line in enumerate(lines, start=1):
            for match in re.finditer(r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\b', line):
                col_start = match.start()
                col_end = match.end()
                start_pos = f"{line_num}.{col_start}"
                end_pos = f"{line_num}.{col_end}"
                text_widget.tag_add('number', start_pos, end_pos)
        
        # Apply cost color formatting (will override number tag)
        start_idx = '1.0'
        while True:
            start_idx = text_widget.search('[COST]', start_idx, stopindex=tk.END)
            if not start_idx:
                break
            end_tag_start = text_widget.search('[/COST]', start_idx, stopindex=tk.END)
            if not end_tag_start:
                break
            
            # Remove the tags and apply color
            text_widget.delete(start_idx, f"{start_idx}+6c")
            end_tag_start = text_widget.search('[/COST]', start_idx, stopindex=tk.END)
            text_widget.delete(end_tag_start, f"{end_tag_start}+7c")
            
            # Apply color to the cost number (higher priority than number tag)
            text_widget.tag_remove("number", start_idx, end_tag_start)
            text_widget.tag_add("cost_color", start_idx, end_tag_start)
            start_idx = end_tag_start

        # Apply total cost color formatting (will override number tag)
        start_idx = '1.0'
        while True:
            start_idx = text_widget.search('[TOTAL]', start_idx, stopindex=tk.END)
            if not start_idx:
                break
            end_tag_start = text_widget.search('[/TOTAL]', start_idx, stopindex=tk.END)
            if not end_tag_start:
                break
            
            # Remove the tags and apply color
            text_widget.delete(start_idx, f"{start_idx}+7c")
            end_tag_start = text_widget.search('[/TOTAL]', start_idx, stopindex=tk.END)
            text_widget.delete(end_tag_start, f"{end_tag_start}+8c")
            
            # Apply color to the total cost (higher priority than number tag)
            text_widget.tag_remove("number", start_idx, end_tag_start)
            text_widget.tag_add("total_color", start_idx, end_tag_start)
            start_idx = end_tag_start

        # Apply warning color formatting
        start_idx = '1.0'
        while True:
            start_idx = text_widget.search('[WARNING]', start_idx, stopindex=tk.END)
            if not start_idx:
                break
            end_tag_start = text_widget.search('[/WARNING]', start_idx, stopindex=tk.END)
            if not end_tag_start:
                break
            
            # Remove the tags and apply color
            text_widget.delete(start_idx, f"{start_idx}+9c")
            end_tag_start = text_widget.search('[/WARNING]', start_idx, stopindex=tk.END)
            text_widget.delete(end_tag_start, f"{end_tag_start}+10c")
            
            # Apply color to the warning text
            text_widget.tag_add("warning_color", start_idx, end_tag_start)
            start_idx = end_tag_start

        # Apply section formatting for character splits
        start_idx = '1.0'
        while True:
            start_idx = text_widget.search('[SECTION]', start_idx, stopindex=tk.END)
            if not start_idx:
                break
            end_tag_start = text_widget.search('[/SECTION]', start_idx, stopindex=tk.END)
            if not end_tag_start:
                break
            
            # Remove the tags and apply color
            text_widget.delete(start_idx, f"{start_idx}+9c")
            end_tag_start = text_widget.search('[/SECTION]', start_idx, stopindex=tk.END)
            text_widget.delete(end_tag_start, f"{end_tag_start}+10c")
            
            # Apply section header formatting
            text_widget.tag_add("item_header", start_idx, end_tag_start)
            start_idx = end_tag_start

        # Apply red color formatting for quantities
        start_idx = '1.0'
        while True:
            start_idx = text_widget.search('[RED]', start_idx, stopindex=tk.END)
            if not start_idx:
                break
            end_tag_start = text_widget.search('[/RED]', start_idx, stopindex=tk.END)
            if not end_tag_start:
                break
            
            # Remove the tags and apply color
            text_widget.delete(start_idx, f"{start_idx}+5c")
            end_tag_start = text_widget.search('[/RED]', start_idx, stopindex=tk.END)
            text_widget.delete(end_tag_start, f"{end_tag_start}+6c")
            
            # Apply color to the quantity text
            text_widget.tag_add("red_color", start_idx, end_tag_start)
            start_idx = end_tag_start

        # Apply green color formatting for x symbol
        start_idx = '1.0'
        while True:
            start_idx = text_widget.search('[GREEN]', start_idx, stopindex=tk.END)
            if not start_idx:
                break
            end_tag_start = text_widget.search('[/GREEN]', start_idx, stopindex=tk.END)
            if not end_tag_start:
                break
            
            # Remove the tags and apply color
            text_widget.delete(start_idx, f"{start_idx}+7c")
            end_tag_start = text_widget.search('[/GREEN]', start_idx, stopindex=tk.END)
            text_widget.delete(end_tag_start, f"{end_tag_start}+8c")
            
            # Apply color to the x symbol
            text_widget.tag_add("green_color", start_idx, end_tag_start)
            start_idx = end_tag_start

        # Apply special formatting for "Overall Total Requirements" header
        start_idx = '1.0'
        while True:
            start_idx = text_widget.search('Overall Total Requirements', start_idx, stopindex=tk.END)
            if not start_idx:
                break
            end_idx = f"{start_idx}+26c"
            text_widget.tag_add('section_header', start_idx, end_idx)
            start_idx = end_idx
        
        # Apply special formatting for item headers
        item_names = [
            "Stardust Mining", "Water Pump", "Osmosis Water Purifier",
            "Super Refinery", "Rainwater", "Small Water Pump", "Brewing Barrel",
            "Water Tank", "Securement", "Normal Refinery", "Furnace", "Blue Light",
            "Radio", "ADVHydraulic", "ADVBiomass", "Deviation"
        ]

        for item in item_names:
            start_idx = "1.0"
            while True:
                start_idx = text_widget.search(item, start_idx, stopindex=tk.END)
                if not start_idx:
                    break
                line_end = text_widget.index(f"{start_idx} lineend")
                line_text = text_widget.get(start_idx, line_end)
                if " Requirements:" in line_text or "Requirements:" in line_text:
                    text_widget.tag_add("item_header", start_idx, line_end)
                start_idx = f"{start_idx}+1c"
        
        # Bold material names in the overall section
        start_idx = '1.0'
        overall_start = text_widget.search('Overall Total Requirements', '1.0', stopindex=tk.END)
        if overall_start:
            search_start = f"{overall_start}+1l"
            current_idx = search_start
            while True:
                current_idx = text_widget.search(':', current_idx, stopindex=tk.END)
                if not current_idx:
                    break
                line_start = text_widget.index(f"{current_idx} linestart")
                line_text = text_widget.get(line_start, current_idx)
                
                if "Watt" not in line_text:
                    text_widget.tag_add("material_name", line_start, current_idx)
                current_idx = f"{current_idx}+1c"
        
        # Make "Watt" stand out in red
        start_idx = '1.0'
        while True:
            start_idx = text_widget.search('Watt:', start_idx, stopindex=tk.END)
            if not start_idx:
                break
            end_idx = f"{start_idx}+5c"
            text_widget.tag_remove("material_name", start_idx, end_idx)
            text_widget.tag_add('red', start_idx, end_idx)
            start_idx = end_idx

    # Insert initial report (do this later after creating all UI elements)
    # We'll insert and format the text after defining all functions
    
    # Create a modern search bar with gray theme
    search_frame = tk.Frame(frame, bg="#F3F4F6")
    search_frame.pack(pady=(0, 10), fill=tk.X)
    elements_to_hide.append(search_frame)  # Add to hide list
    
    # Search icon label
    search_icon = tk.Label(
        search_frame,
        text="🔍",
        bg="#F3F4F6",
        font=("Segoe UI", 12)
    )
    search_icon.pack(side=tk.LEFT, padx=(0, 5))
    
    # Modern search entry
    search_entry = tk.Entry(
        search_frame, 
        width=35,
        font=("Segoe UI", 11),
        bg="#FFFFFF",
        fg="#1F2937",
        relief="solid",
        borderwidth=1,
        insertbackground="#6B7280"
    )
    search_entry.pack(side=tk.LEFT, padx=5, ipady=5)
    
    # Modern search button with gray theme
    search_button = tk.Button(
        search_frame, 
        text="Search", 
        command=search_text,
        bg="#6B7280",
        fg="#FFFFFF",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        borderwidth=0,
        cursor="hand2",
        padx=20,
        pady=5
    )
    search_button.pack(side=tk.LEFT, padx=5)
    
    # Hover effect for search button
    def on_enter_search(e):
        search_button['bg'] = '#4B5563'
    
    def on_leave_search(e):
        search_button['bg'] = '#6B7280'
    
    search_button.bind("<Enter>", on_enter_search)
    search_button.bind("<Leave>", on_leave_search)
    
    # Function to open material transfer selection dialog
    def open_transfer_selection():
        """Open dialog to select which materials should show transfer costs"""
        dialog = tk.Toplevel(report_window)
        dialog.title("⚙ Transfer Cost Settings")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.configure(bg="#F3F4F6")
        
        if app_icon:
            dialog.iconphoto(False, app_icon)
        
        # Gray themed header frame
        header_frame = tk.Frame(dialog, bg="#4B5563", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame, 
            text="⚙  Transfer Cost Settings", 
            bg="#4B5563", 
            fg="#F9FAFB",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=22)
        
        # Modern instructions with icon
        instructions_frame = tk.Frame(dialog, bg="#F3F4F6")
        instructions_frame.pack(pady=15, padx=20)
        
        tk.Label(
            instructions_frame, 
            text="💡 Select which materials should show transfer costs:",
            bg="#F3F4F6", 
            fg="#374151",
            font=("Segoe UI", 11)
        ).pack()
        
        # Create frame for scrollable content with card design
        content_frame = tk.Frame(dialog, bg="#F3F4F6")
        content_frame.pack(fill="both", expand=True, padx=25, pady=(0, 15))
        
        # Card container for list
        card_frame = tk.Frame(content_frame, bg="#FFFFFF", relief="flat")
        card_frame.pack(fill="both", expand=True)
        
        # Create scrollable frame
        canvas_dialog = tk.Canvas(card_frame, bg="#FFFFFF", highlightthickness=0)
        scrollbar_dialog = tk.Scrollbar(card_frame, orient="vertical", command=canvas_dialog.yview)
        scrollable_frame = tk.Frame(canvas_dialog, bg="#FFFFFF")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_dialog.configure(scrollregion=canvas_dialog.bbox("all"))
        )
        
        canvas_dialog.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_dialog.configure(yscrollcommand=scrollbar_dialog.set)
        
        canvas_dialog.pack(side="left", fill="both", expand=True)
        scrollbar_dialog.pack(side="right", fill="y")
        
        # Create modern checkboxes for each material with a cost
        checkbox_vars = {}
        for i, (material, cost) in enumerate(sorted(MATERIAL_COSTS.items())):
            if cost > 0:  # Only show materials that have a transfer cost
                var = tk.BooleanVar(value=SHOW_TRANSFER_FOR.get(material, False))
                checkbox_vars[material] = var
                
                # Alternating row colors for better readability
                row_bg = "#F9FAFB" if i % 2 == 0 else "#FFFFFF"
                
                # Create a frame for each checkbox item
                item_frame = tk.Frame(scrollable_frame, bg=row_bg)
                item_frame.pack(fill="x", pady=1, padx=0)
                
                # Checkbox with material name
                cb = tk.Checkbutton(
                    item_frame,
                    text=f"  {material}",
                    variable=var,
                    bg=row_bg,
                    activebackground=row_bg,
                    font=("Segoe UI", 10),
                    cursor="hand2",
                    selectcolor="#FFFFFF"
                )
                cb.pack(side="left", padx=15, pady=8)
                
                # Cost badge
                cost_label = tk.Label(
                    item_frame, 
                    text=f"{cost} per unit", 
                    bg=row_bg, 
                    fg="#6B7280",
                    font=("Segoe UI", 9)
                )
                cost_label.pack(side="left", padx=5)
        
        # Modern button frame with separator
        separator_dialog = tk.Frame(dialog, bg="#E5E7EB", height=1)
        separator_dialog.pack(fill="x", pady=(15, 0))
        
        button_frame = tk.Frame(dialog, bg="#F3F4F6")
        button_frame.pack(fill="x", padx=25, pady=20)
        
        # Save button
        def save_selection():
            for material, var in checkbox_vars.items():
                SHOW_TRANSFER_FOR[material] = var.get()
            # Save settings to file
            save_transfer_settings()
            dialog.destroy()
            # Live update the report
            if raw_data:
                refresh_display()
        
        # Cancel button
        def cancel_selection():
            dialog.destroy()
        
        # Gray themed Save button
        save_btn = tk.Button(
            button_frame, 
            text="✓  Save Changes", 
            command=save_selection,
            bg="#4B5563",
            fg="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            borderwidth=0,
            relief="flat",
            cursor="hand2",
            padx=30,
            pady=10
        )
        save_btn.pack(side="left", padx=5)
        
        # Hover effect for save button
        def on_enter_save(e):
            save_btn['bg'] = '#374151'
        
        def on_leave_save(e):
            save_btn['bg'] = '#4B5563'
        
        save_btn.bind("<Enter>", on_enter_save)
        save_btn.bind("<Leave>", on_leave_save)
        
        # Gray themed Cancel button
        cancel_btn = tk.Button(
            button_frame, 
            text="✕  Cancel", 
            command=cancel_selection,
            bg="#9CA3AF",
            fg="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            borderwidth=0,
            relief="flat",
            cursor="hand2",
            padx=30,
            pady=10
        )
        cancel_btn.pack(side="left", padx=5)
        
        # Hover effect for cancel button
        def on_enter_cancel(e):
            cancel_btn['bg'] = '#6B7280'
        
        def on_leave_cancel(e):
            cancel_btn['bg'] = '#9CA3AF'
        
        cancel_btn.bind("<Enter>", on_enter_cancel)
        cancel_btn.bind("<Leave>", on_leave_cancel)
    
    # Gray themed buttons frame with separator
    separator = tk.Frame(frame, bg="#E5E7EB", height=1)
    separator.pack(fill=tk.X, pady=(0, 15))
    elements_to_hide.append(separator)  # Add separator to hide list
    
    buttons_frame = tk.Frame(frame, bg="#F3F4F6")
    buttons_frame.pack(pady=0)
    elements_to_hide.append(buttons_frame)  # Add to hide list
    
    # Close window function
    def close_window():
        report_window.destroy()

    # Transfer Settings button - only show if checkbox was ticked (gray theme)
    if show_transfer_button:
        transfer_btn = tk.Button(
            buttons_frame, 
            text="⚙  Transfer Settings", 
            command=open_transfer_selection,
            bg="#6B7280",
            fg="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            borderwidth=0,
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=10
        )
        transfer_btn.pack(side=tk.LEFT, padx=8)
        
        # Hover effects for transfer button
        def on_enter_transfer(e):
            transfer_btn['bg'] = '#4B5563'
        
        def on_leave_transfer(e):
            transfer_btn['bg'] = '#6B7280'
        
        transfer_btn.bind("<Enter>", on_enter_transfer)
        transfer_btn.bind("<Leave>", on_leave_transfer)

    # Close button with gray theme
    ok_button = tk.Button(
        buttons_frame, 
        text="✓  Close", 
        command=close_window,
        bg="#4B5563",
        fg="#FFFFFF",
        font=("Segoe UI", 11, "bold"),
        borderwidth=0,
        relief="flat",
        cursor="hand2",
        padx=25,
        pady=10
    )
    ok_button.pack(side=tk.LEFT, padx=8)
    
    # Hover effects for Close button
    def on_enter_ok(e):
        ok_button['bg'] = '#374151'
    
    def on_leave_ok(e):
        ok_button['bg'] = '#4B5563'
    
    ok_button.bind("<Enter>", on_enter_ok)
    ok_button.bind("<Leave>", on_leave_ok)
    
    # Now insert and format the report text
    text_widget.config(state=tk.NORMAL)
    text_widget.insert(tk.END, report)
    apply_formatting()
    text_widget.config(state=tk.DISABLED)
    
    # Scroll to Overall Total Requirements section
    overall_pos = text_widget.search('Overall Total Requirements', '1.0', stopindex=tk.END)
    
    if overall_pos:
        # Scroll to show the overall section
        text_widget.see(overall_pos)
        # Move up a bit to show some context
        line_num = int(overall_pos.split('.')[0])
        if line_num > 3:
            text_widget.see(f"{line_num - 3}.0")
    else:
        # If not found, scroll to the bottom
        text_widget.see(tk.END)

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
    RUBBER = 10
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
            'Rubber': self.RUBBER * self.quantity,
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
    RUBBER = 20
    ACID = 15
    WATT = 10

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Log': self.LOG * self.quantity,
            'Adhesive': self.ADHESIVE * self.quantity,
            'Aluminum Ingot': self.ALUMINUM_INGOT * self.quantity,
            'Rubber': self.RUBBER * self.quantity,
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
    RUBBER = 20
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
            'Rubber': self.RUBBER * self.quantity,
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
    RUBBER = 10

    def __init__(self, quantity):
        self.quantity = quantity

    def total_requirements(self):
        return {
            'Log': self.LOG * self.quantity,
            'Adhesive': self.ADHESIVE * self.quantity,
            'Electronic Part': self.ELECTRONIC_PART * self.quantity,
            'Rubber': self.RUBBER * self.quantity
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
                # Get the quantity for this item
                quantity = obj.quantity
                detailed_report += f"{name} [GREEN]X[/GREEN][RED]{quantity}[/RED] Requirements:\n"
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
        
        # Save the item details part before adding overall
        item_details_report = detailed_report

        detailed_report += "\nOverall Total Requirements:\n"
        total_watt = filtered_totals.pop('Watt', 0)  # Extract 'Watt' if present

        # Separate materials that should show transfer cost from those that shouldn't
        materials_with_transfer = {}
        materials_without_transfer = {}
        
        for material, amount in filtered_totals.items():
            # Check if this material should show transfer cost
            if SHOW_TRANSFER_FOR.get(material, False) and MATERIAL_COSTS.get(material, 0) > 0:
                materials_with_transfer[material] = amount
            else:
                materials_without_transfer[material] = amount

        # Calculate total cost if checkbox is checked
        total_cost = 0
        if show_costs_var.get():
            for material, amount in materials_with_transfer.items():
                cost = MATERIAL_COSTS.get(material, 0)
                total_cost += amount * cost

        # First show materials with transfer cost
        for material, amount in materials_with_transfer.items():
            if show_costs_var.get():  # If checkbox is checked, show costs
                cost = MATERIAL_COSTS.get(material, 0)
                total = amount * cost
                detailed_report += f"{material}: {amount} → [COST]{total}[/COST]\n"
            else:  # If checkbox is unchecked, show simple format
                detailed_report += f"{material}: {amount}\n"

        # Then show materials without transfer cost
        for material, amount in materials_without_transfer.items():
            detailed_report += f"{material}: {amount}\n"

        # Add Watt
        if total_watt > 0:
            detailed_report += f"Watt: {total_watt}\n"

        # Add total cost under Watt if checkbox is checked with smart character splitting
        if show_costs_var.get() and total_cost > 0:
            if total_cost > 20000:
                import math
                
                detailed_report += f"\n{'='*50}\n"
                detailed_report += f"[WARNING]⚠ Total Transfer Cost: {total_cost:,} (exceeds 20,000 limit)[/WARNING]\n"
                detailed_report += f"{'='*50}\n\n"
                
                # Create list of (material, amount, unit_cost, total_cost) tuples
                material_list = []
                for material, amount in materials_with_transfer.items():
                    unit_cost = MATERIAL_COSTS.get(material, 0)
                    mat_total = amount * unit_cost
                    material_list.append({
                        'name': material,
                        'amount': amount,
                        'unit_cost': unit_cost,
                        'total_cost': mat_total
                    })
                
                # Sort by total cost (descending) for better filling
                material_list.sort(key=lambda x: x['total_cost'], reverse=True)
                
                # Split into characters
                characters = []
                current_char = {'materials': [], 'total_cost': 0}
                
                for mat in material_list:
                    remaining_amount = mat['amount']
                    
                    while remaining_amount > 0:
                        # Calculate how much we can fit in current character
                        space_left = 20000 - current_char['total_cost']
                        
                        # Calculate max quantity that fits in remaining space
                        max_qty = space_left // mat['unit_cost'] if mat['unit_cost'] > 0 else remaining_amount
                        
                        # Take the minimum of what's needed and what fits
                        qty_to_add = min(remaining_amount, max_qty)
                        
                        if qty_to_add > 0:
                            cost_to_add = qty_to_add * mat['unit_cost']
                            current_char['materials'].append({
                                'name': mat['name'],
                                'amount': qty_to_add,
                                'cost': cost_to_add
                            })
                            current_char['total_cost'] += cost_to_add
                            remaining_amount -= qty_to_add
                        
                        # If character is full or no more room, start new character
                        if remaining_amount > 0 or current_char['total_cost'] >= 19900:  # Leave small buffer
                            if current_char['materials']:  # Only save if has materials
                                characters.append(current_char)
                            current_char = {'materials': [], 'total_cost': 0}
                
                # Add last character if has materials
                if current_char['materials']:
                    characters.append(current_char)
                
                # Display character assignments
                detailed_report += f"[TOTAL]📦 Split across {len(characters)} character(s):[/TOTAL]\n\n"
                
                for idx, char in enumerate(characters, 1):
                    detailed_report += f"[SECTION]Character {idx} (Total: {char['total_cost']:,}):[/SECTION]\n"
                    for mat in char['materials']:
                        detailed_report += f"  {mat['name']}: {mat['amount']} → [COST]{mat['cost']:,}[/COST]\n"
                    detailed_report += "\n"
                
            else:
                detailed_report += f"[TOTAL]Total Transfer Cost: {total_cost:,}[/TOTAL]\n"

        if detailed_report:
            # Prepare raw data for live updates
            raw_data = {
                'filtered_totals': filtered_totals.copy(),
                'show_costs': show_costs_var.get(),
                'item_details': item_details_report  # Include individual item requirements
            }
            # Add Watt back to filtered_totals for raw_data
            if total_watt > 0:
                raw_data['filtered_totals']['Watt'] = total_watt
            
            show_formatted_report(detailed_report, show_transfer_button=show_costs_var.get(), raw_data=raw_data)
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
    return str(Path(base_path) / "assets" / path)

def load_image(image_path):
    """Load an image from a path with caching."""
    try:
        image = PhotoImage(file=relative_to_assets(image_path))
        return image
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

# Function to load transfer settings from file
def load_transfer_settings():
    """Load transfer settings from assets/transfer_settings.txt"""
    settings_file = relative_to_assets("transfer_settings.txt")
    try:
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        material, value = line.split('=', 1)
                        material = material.strip()
                        value = value.strip().lower()
                        if material in SHOW_TRANSFER_FOR:
                            SHOW_TRANSFER_FOR[material] = (value == 'true')
    except Exception as e:
        print(f"Error loading transfer settings: {e}")

# Function to save transfer settings to file
def save_transfer_settings():
    """Save transfer settings to assets/transfer_settings.txt"""
    settings_file = relative_to_assets("transfer_settings.txt")
    try:
        with open(settings_file, 'w') as f:
            f.write("# Transfer Cost Settings\n")
            f.write("# Format: Material Name = true/false\n\n")
            for material in sorted(SHOW_TRANSFER_FOR.keys()):
                if MATERIAL_COSTS.get(material, 0) > 0:  # Only save materials with costs
                    f.write(f"{material} = {str(SHOW_TRANSFER_FOR[material]).lower()}\n")
    except Exception as e:
        print(f"Error saving transfer settings: {e}")

window = tk.Tk()
window.geometry("1348x785")
window.configure(bg="#FFFFFF")
window.title("Once Human Tool Helper By Brëakdown")

# Load transfer settings from file
load_transfer_settings()

# Hide window during loading for smoother startup
window.withdraw()

# Disable window updates during setup for faster rendering
window.update_idletasks()

bold_font = font.Font(weight="bold")

# Create checkbox variable for showing costs
show_costs_var = tk.BooleanVar()
show_costs_var.set(False)  # Default to not showing costs

# Load images after creating the root window (optimized loading)
app_icon = load_image("appicon1.png")
main_images = [load_image(f"image_{i}.png") for i in range(1, 18)]
entry_images = [load_image(f"entry_{i}.png") for i in range(1, 17)]
button_image = load_image("button_1.png")


# Set up icon if possible
if app_icon:
    window.iconphoto(False, app_icon)

# Create frames for different pages
frame1 = tk.Frame(window, bg="#FFFFFF")
frame2 = tk.Frame(window, bg="#FFFFFF")

# Animation function for smooth transitions
def animate_transition(from_frame, to_frame, direction='right'):
    """Animate transition between frames with slide effect"""
    # Determine slide direction
    if direction == 'right':
        start_x = 1348  # Start from right
        end_x = 0
        from_end_x = -1348  # Exit to left
    else:  # left
        start_x = -1348  # Start from left
        end_x = 0
        from_end_x = 1348  # Exit to right
    
    # Raise the to_frame to be on top
    to_frame.lift()
    
    # Place both frames
    from_frame.place(x=0, y=0, width=1348, height=785)
    to_frame.place(x=start_x, y=0, width=1348, height=785)
    
    # Animation parameters - faster transition
    steps = 10  # Number of animation steps (reduced for faster animation)
    delay = 8  # Milliseconds between steps (reduced for faster animation)
    
    def slide_step(step):
        if step <= steps:
            # Calculate positions
            progress = step / steps
            to_x = start_x + (end_x - start_x) * progress
            from_x = 0 + (from_end_x - 0) * progress
            
            # Update positions
            to_frame.place(x=int(to_x), y=0, width=1348, height=785)
            from_frame.place(x=int(from_x), y=0, width=1348, height=785)
            
            # Schedule next step
            window.after(delay, lambda: slide_step(step + 1))
        else:
            # Animation complete - clean up
            # Move from_frame far off screen instead of place_forget
            from_frame.place(x=5000, y=0, width=1348, height=785)
            from_frame.lower()
            # Position to_frame correctly
            to_frame.place(x=0, y=0, width=1348, height=785)
            to_frame.lift()
            to_frame.tkraise()
            # Set focus to the new frame
            to_frame.focus_set()
            # Update to ensure proper stacking
            window.update_idletasks()
    
    # Start animation
    slide_step(0)

# Function to show frame 1
def show_frame1():
    # Unbind mousewheel when leaving frame2
    try:
        scroll_canvas.unbind_all("<MouseWheel>")
    except:
        pass
    # Lower frame2 to ensure frame1 is accessible
    frame2.lower()
    animate_transition(frame2, frame1, direction='left')

# Function to show frame 2
def show_frame2():
    # Lower frame1 to ensure frame2 is accessible
    frame1.lower()
    animate_transition(frame1, frame2, direction='right')

# Initially show frame 1
frame1.place(x=0, y=0, width=1348, height=785)

# ===== FRAME 1 CONTENT =====
canvas = Canvas(
    frame1, bg="#FFFFFF", height=785, width=1348, bd=0,
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

# Create entry backgrounds and widgets together
for x, y, img in entry_positions:
    if img:
        canvas.create_image(x, y, image=img)
        entry = Entry(
            frame1,
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

canvas.create_text(440.0, 43.0, anchor="nw", text="Alt Base Materials Calculator ", fill="#FFFFFF", font=("Inter Bold", 40 * -1))

# Add checkbox for showing costs (no text label)
cost_checkbox = tk.Checkbutton(
    frame1, 
    text="", 
    variable=show_costs_var,
    bg="#FFFFFF",
    activebackground="#FFFFFF",
    selectcolor="#FFFFFF"
)
cost_checkbox.place(x=970, y=660)

# Set up buttons on frame1
if button_image:
    Button(
        frame1, image=button_image, borderwidth=0,
        highlightthickness=0, command=calculate_requirements,
        relief="flat"
    ).place(x=375.0, y=634.0, width=588.0, height=85.0)

# Add navigation button to go to Frame 2
nav_button = Button(
    frame1, text="Next Page →", 
    command=show_frame2,
    bg="#2C2C2C", fg="#FFFFFF",
    font=("Inter Bold", 16),
    borderwidth=2,
    relief="flat",
    cursor="hand2",
    activebackground="#404040",
    activeforeground="#FFFFFF",
    highlightthickness=0,
    padx=20,
    pady=10
)
nav_button.place(x=1120, y=40, width=180, height=50)

# Add hover effect for nav button
def on_enter_nav(e):
    nav_button['bg'] = '#404040'
    nav_button['font'] = ('Inter Bold', 17)

def on_leave_nav(e):
    nav_button['bg'] = '#2C2C2C'
    nav_button['font'] = ('Inter Bold', 16)

nav_button.bind("<Enter>", on_enter_nav)
nav_button.bind("<Leave>", on_leave_nav)



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

# Character data storage
selected_memetics = {}  # {memetic_name: True/False}
characters_file = relative_to_assets("characters.txt")

def save_character_data(char_name):
    """Save character's selected memetics to file in readable format"""
    server = server_var.get()
    
    try:
        # Read existing data
        existing_data = []
        if os.path.exists(characters_file):
            with open(characters_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                # Split by character entries (each starts with "Character:")
                if content:
                    entries = content.split('\n\nCharacter: ')
                    if entries:
                        # First entry might have "Character: " prefix
                        if entries[0].startswith('Character: '):
                            existing_data = [entries[0]]
                            existing_data.extend(['Character: ' + e for e in entries[1:]])
                        else:
                            existing_data = [entries[0]] + ['Character: ' + e for e in entries[1:]]
        
        # Remove old entry for same server+character
        existing_data = [entry for entry in existing_data 
                        if entry.strip() and not (f"Character: {char_name}\nServer: {server.lower()}" in entry)]
        
        # Create new formatted entry
        new_entry = f"Character: {char_name}\nServer: {server.lower()}\n"
        
        # Group selected memetics by level and category
        level_groups = {"5-15": {}, "20-35": {}, "40-50": {}}
        
        for name, sel in selected_memetics.items():
            if sel:
                # Find this memetic in memetic_data
                for m_name, m_level, m_category, m_server in memetic_data:
                    if m_name == name:
                        if m_level not in level_groups:
                            level_groups[m_level] = {}
                        if m_category not in level_groups[m_level]:
                            level_groups[m_level][m_category] = []
                        level_groups[m_level][m_category].append(name)
                        break
        
        # Format output - ensure each memetic line ends with \n
        for level in ["5-15", "20-35", "40-50"]:
            if level in level_groups:
                for category in ["Gathering", "Building", "Crafting", "Management"]:
                    if category in level_groups[level] and level_groups[level][category]:
                        for memetic_name in level_groups[level][category]:
                            new_entry += f"Level {level} ({category}): {memetic_name}\n"
        
        # Add new entry
        existing_data.append(new_entry.strip())  # Strip trailing newline from entry
        
        # Write back with double newline separation between entries
        with open(characters_file, 'w', encoding='utf-8') as f:
            # Join with \n\n and add newline at start and end of file
            f.write('\n' + '\n\n'.join(existing_data) + '\n')
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save character: {e}")

def detect_and_update_character_display():
    """Automatically detect character based on selected memetics"""
    server = server_var.get()
    
    # Define character patterns to detect
    character_patterns = {
        "Furnace Hero (Manibus)": {
            "server": "Manibus",
            "memetics": [
                "Furnace: Precision Refining",
                "Electric Furnace: Efficiency Lover",
                "Furnace: Sintering",
                "Electric Furnace: Electrolysis"
            ]
        },
        "Furnace Hero (Edream)": {
            "server": "Edream",
            "memetics": [
                "Furnace: Precision Refining",
                "Furnace: Large Furnace",
                "Electric Furnace: Efficiency Lover",
                "Furnace: Chaosium Material Analysis",
                "Furnace: Sintering",
                "Electric Furnace: Electrolysis"
            ]
        },
        "Kitchen Hero": {
            "server": "All",
            "memetics": [
                "Stove: Long-Term Storage",
                "Kitchen Set: Gourmand"
            ]
        },
        "Disassembly Hero": {
            "server": "All",
            "memetics": [
                "Disassembly Bench: Careful Disassembly",
                "Disassembly Bench: Electronic Recycling"
            ]
        },
        "Electricity Hero (Manibus)": {
            "server": "Manibus",
            "memetics": [
                "Biomass Generator: Sustained Output",
                "Generator: Electrical Expert",
                "Hydraulic Generator: One with the Tides",
                "Deviant Power Generator: Stardust Unleashed"
            ]
        },
        "Electricity Hero (Edream)": {
            "server": "Edream",
            "memetics": [
                "Biomass Generator: Sustained Output",
                "Generator: Electrical Expert",
                "Generator: Heat Dissipation",
                "Biomass Generator: Heat Generator",
                "Hydraulic Generator: One with the Tides",
                "Deviant Power Generator: Stardust Unleashed",
                "Deviant Power Generator: Energy Extraction"
            ],
            "priority": 1  # Highest priority
        },
        "Biomass Hero": {
            "server": "Edream",
            "memetics": [
                "Biomass Generator: Sustained Output",
                "Generator: Electrical Expert",
                "Generator: Heat Dissipation",
                "Biomass Generator: Heat Generator",
                "Hydraulic Generator: One with the Tides"
            ],
            "priority": 2
        },
        "Deviation Hero": {
            "server": "Edream",
            "memetics": [
                "Hydraulic Generator: One with the Tides",
                "Deviant Power Generator: Stardust Unleashed",
                "Deviant Power Generator: Energy Extraction",
                "Generator: Electrical Expert"
            ],
            "priority": 3
        },
        "Workbench Hero (Manibus)": {
            "server": "Manibus",
            "memetics": [
                "Supplies Workbench: Ammo Factory",
                "Supplies Workbench: Healing Boost",
                "Supplies Workbench: Anti-Armor"
            ]
        },
        "Workbench Hero (Edream)": {
            "server": "Edream",
            "memetics": [
                "Supplies Workbench: Ammo Factory",
                "Supplies Workbench: Forest Hunter",
                "Supplies Workbench: Healing Boost",
                "Supplies Workbench: Anti-Armor"
            ]
        }
    }
    
    # Get currently selected memetics
    current_selections = [name for name, selected in selected_memetics.items() if selected]
    
    # Check each character pattern and collect all matches
    detected_characters = []
    priority_groups = {}  # Track matches by priority group
    
    for char_name, pattern in character_patterns.items():
        # Check if server matches (pattern server "All" matches any server)
        if pattern["server"].lower() != "all" and pattern["server"].lower() != server.lower():
            continue
        
        # Check if all memetics are selected
        all_selected = all(memetic in current_selections for memetic in pattern["memetics"])
        
        if all_selected:
            priority = pattern.get("priority", 0)
            if priority > 0:
                # Track priority-based matches separately
                if priority not in priority_groups:
                    priority_groups[priority] = []
                priority_groups[priority].append(char_name)
            else:
                # Non-priority matches are always added
                detected_characters.append(char_name)
    
    # Add only the highest priority match from priority groups
    if priority_groups:
        highest_priority = min(priority_groups.keys())  # Lower number = higher priority
        detected_characters.extend(priority_groups[highest_priority])
    
    # Update display
    character_display_text.config(state=tk.NORMAL)
    character_display_text.delete("1.0", tk.END)
    
    if detected_characters:
        # Clean up names by removing server suffix (Manibus/Edream)
        clean_names = []
        for name in detected_characters:
            clean_name = name.replace(" (Manibus)", "").replace(" (Edream)", "")
            clean_names.append(clean_name)
        
        # Join multiple character names with " + "
        display_text = " + ".join(clean_names)
        character_display_text.insert("1.0", display_text)
        character_display_text.tag_add("center", "1.0", "end")
        character_display_text.tag_config("center", justify='center')
    
    character_display_text.config(state=tk.DISABLED)

def update_character_display(char_name):
    """Update the character display text widget with character name"""
    
    # Enable text widget for editing
    character_display_text.config(state=tk.NORMAL)
    character_display_text.delete("1.0", tk.END)
    
    # Just display the character name centered
    if char_name:
        display_text = char_name
    else:
        display_text = ""
    
    character_display_text.insert("1.0", display_text)
    character_display_text.tag_add("center", "1.0", "end")
    character_display_text.tag_config("center", justify='center')
    character_display_text.config(state=tk.DISABLED)

def load_character_data(char_name):
    """Load character's selected memetics from file (readable format)"""
    server = server_var.get()
    
    try:
        if not os.path.exists(characters_file):
            messagebox.showinfo("Info", "No saved characters found!")
            return
        
        with open(characters_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            messagebox.showinfo("Info", "No saved characters found!")
            return
        
        # Split by character entries (handle newlines properly)
        entries = content.split('\n\nCharacter: ')
        
        # Process entries
        processed_entries = []
        for i, entry in enumerate(entries):
            entry = entry.strip()
            if not entry:
                continue
            # Add "Character: " prefix if it's not the first entry or if it doesn't have it
            if i == 0 and entry.startswith('Character: '):
                processed_entries.append(entry)
            elif not entry.startswith('Character: '):
                processed_entries.append('Character: ' + entry)
            else:
                processed_entries.append(entry)
        
        # Find matching character
        for entry in processed_entries:
            if not entry.strip():
                continue
            
            lines = entry.strip().split('\n')
            if len(lines) < 2:
                continue
            
            # Parse character and server
            entry_char = lines[0].replace('Character: ', '').strip()
            entry_server = lines[1].replace('Server: ', '').strip()
            
            if entry_char == char_name and entry_server == server.lower():
                # Found the character - parse memetics
                selected_list = []
                for line in lines[2:]:
                    line = line.strip()
                    if line.startswith('Level '):
                        # Extract memetic name after ": "
                        if ': ' in line:
                            memetic_name = line.split(': ', 1)[1].strip()
                            selected_list.append(memetic_name)
                
                # Update selected memetics
                for name in selected_memetics:
                    selected_memetics[name] = name in selected_list
                
                # Update character display
                update_character_display(char_name)
                
                # Refresh the display to show selections
                apply_filter(filter_var.get())
                messagebox.showinfo("Success", f"Loaded '{char_name}' from {server}!")
                return
        
        messagebox.showinfo("Info", f"Character '{char_name}' not found on {server}!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load character: {e}")

def load_character_choices():
    """Load saved character choices for current server"""
    global selected_memetics
    selected_memetics = {}
    # Initialize all memetics as unselected
    for name, level, cat, srv in memetic_data:
        selected_memetics[name] = False

def update_character_list():
    """Update character dropdown with saved characters for current server"""
    server = server_var.get()
    characters = set()
    
    try:
        if os.path.exists(characters_file):
            with open(characters_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                character_dropdown['values'] = []
                return
            
            # Split by character entries (handle newlines properly)
            entries = content.split('\n\nCharacter: ')
            
            # Process entries
            processed_entries = []
            for i, entry in enumerate(entries):
                entry = entry.strip()
                if not entry:
                    continue
                # Add "Character: " prefix if it's not the first entry or if it doesn't have it
                if i == 0 and entry.startswith('Character: '):
                    processed_entries.append(entry)
                elif not entry.startswith('Character: '):
                    processed_entries.append('Character: ' + entry)
                else:
                    processed_entries.append(entry)
            
            # Parse each entry
            for entry in processed_entries:
                if not entry.strip():
                    continue
                
                lines = entry.strip().split('\n')
                if len(lines) < 2:
                    continue
                
                # Parse character and server
                entry_char = lines[0].replace('Character: ', '').strip()
                entry_server = lines[1].replace('Server: ', '').strip()
                
                if entry_server == server.lower():
                    characters.add(entry_char)
        
        character_dropdown['values'] = sorted(list(characters))
    except Exception as e:
        print(f"Error loading character list: {e}")

# ===== FRAME 2 CONTENT - MEMETIC SPECIALIZATIONS =====
canvas2 = Canvas(
    frame2, bg="#FFFFFF", height=785, width=1348, bd=0,
    highlightthickness=0, relief="ridge"
)
canvas2.place(x=0, y=0)

# Add image_3.png to canvas2 (header background)
if main_images[2]:  # image_3.png is at index 2
    canvas2.create_image(674.0, 65.0, image=main_images[2])

# Add title text to canvas2
canvas2.create_text(475.0, 43.0, anchor="nw", text="Alt Memetic Specializations ", fill="#FFFFFF", font=("Inter Bold", 40 * -1))

# Server selection frame
server_frame = tk.Frame(frame2, bg="#F5F5F5", highlightthickness=1, highlightbackground="#CCCCCC")
server_frame.place(x=55, y=140, width=300, height=50)

tk.Label(server_frame, text="Server:", bg="#F5F5F5", fg="#333333", font=("Inter Bold", 14)).place(x=10, y=12)

# Server buttons
server_var = tk.StringVar(value="Manibus")
server_buttons = {}

def select_server(server_name):
    server_var.set(server_name)
    # Update button colors
    for srv_name, srv_btn in server_buttons.items():
        if srv_name == server_name:
            srv_btn.config(bg="#4069D5", fg="#FFFFFF")
        else:
            srv_btn.config(bg="#E0E0E0", fg="#000000")
    # Reload character data for selected server
    load_character_choices()
    update_character_list()
    # Refresh the card display to show server-specific cards
    apply_filter(filter_var.get())

manibus_btn = tk.Button(
    server_frame, text="Manibus", command=lambda: select_server("Manibus"),
    bg="#4069D5", fg="#FFFFFF", font=("Inter Black", 12),
    borderwidth=0, relief="flat", cursor="hand2"
)
manibus_btn.place(x=80, y=10, width=100, height=30)
server_buttons["Manibus"] = manibus_btn

edream_btn = tk.Button(
    server_frame, text="Edream", command=lambda: select_server("Edream"),
    bg="#E0E0E0", fg="#000000", font=("Inter Black", 12),
    borderwidth=0, relief="flat", cursor="hand2"
)
edream_btn.place(x=190, y=10, width=100, height=30)
server_buttons["Edream"] = edream_btn

# Character name frame
character_frame = tk.Frame(frame2, bg="#F5F5F5", highlightthickness=1, highlightbackground="#CCCCCC")
character_frame.place(x=370, y=140, width=530, height=50)

tk.Label(character_frame, text="Character:", bg="#F5F5F5", fg="#333333", font=("Inter Bold", 14)).place(x=10, y=12)

# Character name dropdown
character_var = tk.StringVar()
character_dropdown = ttk.Combobox(
    character_frame, textvariable=character_var,
    font=("Inter", 11), state="normal", width=22
)
character_dropdown.place(x=110, y=10, height=30)

# Save and Load buttons
def save_character():
    char_name = character_var.get().strip()
    if char_name:
        # Save selected memetics to file
        save_character_data(char_name)
        # Update dropdown list
        update_character_list()
        messagebox.showinfo("Success", f"Character '{char_name}' saved!")
    else:
        messagebox.showwarning("Warning", "Please enter a character name!")

def load_character():
    char_name = character_var.get().strip()
    if char_name:
        load_character_data(char_name)
    else:
        messagebox.showwarning("Warning", "Please select a character name!")

def reset_selections():
    """Reset all selections - clear character name and all selected memetics"""
    # Clear character name input
    character_var.set("")
    
    # Clear all memetic selections
    for name in selected_memetics:
        selected_memetics[name] = False
    
    # Clear character display
    character_display_text.config(state=tk.NORMAL)
    character_display_text.delete("1.0", tk.END)
    character_display_text.config(state=tk.DISABLED)
    
    # Refresh the card display to show cleared selections
    apply_filter(filter_var.get())

save_btn = tk.Button(
    character_frame, text="Save", command=save_character,
    bg="#4CAF50", fg="#FFFFFF", font=("Inter Black", 12),
    borderwidth=0, relief="flat", cursor="hand2"
)
save_btn.place(x=315, y=10, width=60, height=30)

load_btn = tk.Button(
    character_frame, text="Load", command=load_character,
    bg="#2196F3", fg="#FFFFFF", font=("Inter Black", 12),
    borderwidth=0, relief="flat", cursor="hand2"
)
load_btn.place(x=385, y=10, width=60, height=30)

reset_btn = tk.Button(
    character_frame, text="Reset", command=reset_selections,
    bg="#FF5722", fg="#FFFFFF", font=("Inter Black", 12),
    borderwidth=0, relief="flat", cursor="hand2"
)
reset_btn.place(x=455, y=10, width=60, height=30)

# Create filter frame
filter_frame = tk.Frame(frame2, bg="#F5F5F5", highlightthickness=1, highlightbackground="#CCCCCC")
filter_frame.place(x=920, y=140, width=325, height=50)

# Filter buttons
filter_var = tk.StringVar(value="All")
filter_buttons = {}

filter_buttons_data = [
    ("All", 10),
    ("Own", 70),
    ("5-15", 135),
    ("20-35", 200),
    ("40-50", 270)
]

def apply_filter(category):
    filter_var.set(category)
    
    # Update button colors
    for btn_name, btn in filter_buttons.items():
        if btn_name == category:
            btn.config(bg="#4069D5", fg="#FFFFFF")
        else:
            btn.config(bg="#E0E0E0", fg="#000000")
    
    # Clear existing cards
    for widget in cards_frame.winfo_children():
        widget.destroy()
    
    # Get current server
    current_server = server_var.get()
    
    # Filter and display cards based on category AND server
    if category == "All":
        filtered_data = [(name, level, cat, srv) for name, level, cat, srv in memetic_data 
                        if srv == "All" or srv == current_server]
    elif category == "Own":
        # Show only selected cards
        filtered_data = [(name, level, cat, srv) for name, level, cat, srv in memetic_data 
                        if selected_memetics.get(name, False) and (srv == "All" or srv == current_server)]
    elif category == "5-15":
        filtered_data = [(name, level, cat, srv) for name, level, cat, srv in memetic_data 
                        if level == "5-15" and (srv == "All" or srv == current_server)]
    elif category == "20-35":
        filtered_data = [(name, level, cat, srv) for name, level, cat, srv in memetic_data 
                        if level == "20-35" and (srv == "All" or srv == current_server)]
    elif category == "40-50":
        filtered_data = [(name, level, cat, srv) for name, level, cat, srv in memetic_data 
                        if level == "40-50" and (srv == "All" or srv == current_server)]
    else:
        # Category-specific filter (Gathering, Building, Crafting, Management)
        filtered_data = [(name, level, cat, srv) for name, level, cat, srv in memetic_data 
                        if cat == category and (srv == "All" or srv == current_server)]
    
    # Recreate cards with filtered data
    for idx, (name, level, cat, srv) in enumerate(filtered_data):
        row = idx // 6
        col = idx % 6
        create_memetic_card(cards_frame, name, level, cat, row, col)
    
    # Update scroll region with optimized refresh
    window.update_idletasks()
    scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
    # Reset scroll to top
    scroll_canvas.yview_moveto(0)

for text, x_pos in filter_buttons_data:
    btn = tk.Button(
        filter_frame,
        text=text,
        command=lambda t=text: apply_filter(t),
        bg="#4069D5" if text == "All" else "#E0E0E0",
        fg="#FFFFFF" if text == "All" else "#000000",
        font=("Inter Black", 12),
        borderwidth=0,
        relief="flat",
        cursor="hand2"
    )
    btn.place(x=x_pos, y=10, width=50, height=30)
    filter_buttons[text] = btn

# Create scrollable frame for memetic cards with optimized scrolling
scroll_canvas = Canvas(frame2, bg="#FFFFFF", highlightthickness=0)
scroll_canvas.place(x=50, y=200, width=1250, height=475)

# Create scrollbar
scrollbar = tk.Scrollbar(frame2, orient="vertical", command=scroll_canvas.yview)
scrollbar.place(x=1300, y=200, height=480)
scroll_canvas.configure(yscrollcommand=scrollbar.set)

# Create frame inside canvas for cards
cards_frame = tk.Frame(scroll_canvas, bg="#FFFFFF")
scroll_canvas.create_window((0, 0), window=cards_frame, anchor="nw")

# Create display frame below cards to show loaded character's memetics
character_display_frame = tk.Frame(frame2, bg="#F5F5F5", highlightthickness=2, highlightbackground="#CCCCCC")
character_display_frame.place(x=424, y=690, width=500, height=85)

# Add scrollable text widget for character display
character_display_text = tk.Text(
    character_display_frame, 
    bg="#F5F5F5", 
    fg="#4069D5", 
    font=("Inter Bold", 16),
    height=4,
    wrap=tk.WORD,
    borderwidth=0,
    highlightthickness=0
)
character_display_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=25)
character_display_text.config(state=tk.DISABLED)

# Optimize scrolling performance with smoother mousewheel
def on_mousewheel(event):
    scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# Bind mousewheel only when hovering over the scroll canvas area
def bind_mousewheel(event):
    scroll_canvas.bind_all("<MouseWheel>", on_mousewheel)

def unbind_mousewheel(event):
    scroll_canvas.unbind_all("<MouseWheel>")

scroll_canvas.bind("<Enter>", bind_mousewheel)
scroll_canvas.bind("<Leave>", unbind_mousewheel)

# Dictionary to store loaded memetic images
memetic_images = {}

def load_memetic_image(name):
    """Load memetic specialization image by name with caching and optimization"""
    # Check if already loaded
    if name in memetic_images:
        return memetic_images[name]
    
    # Create filename from name (handle special characters)
    # Remove colons but keep spaces and ampersands
    filename = name.replace(": ", " ").replace(":", " ").strip() + ".png"
    
    try:
        # Load and resize image to fit card (120x120) - optimized resize
        pil_img = Image.open(relative_to_assets(filename))
        # Use NEAREST for fastest performance, BILINEAR for better quality
        pil_img = pil_img.resize((120, 120), Image.Resampling.NEAREST)
        # Convert to RGB to reduce memory
        if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')
        img = ImageTk.PhotoImage(pil_img)
        memetic_images[name] = img  # Cache it
        return img
    except Exception as e:
        # Try alternative with "and" instead of "&"
        try:
            filename_alt = name.replace(": ", " ").replace(":", " ").replace(" & ", " and ").strip() + ".png"
            pil_img = Image.open(relative_to_assets(filename_alt))
            pil_img = pil_img.resize((120, 120), Image.Resampling.NEAREST)
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            img = ImageTk.PhotoImage(pil_img)
            memetic_images[name] = img  # Cache it
            return img
        except:
            print(f"Could not load image for {name}: {e}")
            memetic_images[name] = None  # Cache failure too
    return None

def create_memetic_card(parent, name, level, category, row, col):
    """Create a selectable memetic specialization card with actual image"""
    # Initialize selection state if not exists
    if name not in selected_memetics:
        selected_memetics[name] = False
    
    # Determine border color based on selection
    border_color = "#4CAF50" if selected_memetics[name] else "#CCCCCC"
    bg_color = "#E8F5E9" if selected_memetics[name] else "#F5F5F5"
    
    card = tk.Frame(parent, bg=bg_color, highlightthickness=2, highlightbackground=border_color, width=190, height=220)
    card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
    card.grid_propagate(False)  # Maintain fixed size
    
    # Load and display actual image (cached automatically)
    img = load_memetic_image(name)
    if img:
        img_label = tk.Label(card, image=img, bg=bg_color)
        img_label.pack(pady=3)
    else:
        # Fallback to placeholder if image not found
        img_label = tk.Label(card, bg="#CCCCCC", width=15, height=6, text="No Image", font=("Inter", 8))
        img_label.pack(pady=3)
    
    # Name (truncate if too long)
    display_name = name if len(name) <= 25 else name[:22] + "..."
    name_label = tk.Label(card, text=display_name, bg=bg_color, fg="#1A1A1A", font=("Inter ExtraBold", 11), wraplength=180)
    name_label.pack(pady=3)
    
    # Level and Category
    info_frame = tk.Frame(card, bg=bg_color)
    info_frame.pack(pady=5)
    tk.Label(info_frame, text=f"Lv.{level}", bg=bg_color, fg="#4069D5", font=("Inter Black", 12)).pack(side=tk.LEFT, padx=3)
    tk.Label(info_frame, text=f"• {category}", bg=bg_color, fg="#555555", font=("Inter Bold", 9)).pack(side=tk.LEFT, padx=2)
    
    # Make card clickable with level-based limits
    def toggle_selection(event=None):
        # Check current selection count for this level range
        level_selected = sum(1 for n, l, c, s in memetic_data 
                            if selected_memetics.get(n, False) and l == level)
        
        if not selected_memetics[name]:
            # Trying to select - check limit based on level range
            if level in ["20-35"]:
                max_selections = 4
            else:
                max_selections = 3
                
            if level_selected >= max_selections:
                messagebox.showwarning("Selection Limit", 
                                      f"You can only select {max_selections} memetics from level {level}!")
                return
            selected_memetics[name] = True
        else:
            # Deselecting - always allowed
            selected_memetics[name] = False
        
        # Update card appearance
        if selected_memetics[name]:
            card.config(bg="#E8F5E9", highlightbackground="#4CAF50")
            img_label.config(bg="#E8F5E9")
            name_label.config(bg="#E8F5E9")
            info_frame.config(bg="#E8F5E9")
            for child in info_frame.winfo_children():
                child.config(bg="#E8F5E9")
        else:
            card.config(bg="#F5F5F5", highlightbackground="#CCCCCC")
            img_label.config(bg="#F5F5F5")
            name_label.config(bg="#F5F5F5")
            info_frame.config(bg="#F5F5F5")
            for child in info_frame.winfo_children():
                child.config(bg="#F5F5F5")
        
        # Automatically detect and update character display
        detect_and_update_character_display()
    
    # Bind click events to all widgets in the card
    card.bind("<Button-1>", toggle_selection)
    img_label.bind("<Button-1>", toggle_selection)
    name_label.bind("<Button-1>", toggle_selection)
    info_frame.bind("<Button-1>", toggle_selection)
    for child in info_frame.winfo_children():
        child.bind("<Button-1>", toggle_selection)
    
    # Change cursor on hover
    card.config(cursor="hand2")
    
    return card

def show_memetic_details(name, level, category):
    """Show details popup for memetic specialization"""
    details_window = tk.Toplevel(window)
    details_window.title(f"{name}")
    details_window.geometry("400x300")
    details_window.resizable(False, False)
    
    # Add icon
    if app_icon:
        details_window.iconphoto(False, app_icon)
    
    # Content
    tk.Label(details_window, text=name, font=("Inter Bold", 16), wraplength=350).pack(pady=20)
    tk.Label(details_window, text=f"Level: {level}", font=("Inter", 12)).pack(pady=5)
    tk.Label(details_window, text=f"Category: {category}", font=("Inter", 12)).pack(pady=5)
    
    # Close button
    tk.Button(details_window, text="Close", command=details_window.destroy,
              bg="#4069D5", fg="#FFFFFF", font=("Inter", 12),
              borderwidth=0, relief="flat", cursor="hand2").pack(pady=20)

# Complete memetic specializations data
# Format: (name, level, category, server)
# server: "All" = show on both servers, "Edream" = Edream only, "Manibus" = Manibus only
memetic_data = [
    # Level 5-15 (Gathering)
    ("Furnace: Precision Refining", "5-15", "Gathering", "All"),
    ("Load Handling", "5-15", "Gathering", "All"),
    ("Pickaxe: Moonlight Mining", "5-15", "Gathering", "All"),
    ("Pickaxe: Forest Foe", "5-15", "Gathering", "All"),
    ("Disassembly Bench: Careful Disassembly", "5-15", "Gathering", "All"),
    ("Super Refinery", "5-15", "Gathering", "All"),
    
    # Level 5-15 (Building)
    ("Flamethrower Trap: Scorching Blast", "5-15", "Building", "All"),
    ("Robotics Facility: Skilled Mechanician", "5-15", "Building", "All"),
    ("Wood Structures: Tough Plant", "5-15", "Building", "All"),
    ("Bed: A Place to Call Home", "5-15", "Building", "All"),
    ("Deluxe Storage Crate", "5-15", "Building", "All"),
    ("Basic Defense: Battle-Hardened", "5-15", "Building", "All"),
    
    # Level 5-15 (Crafting)
    ("Gear Workbench: Customization", "5-15", "Crafting", "All"),
    ("Explosive On-the-Go", "5-15", "Crafting", "All"),
    ("Electronics Grabber", "5-15", "Crafting", "All"),
    ("Disassembly Bench: Electronic Recycling", "5-15", "Crafting", "All"),
    ("Throwing Dagger: Bullseye", "5-15", "Crafting", "All"),
    ("Jump Booster", "5-15", "Crafting", "All"),
    ("Explosive Sack", "5-15", "Crafting", "All"),
    ("Backpack Expansion", "5-15", "Crafting", "All"),
    ("Supplies Workbench: Ammo Factory", "5-15", "Crafting", "All"),
    
    # Level 5-15 (Management)
    ("Chef's Knife", "5-15", "Management", "All"),
    ("Portable Diving Gear", "5-15", "Management", "All"),
    ("Roasted & Dried: Low and Slow", "5-15", "Management", "All"),
    ("Stove: Long-Term Storage", "5-15", "Management", "All"),
    ("Portable Rainwater Collection System", "5-15", "Management", "All"),
    ("Gardening Gloves", "5-15", "Management", "All"),
    ("Harvesting Sickle", "5-15", "Management", "All"),
    ("Compost Bin", "5-15", "Management", "All"),
    ("Activated Carbon Filter", "5-15", "Management", "All"),
    
    # Level 20-35 (Gathering)
    ("Chainsaw: Chainsaw Horror Show", "20-35", "Gathering", "All"),
    ("Electric Drill: Treasure Hunter", "20-35", "Gathering", "All"),
    ("Electric Furnace: Efficiency Lover", "20-35", "Gathering", "All"),
    ("Oil Processing", "20-35", "Gathering", "All"),
    ("Precious Metal Refining", "20-35", "Gathering", "All"),
    ("Solar Drill", "20-35", "Gathering", "All"),
    
    # Level 20-35 (Building)
    ("Furnace: Sintering", "20-35", "Building", "All"),
    ("Updraft Device: Gravity Lite", "20-35", "Building", "All"),
    ("Stone Structures: Intense Defense", "20-35", "Building", "All"),
    ("Shotgun Turret: Volley Fire", "20-35", "Building", "All"),
    ("Biomass Missile: Ample Munition", "20-35", "Building", "All"),
    ("Gravitational Grip: Bonds of Guidance", "20-35", "Building", "All"),
    
    # Level 20-35 (Crafting)
    ("Claymore Mine: Warrior's Resolve", "20-35", "Crafting", "All"),
    ("Adrenaline Shot: Phoenix", "20-35", "Crafting", "All"),
    ("Explosive Throwables: Echo Blast", "20-35", "Crafting", "All"),
    ("Synthesis Bench: Recycle & Reuse", "20-35", "Crafting", "All"),
    ("Sulfur Chemist", "20-35", "Crafting", "All"),
    ("Supplies Workbench: Healing Boost", "20-35", "Crafting", "All"),
    ("Portable Updraft Device", "20-35", "Crafting", "All"),
    ("Combo Chipset", "20-35", "Crafting", "All"),
    ("Portable MG Turret: Barrage of Bullets", "20-35", "Crafting", "All"),
    
    # Level 20-35 (Management)
    ("Portable Fridge", "20-35", "Management", "All"),
    ("Improved Compound Fertilizer", "20-35", "Management", "All"),
    ("Biomass Generator: Sustained Output", "20-35", "Management", "All"),
    ("Generator: Electrical Expert", "20-35", "Management", "All"),
    ("Canned Goods: Mini Canner", "20-35", "Management", "All"),
    ("Solar Generator: Photon Power", "20-35", "Management", "All"),
    ("Stardust Water Pump", "20-35", "Management", "All"),
    ("Iced Treat: Brain Freeze", "20-35", "Management", "All"),
    
    # Level 40-50 (Gathering)
    ("Electric Furnace: Electrolysis", "40-50", "Gathering", "All"),
    ("Art of Stardust Decay", "40-50", "Gathering", "All"),
    ("Crystal Transformation", "40-50", "Gathering", "All"),
    ("Gold Pickaxe and Silver Pickaxe", "40-50", "Gathering", "All"),
    ("Lucky Logging Platform", "40-50", "Gathering", "All"),
    ("Stardust Mining Platform", "40-50", "Gathering", "All"),
    
    # Level 40-50 (Building)
    ("Reinforced Structures: Healing Defense", "40-50", "Building", "All"),
    ("Red Plasma Rounds", "40-50", "Building", "All"),
    ("Gatling Cannon: Power Blast", "40-50", "Building", "All"),
    ("Rifle Turret: Two Birds One Stone", "40-50", "Building", "All"),
    
    # Level 40-50 (Crafting)
    ("High Power Warhead", "40-50", "Crafting", "All"),
    ("Ultra Grenade", "40-50", "Crafting", "All"),
    ("Supplies Workbench: Anti-Armor", "40-50", "Crafting", "All"),
    ("Stardust Barrier: Hold the Line", "40-50", "Crafting", "All"),
    ("Rare Crystal Set", "40-50", "Crafting", "All"),
    ("Stardust Regulator", "40-50", "Crafting", "All"),
    ("Golden Knife", "40-50", "Crafting", "All"),
    ("Spectral Cloak", "40-50", "Crafting", "All"),
    ("Scout Drone: Invisible Hunter", "40-50", "Crafting", "All"),
    
    # Level 40-50 (Management)
    ("Kitchen Set: Gourmand", "40-50", "Management", "All"),
    ("Stardust Dish: Shell Break", "40-50", "Management", "All"),
    ("Nalcott Easter Egg", "40-50", "Management", "All"),
    ("Hydraulic Generator: One with the Tides", "40-50", "Management", "All"),
    ("Deviant Power Generator: Stardust Unleashed", "40-50", "Management", "All"),
    ("Pulse Power Device", "40-50", "Management", "All"),
    
    # ===== EDREAM-ONLY CARDS =====
    
    # Level 5-15 Edream Only
    ("Furnace: Large Furnace", "5-15", "Gathering", "Edream"),
    ("Supplies Workbench: Forest Hunter", "5-15", "Crafting", "Edream"),
    ("Snowmobile", "5-15", "Crafting", "Edream"),
    ("Blade Fan", "5-15", "Crafting", "Edream"),
    ("Spicy Pepper", "5-15", "Management", "Edream"),
    
    # Level 20-35 Edream Only
    ("Gunpowder Extraction", "20-35", "Gathering", "Edream"),
    ("Molecular Structure Research", "20-35", "Gathering", "Edream"),
    ("Furnace: Chaosium Material Analysis", "20-35", "Gathering", "Edream"),
    ("Scout Drone: Freezing Drone", "20-35", "Crafting", "Edream"),
    ("Frost Armor", "20-35", "Crafting", "Edream"),
    ("Grenade: Line Charge", "20-35", "Crafting", "Edream"),
    ("Ice Throwing Dagger and Flame Throwing Dagger", "20-35", "Crafting", "Edream"),
    ("Portable Thermostat", "20-35", "Crafting", "Edream"),
    ("Claymore Mine: Frost Trap", "20-35", "Crafting", "Edream"),
    ("Portable Gun Turret: Explosive Automatic Ammo", "20-35", "Crafting", "Edream"),
    ("Bed: Heat Preservation", "20-35", "Building", "Edream"),
    ("Dummy: Fear and Terror", "20-35", "Building", "Edream"),
    ("Generator: Heat Dissipation", "20-35", "Management", "Edream"),
    ("Refining Facility: Smelting", "20-35", "Management", "Edream"),
    ("Water Pump: Underground Pump", "20-35", "Management", "Edream"),
    ("Biomass Generator: Heat Generator", "20-35", "Management", "Edream"),
    ("Planter Box: Greenhouse Planting", "20-35", "Management", "Edream"),
    ("Grilled Dish: Grilling Master", "20-35", "Management", "Edream"),
    
    # Level 40-50 Edream Only
    ("Metal Dissolution", "40-50", "Gathering", "Edream"),
    ("Grenade: Cluster Grenade", "40-50", "Crafting", "Edream"),
    ("Composite Crystal", "40-50", "Crafting", "Edream"),
    ("Frag Grenade: Viscoelastic Cold Fire", "40-50", "Crafting", "Edream"),
    ("Silentfire Shield", "40-50", "Crafting", "Edream"),
    ("Flamethrower Trap: Kebob Party", "40-50", "Building", "Edream"),
    ("Building Master", "40-50", "Building", "Edream"),
    ("Deviant Power Generator: Energy Extraction", "40-50", "Management", "Edream"),
    ("Fish Pheromones", "40-50", "Management", "Edream"),
]

# Configure grid weights for 6 columns
for i in range(6):
    cards_frame.columnconfigure(i, weight=1, minsize=200)

# Function to populate cards initially
def populate_initial_cards():
    """Populate initial cards after window is shown"""
    current_server = server_var.get()
    visible_idx = 0
    for name, level, category, server in memetic_data:
        # Show card if it's for "All" servers or matches current server
        if server == "All" or server == current_server:
            row = visible_idx // 6
            col = visible_idx % 6
            create_memetic_card(cards_frame, name, level, category, row, col)
            visible_idx += 1
    
    # Update scroll region after all cards are created
    window.update_idletasks()
    scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

# Initialize character system (after memetic_data is defined)
update_character_list()
load_character_choices()

# Populate initial cards before showing window
populate_initial_cards()

# Add back button to return to Frame 1
back_button = Button(
    frame2, text="← Back", 
    command=show_frame1,
    bg="#2C2C2C", fg="#FFFFFF",
    font=("Inter Bold", 16),
    borderwidth=2,
    relief="flat",
    cursor="hand2",
    activebackground="#404040",
    activeforeground="#FFFFFF",
    highlightthickness=0,
    padx=20,
    pady=10
)
back_button.place(x=40, y=40, width=180, height=50)

# Add hover effect for back button
def on_enter_back(e):
    back_button['bg'] = '#404040'
    back_button['font'] = ('Inter Bold', 17)

def on_leave_back(e):
    back_button['bg'] = '#2C2C2C'
    back_button['font'] = ('Inter Bold', 16)

back_button.bind("<Enter>", on_enter_back)
back_button.bind("<Leave>", on_leave_back)

window.resizable(False, False)

# Preload first batch of images in background for faster initial display
def preload_images():
    """Preload first 30 images in background"""
    current_server = server_var.get()
    count = 0
    for name, level, cat, srv in memetic_data:
        if srv == "All" or srv == current_server:
            if name not in memetic_images:
                load_memetic_image(name)
                count += 1
                if count >= 30:  # Preload first 30 cards
                    break

# Preload images before showing window
preload_images()

# Force update to ensure everything is drawn
window.update_idletasks()

# Show window after everything is loaded
window.deiconify()
window.mainloop()
