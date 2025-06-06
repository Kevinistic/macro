import pyautogui
from tkinter import *
from tkinter import ttk, messagebox
import time
import threading
import os
from pynput.keyboard import Controller, Listener, Key

class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("Macro Interface")
        self.geometry("640x600")  # size in px
        self.resizable(False, False)  # nuh uh
        self.attributes("-topmost", True)  # always on top
        self.rowconfigure(0, weight=1)  # snap to geometry()
        self.columnconfigure(0, weight=1)

        FrameMain(self)
    
    def run(self):  # call to run
        self.mainloop()

class FrameMain(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.spamming = False
        self.keyboard_controller = Controller()
        self.toggle_key = "F6"  # Key to toggle spamming

        # Start spam loop thread
        threading.Thread(target=self.spam_loop, daemon=True).start()

        # Start global key listener thread
        threading.Thread(target=self.start_global_key_listener, daemon=True).start()


        self.labels = []
        self.macro_list = []

        self.grid(column=0,row=0,sticky='NSEW')

        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.intro = Label(self, text="Your Macros:")
        self.intro.grid(column=0,row=0,sticky='W')

        self.tableFrame = Frame(self)
        self.tableFrame.grid(column=0,row=1,sticky='W')

        self.categoriesNumber = Label(self.tableFrame, text='No.')
        self.categoriesAction = Label(self.tableFrame, text='Action')
        self.categoriesDescription = Label(self.tableFrame, text='Description')
        self.categoriesNumber.grid(column=0,row=0,sticky='W')
        self.categoriesAction.grid(column=1,row=0,sticky='W')
        self.categoriesDescription.grid(column=2,row=0,sticky='W')

        self.macroControlFrame = Frame(self)
        self.macroControlFrame.grid(column=0, row=2, sticky='NW')

        self.addNew = ttk.Button(self.macroControlFrame, text='Add New', width=10, command=self.add_macro)
        self.addNew.grid(column=0, row=0, sticky='W', padx=(0, 5))

        self.deleteLast = ttk.Button(self.macroControlFrame, text='Delete Last', width=12, command=self.delete_last_macro)
        self.deleteLast.grid(column=1, row=0, sticky='W')

        self.buttonFrame = Frame(self)
        self.buttonFrame.grid(column=0,row=3,sticky='SW')

        self.updateButton = ttk.Button(self.buttonFrame,text='Update',width=10)
        self.settingsButton = ttk.Button(self.buttonFrame,text='Settings',width=10,command=self.change_toggle_key)
        self.aboutButton = ttk.Button(self.buttonFrame,text='About',width=10)
        self.updateButton.grid(column=0,row=0,sticky='W')
        self.settingsButton.grid(column=1,row=0,sticky='W')
        self.aboutButton.grid(column=2,row=0,sticky='W')
    
    def add_macro(self):
        # Create a non-blocking popup
        top = Toplevel(self)
        top.title("Key Capture")
        top.geometry("300x150")  
        top.attributes('-topmost', True)  # keep on top
        top.grab_set()  # focus

        Label(top, text="Please press a key to assign to this macro.", wraplength=280, justify="center").pack(pady=10)

        listener_holder = {}

        def on_press(key):
            try:
                key_str = key.char  # character keys
            except AttributeError:
                key_str = key.name  # special keys

            key_str = key_str.upper()  # normalize to uppercase
            description = f"Pressed key: {key_str}"
            self.macro_list.append((key_str, description))

            self.refresh_macro_table()

            if 'listener' in listener_holder:
                listener_holder['listener'].stop()
                top.destroy()

        def cancel_macro():
            if 'listener' in listener_holder:
                listener_holder['listener'].stop()
            top.destroy()

        # Handle manual window close (via the X button)
        top.protocol("WM_DELETE_WINDOW", cancel_macro)

        # Add Cancel button
        cancel_btn = ttk.Button(top, text="Cancel", command=cancel_macro)
        cancel_btn.pack(pady=10)

        listener = Listener(on_press=on_press)
        listener_holder['listener'] = listener
        listener.start()

    def refresh_macro_table(self):
        # Remove existing rows
        for widget in self.tableFrame.winfo_children():
            info = widget.grid_info()
            if int(info['row']) > 0:  # skip header row
                widget.destroy()

        # Re-add header
        self.categoriesNumber = Label(self.tableFrame, text='No.')
        self.categoriesAction = Label(self.tableFrame, text='Action')
        self.categoriesDescription = Label(self.tableFrame, text='Description')
        self.categoriesNumber.grid(column=0, row=0, sticky='W')
        self.categoriesAction.grid(column=1, row=0, sticky='W')
        self.categoriesDescription.grid(column=2, row=0, sticky='W')

        # Add all macros
        for i, (action, desc) in enumerate(self.macro_list, start=1):
            Label(self.tableFrame, text=str(i)).grid(column=0, row=i, sticky='W')
            Label(self.tableFrame, text=action).grid(column=1, row=i, sticky='W')
            Label(self.tableFrame, text=desc).grid(column=2, row=i, sticky='W')

    def delete_last_macro(self):
        if self.macro_list:
            self.macro_list.pop()
            self.refresh_macro_table()
        else:
            messagebox.showinfo("Info", "No macros to delete.")

    def spam_loop(self):
        while True:
            if self.spamming and self.macro_list:
                for key, _ in self.macro_list:
                    self.keyboard_controller.press(key)
                    self.keyboard_controller.release(key)
                    time.sleep(0.01)
            else:
                time.sleep(0.01)

    def start_global_key_listener(self):
        def on_press(key):
            try:
                key_str = key.char.upper() if hasattr(key, 'char') and key.char else key.name.upper()
                if key_str == self.toggle_key:
                    self.spamming = not self.spamming
                    print(f"Spamming {'enabled' if self.spamming else 'disabled'}")
            except Exception as e:
                print(f"Listener error: {e}")
        Listener(on_press=on_press).run()  # runs in thread

    def change_toggle_key(self):
        top = Toplevel(self)
        top.title("Change Toggle Key")
        top.geometry("300x150")
        top.attributes('-topmost', True)
        top.grab_set()

        Label(top, text=f"Press a new key to toggle spam (current: {self.toggle_key}).", wraplength=280, justify="center").pack(pady=10)

        listener_holder = {}

        def on_press(key):
            try:
                key_str = key.char.upper()
            except AttributeError:
                key_str = key.name.upper()

            self.toggle_key = key_str
            messagebox.showinfo("Key Changed", f"New toggle key is set to: {self.toggle_key}")
            print(f"Toggle key changed to: {self.toggle_key}")

            if 'listener' in listener_holder:
                listener_holder['listener'].stop()
                top.destroy()

        def cancel():
            if 'listener' in listener_holder:
                listener_holder['listener'].stop()
            top.destroy()

        top.protocol("WM_DELETE_WINDOW", cancel)
        cancel_btn = ttk.Button(top, text="Cancel", command=cancel)
        cancel_btn.pack(pady=10)

        listener = Listener(on_press=on_press)
        listener_holder['listener'] = listener
        listener.start()

if __name__ == "__main__":
    app = App()
    app.run()  # Start the application