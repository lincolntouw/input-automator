"""
===========================================================
Lincoln's Input Automation Tools
===========================================================

AUTHOR      Lincoln Touw (github.com/lincolntouw)         
CREATED     08/31/2025       

Input automator made with Python (UI made with Python's 
tkinter library) Supports auto-clicking / auto-key-pressing
as well as runnable CSV-formatted programs.                      

===========================================================
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import pyautogui
import keyboard

# ================== Globals ==================

clicking = False
click_thread = None
current_hotkey = "F4"       # default toggle hotkey
current_mode = "AutoClick"  # default mode (AutoClick/AutoKeyPress)           
root = None
hotkey = None
CUSTOM_FONT = ("Arial", 10)   

# ================== Statistics ==================

# variables
initial_stats = {
    "Clicks": 0,
    "Keys Pressed": 0,
    "Elapsed Time": 0.0,
}
stats = dict(initial_stats)
stat_labels = {}
start_time = 0

# functions     
def reset_all_stats():
    for name, value in initial_stats.items():
        stats[name] = value
        stat_labels[name].config(text=f"{name}: {value}")

def update_stat(name, value):
    stats[name] = value
    text_value = f"{value:.2f}" if isinstance(value, float) else value
    stat_labels[name].config(text=f"{name}: {text_value}")
 
def increment_stat(name, value=1):
    update_stat(name, stats[name] + value)
    
# ================== Actions ==================
def start_action(ui):
    global clicking, click_thread, start_time 
    if clicking: return

    clicking = True
    ui["start_button"].config(state="disabled")
    ui["stop_button"].config(state="normal")
    start_time = time.time()
    if ui["reset_stats"].get(): reset_all_stats()

    def update_time():
        elapsed = time.time() - start_time
        update_stat("Elapsed Time", elapsed)
        if clicking: root.after(50, update_time)
    update_time()

    def action_loop():
        interval = float(ui["interval_entry"].get())
        max_iterations = int(ui["max_iterations_entry"].get())

        stat_name = "Clicks" if current_mode == "AutoClick" else "Keys Pressed"
        start_value = stats[stat_name]

        if current_mode == "AutoClick":
            button = ui["button_choice"].get()
            location_mode = ui["click_mode_choice"].get()

            while clicking:
                if location_mode == "cursor position":
                    pyautogui.click(button=button)
                elif location_mode == "fixed position":
                    pyautogui.click(
                        button=button,
                        x=int(ui["click_x"].get()),
                        y=int(ui["click_y"].get())
                    )

                increment_stat("Clicks")     
                if max_iterations and stats["Clicks"] - start_value >= max_iterations:
                    stop_action(ui)

                time.sleep(interval)
        elif current_mode == "AutoKeyPress":    
            modifiers = []
            if ui["shift_modifier"].get(): modifiers.append("shift")
            if ui["control_modifier"].get(): modifiers.append("ctrl")
            if ui["alt_modifier"].get(): modifiers.append("alt")
            key = ui["key_entry"].get().strip()
            if key: modifiers.append(key)
            keys = "+".join(modifiers)

            while clicking:
                keyboard.press_and_release(keys)
                
                increment_stat("Keys Pressed")
                if max_iterations and stats["Keys Pressed"] - start_value >= max_iterations:
                    stop_action(ui)

                time.sleep(interval)

    click_thread = threading.Thread(target=action_loop, daemon=True)
    click_thread.start()

def stop_action(ui):
    global clicking
    clicking = False
    ui["start_button"].config(state="normal")
    ui["stop_button"].config(state="disabled")


# ================== Hotkey ==================     
def setup_hotkey(ui):
    global hotkey

    def toggle():
        if clicking: stop_action(ui) 
        else: start_action(ui)

    if hotkey:
        keyboard.remove_hotkey(hotkey)
    hotkey = keyboard.add_hotkey(current_hotkey, toggle)
    ui["hotkey_label"].config(text=f"Toggle Hotkey: {current_hotkey}")      

def change_hotkey(ui):
    global current_hotkey
    new_key = ui["hotkey_entry"].get().strip()
    if new_key:
        current_hotkey = new_key
        setup_hotkey(ui)

# ================== Position Selector ==================
def pick_click_position(ui):
    from pynput import mouse

    picker = tk.Toplevel()
    picker.overrideredirect(True)
    picker.attributes("-topmost", True)
    picker.geometry("+100+100")

    label = tk.Label(picker, text="Left-click to pick, press Esc to cancel", padx=10, pady=5, font=CUSTOM_FONT, bg="white")     
    label.pack()

    def update_position():
        x, y = pyautogui.position()
        picker.geometry(f"+{x+15}+{y+15}")
        label.config(text=f"Left-click to pick, press Esc to cancel\n(X: {x}, Y: {y})")
        if picker.winfo_exists():
            picker.after(30, update_position)

    def on_click(x, y, button, pressed):
        if pressed:
            ui["click_x"].delete(0, tk.END)
            ui["click_x"].insert(0, str(x))

            ui["click_y"].delete(0, tk.END)
            ui["click_y"].insert(0, str(y))
            stop()

    def cancel_pick(): stop()
    def stop():
        try: listener.stop()
        except: pass
        keyboard.remove_hotkey("esc")
        if picker.winfo_exists():
            picker.destroy()

    listener = mouse.Listener(on_click=on_click)
    listener.start()
    keyboard.add_hotkey("esc", cancel_pick)

    update_position()
    picker.mainloop()

# ================== Main Interface ==================      
def main():
    global root, current_mode

    root = tk.Tk()       
    root.title("Input Automator")
    root.geometry("430x730")
    root.resizable(False, False)

    ui = {}
    
    # Mode selection tabs        
    notebook = ttk.Notebook(root)
    notebook.pack(padx=10, pady=10, fill="x")

    # ------------------ AutoClick Tab ------------------
    click_tab = tk.Frame(notebook)
    notebook.add(click_tab, text="AutoClicker")

    tk.Label(click_tab, text="Mouse Button:", font=CUSTOM_FONT).grid(row=0, column=0, sticky="w", padx=10, pady=10)
    ui["button_choice"] = tk.StringVar(value="left")
    tk.OptionMenu(click_tab, ui["button_choice"], "left", "right", "middle").grid(row=0, column=1, sticky="w")

    ui["click_mode_choice"] = tk.StringVar(value="cursor position")

    # Click at cursor pos  
    cursor_pos_menu = tk.Frame(click_tab)
    cursor_pos_menu.grid(row=1, column=0, columnspan=2, sticky="w")
    tk.Radiobutton(cursor_pos_menu, variable=ui["click_mode_choice"], value="cursor position", font=CUSTOM_FONT).grid(row=1, column=0, sticky='w')
    tk.Label(cursor_pos_menu, text="Click at cursor position", font=CUSTOM_FONT).grid(row=1, column=1, sticky='w')

    # Click at fixed pos
    fixed_pos_menu = tk.Frame(click_tab)
    fixed_pos_menu.grid(row=2, column=0, columnspan=2, sticky="w")
    tk.Radiobutton(fixed_pos_menu, variable=ui["click_mode_choice"], value="fixed position", font=CUSTOM_FONT).grid(row=2, column=0, sticky='w')
    tk.Label(fixed_pos_menu, text="Click at", font=CUSTOM_FONT).grid(row=2, column=1, sticky="w")

    pos_frame = tk.Frame(click_tab)
    pos_frame.grid(row=2, column=1, columnspan=1, sticky="w")
    ui["choose_click_position"] = tk.Button(pos_frame, text="Pick Location", font=CUSTOM_FONT, command=lambda: pick_click_position(ui))
    ui['choose_click_position'].grid(row=0, column=0, sticky="w", padx=10, pady=10)
    tk.Label(pos_frame, text="X:", font=CUSTOM_FONT).grid(row=0, column=1, sticky="w")
    ui["click_x"] = tk.Entry(pos_frame, width=6, font=CUSTOM_FONT)
    ui["click_x"].insert(0, "0")
    ui["click_x"].grid(row=0, column=2, sticky="w")
    tk.Label(pos_frame, text="Y:", font=CUSTOM_FONT).grid(row=0, column=3, sticky="w")
    ui["click_y"] = tk.Entry(pos_frame, width=6, font=CUSTOM_FONT)
    ui["click_y"].insert(0, "0")
    ui["click_y"].grid(row=0, column=4, sticky="w")

    # Array (todo: make pattern editor for simpler ceration)               
    array_pos_menu = tk.Frame(click_tab)
    array_pos_menu.grid(row=3, column=0, columnspan=2, sticky="w")
    tk.Radiobutton(array_pos_menu, variable=ui["click_mode_choice"], value="array", font=CUSTOM_FONT).grid(row=2, column=0, sticky='w')
    tk.Label(array_pos_menu, text="Click pattern", font=CUSTOM_FONT).grid(row=2, column=1, sticky="w")
    tk.Button(array_pos_menu, text="Import CSV", font=CUSTOM_FONT).grid(row=2, column=2, sticky='w', padx=10)
    open_pattern_editor = tk.Button(array_pos_menu, text="Create", font=CUSTOM_FONT)
    open_pattern_editor.grid(row=2, column=3, sticky='w', padx=10)
    open_pattern_editor.config(state='disabled')

    # ------------------ AutoKeyPress Tab ------------------            
    key_tab = tk.Frame(notebook, padx=10, pady=10)
    notebook.add(key_tab, text="AutoKeyPresser")

    # Key selection
    tk.Label(key_tab, text="Key to press:", font=CUSTOM_FONT).grid(row=0, column=0, sticky="w")
    ui["key_entry"] = tk.Entry(key_tab, width=10, font=CUSTOM_FONT)
    ui["key_entry"].insert(0, "a")
    ui["key_entry"].grid(row=0, column=1, sticky="w")

    # Modifier key boxes
    tk.Label(key_tab, text="Modifier Keys:", font=CUSTOM_FONT).grid(row=1, column=0, sticky="w")
    tk.Label(key_tab, text="Shift:", font=CUSTOM_FONT).grid(row=2, column=0, sticky="w")
    ui["shift_modifier"] = tk.BooleanVar(value=False)
    tk.Checkbutton(key_tab, variable=ui['shift_modifier'], font=CUSTOM_FONT).grid(row=2, column=1, padx=5, sticky="w")

    tk.Label(key_tab, text="Control:", font=CUSTOM_FONT).grid(row=3, column=0, sticky="w")
    ui["control_modifier"] = tk.BooleanVar(value=False)
    tk.Checkbutton(key_tab, variable=ui['control_modifier'], font=CUSTOM_FONT).grid(row=3, column=1, padx=5, sticky="w")

    tk.Label(key_tab, text="Alt:", font=CUSTOM_FONT).grid(row=4, column=0, sticky="w")
    ui["alt_modifier"] = tk.BooleanVar(value=False)
    tk.Checkbutton(key_tab, variable=ui['alt_modifier'], font=CUSTOM_FONT).grid(row=4, column=1, padx=5, sticky="w")

    def on_tab_change(event):
        global current_mode
        tab_index = notebook.index(notebook.select())
        current_mode = "AutoClick" if tab_index == 0 else "AutoKeyPress"  
    notebook.bind("<<NotebookTabChanged>>", on_tab_change)

    # ------------------ Shared Settings ------------------
    shared_frame = tk.LabelFrame(root, text="Settings", padx=10, pady=10, font=CUSTOM_FONT)
    shared_frame.pack(padx=10, pady=5, fill="x")

    general_frame = tk.Frame(shared_frame)
    general_frame.grid(row=0, column=0, sticky="w")

    # Input interval
    tk.Label(general_frame, text="Interval (seconds):", font=CUSTOM_FONT).grid(row=0, column=0, sticky="w")
    ui["interval_entry"] = tk.Entry(general_frame, width=10, font=CUSTOM_FONT)
    ui["interval_entry"].insert(0, "0.5")
    ui["interval_entry"].grid(row=0, column=1, padx=5, sticky="w")

    # Reset statistics on start
    tk.Label(general_frame, text="Reset stats on start:", font=CUSTOM_FONT).grid(row=3, column=0, sticky="w")
    ui["reset_stats"] = tk.BooleanVar(value=True)
    tk.Checkbutton(general_frame, variable=ui["reset_stats"], font=CUSTOM_FONT).grid(row=3, column=1, sticky="w")

    # Stop mode     
    stop_mode = tk.Frame(shared_frame, padx=10, pady=10)
    stop_mode.grid(row=1, column=0, sticky="w")
    ui['stop_after_mode'] = tk.StringVar(value="until stopped")
    tk.Radiobutton(stop_mode, text="Stop after:", value="after x", variable=ui['stop_after_mode'], font=CUSTOM_FONT).grid(row=1, column=0, sticky="w")
    ui["max_iterations_entry"] = tk.Entry(stop_mode, width=10, font=CUSTOM_FONT)
    ui["max_iterations_entry"].insert(0, "0")
    ui["max_iterations_entry"].grid(row=1, column=1, padx=5, sticky="w")
    tk.Label(stop_mode, text="inputs", font=CUSTOM_FONT).grid(row=1, column=2, sticky="w")
    tk.Radiobutton(stop_mode, text="Repeat until stopped", value="until stopped", variable=ui['stop_after_mode'], font=CUSTOM_FONT).grid(row=2, column=0)

    # ------------------ Control Buttons ------------------     
    control_frame = tk.LabelFrame(root, text="Controls", padx=10, pady=10, font=CUSTOM_FONT)
    control_frame.pack(padx=10, pady=5, fill="x")
    ui["start_button"] = tk.Button(control_frame, text="Start", width=12, font=CUSTOM_FONT, command=lambda:start_action(ui))
    ui["start_button"].grid(row=0, column=0, padx=5)
    ui["stop_button"] = tk.Button(control_frame, text="Stop", width=12, font=CUSTOM_FONT, state="disabled", command=lambda:stop_action(ui))
    ui["stop_button"].grid(row=0, column=1, padx=5)

    # ------------------ Hotkey Settings ------------------
    hotkey_frame = tk.LabelFrame(root, text="Hotkey Settings", padx=10, pady=10, font=CUSTOM_FONT)
    hotkey_frame.pack(padx=10, pady=5, fill="x")
    tk.Label(hotkey_frame, text="(i) Pressing the selected hotkey will toggle automation", fg="gray", font=CUSTOM_FONT).grid(row=0, column=0, columnspan=2, pady=5, sticky="w")
    ui["hotkey_label"] = tk.Label(hotkey_frame, text=f"Hotkey: {current_hotkey}", font=CUSTOM_FONT)
    ui["hotkey_label"].grid(row=1, column=0, columnspan=2, pady=5, sticky="w")

    # Hotkey changer
    tk.Label(hotkey_frame, text="Set new hotkey:", font=CUSTOM_FONT).grid(row=2, column=0, sticky="w")
    ui["hotkey_entry"] = tk.Entry(hotkey_frame, width=10, font=CUSTOM_FONT)
    ui["hotkey_entry"].grid(row=2, column=1, padx=5, sticky="w")
    tk.Button(hotkey_frame, text="Change", font=CUSTOM_FONT, command=lambda:change_hotkey(ui)).grid(row=2, column=2, columnspan=2, pady=5)
    ui["hotkey_entry"].insert(0, current_hotkey)

    # ------------------ Statistics ------------------      
    stats_frame = tk.LabelFrame(root, text="Statistics", padx=10, pady=10, font=CUSTOM_FONT)
    stats_frame.pack(padx=10, pady=5, fill="x")

    stats_container = tk.LabelFrame(root, text="Statistics", padx=10, pady=10)
    stats_frame.pack(padx=10, pady=5, fill="x")

    stats_container = tk.Frame(stats_frame)                             
    stats_container.grid(row=0, column=0)               
    for name in stats:
        lbl = tk.Label(stats_container, text=f"{name}: {stats[name]}")
        lbl.grid(sticky="w")
        stat_labels[name] = lbl
        
    # Export options    
    def export_json():
        import json
        from tkinter import filedialog 
        file_path = filedialog.asksaveasfilename( defaultextension=".json", filetypes=[("JSON file", "*.json"), ("All files", "*.*")] )
        if file_path:       
            with open(file_path, "w") as file:
                json.dump(stats, file, indent=4) 
    def export_csv():       
        csv = 'statistic,value'                 
        for name in stats:
            csv += f"\n{name},{str(stats[name])}"         
        from tkinter import filedialog 
        file_path = filedialog.asksaveasfilename( defaultextension=".csv", filetypes=[("CSV file", "*.csv"), ("All files", "*.*")] )       
        if file_path:           
            with open(file_path, "w") as file:
                file.write(csv) 

    save_json_button = tk.Button(stats_frame, text="Export JSON",  command=export_json)
    save_json_button.grid(sticky="w", column=0, row=2)      
    save_csv_button = tk.Button(stats_frame, text="Export CSV", command=export_csv)
    save_csv_button.grid(sticky="w", column=1, row=2)      

    # ------------------ Setup Hotkeys ------------------
    setup_hotkey(ui)

    # ------------------ :) ------------------
    root.mainloop()


if __name__ == "__main__":
    main()

