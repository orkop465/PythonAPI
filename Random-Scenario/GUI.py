import os
import shutil
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import Randomizer

# TODO: exception handling for running gui without lgsvl running
root = tk.Tk()
root.title("LGSVL PythonAPI")
root.resizable(width=False, height=False)
root.geometry('700x350')
program_directory = sys.path[0]
root.iconphoto(True, tk.PhotoImage(file=os.path.join(program_directory, "yoinkPY.png")))
saved_file_root = ''
loaded_file_root = ''

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TAB SETUP
tabControl = ttk.Notebook(root)
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text="Run")

tab2 = ttk.Frame(tabControl)
tabControl.add(tab2, text="Replay")

tab3 = ttk.Frame(tabControl)
tabControl.add(tab3, text="Output")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# These functions are mostly helper functions, which are called by various buttons and entry boxes

# validate only ints are entered in entry box, negatives not allowed
# noinspection PyUnusedLocal
def validate_int(action, index, value_if_allowed,
                 prior_value, text, validation_type, trigger_type, widget_name):
    # action=1 -> insert
    if action == '1':
        if text in '0123456789':
            try:
                int(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False
    else:
        return True


# validate only numbers are entered in entry box, negatives not allowed
# noinspection PyUnusedLocal
def validate_float(action, index, value_if_allowed,
                   prior_value, text, validation_type, trigger_type, widget_name):
    # action=1 -> insert
    if action == '1':
        if text in '0123456789.':
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False
    else:
        return True


# validate only numbers are entered in entry box, negatives allowed
# noinspection PyUnusedLocal
def validate_int_negatives(action, index, value_if_allowed,
                           prior_value, text, validation_type, trigger_type, widget_name):
    # action=1 -> insert
    if action == '1':
        if text in '0123456789':
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        if text in '-' and value_if_allowed == '-':
            return True
        else:
            return False
    else:
        return True


# add passed argument text to the output tab's scrolledtext
def addEntryContentToScrolledText(text, textwidget):
    entryValue = text
    textwidget.configure(state='normal')
    if entryValue != "":
        textwidget.insert("insert", (entryValue + "\n"))
    textwidget.configure(state='disabled')
    textwidget.see('end')


# helper function to return all the keys of all the current existing scenarios
def getKeys(file):
    if file == '':
        filename = tempfile.gettempdir() + '/or/pickleDict.txt'
    else:
        filename = file
    keys = []
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
        if not lines:
            return None
        for line in lines:
            keys.append(line[-4:])
    return keys


# python doesn't like numbers with zeros in front (0001, 0002...)
# this helper function returns the number with the zeros in front by turning it to a string
def fixNumbers(number):
    numbers = [char for char in str(number)]
    strFixed = str(number)
    zeros = 4 - len(numbers)
    for x in range(zeros):
        strFixed = "0" + strFixed
    return strFixed


# helper function, allows you to pass functions to be called together, each with respective parameters
def combine_funcs(*funcs):
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)

    return combined_func


# the popup that appears when pressing the save button, places all existing scenarios as checkboxes, allowing you to
# select an arbitrary amount to be saved. the save button kills the popup and calls save_selected_scenarios with the
# selected checkboxes
def popup_select_scenarios(keys):
    win = tk.Toplevel()
    win.resizable(width=False, height=False)
    win.geometry('175x225')
    win.wm_title("Select scenarios to be saved")

    canvas = tk.Canvas(win, width=175, height=175)

    x = 0
    y = 0
    var_list = []
    for key in keys:
        var = tk.IntVar()
        var_list.append(var)
        cb = tk.Checkbutton(canvas, text=key, variable=var)
        canvas.create_window(y * 75, x * 25, anchor='nw', window=cb)
        if x == 6:
            y += 1
            x = 0
        else:
            x += 1

    canvas.grid(row=0, column=0)
    if len(keys) > 14:
        scroll_x = tk.Scrollbar(win, orient="horizontal", command=canvas.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")

        canvas.configure(xscrollcommand=scroll_x.set)
        canvas.configure(scrollregion=canvas.bbox("all"))

    save_button = ttk.Button(win, text="Save",
                             command=combine_funcs(win.destroy, lambda: save_selected_scenarios(var_list, keys)))
    if y in [0, 1, 2]:
        col = 0
    else:
        col = int(y / 2)
    save_button.grid(row=8, column=col, columnspan=2)


# given the list of checkboxes, check if any are selected. if none are create error popup and close the first popup. if
# any are selected, open a directory selector popup, and in the chosen directory copy the selected scenarios to the
# directory, in a file titled "LGSVL" followed by today's date and the current time. also create a new pickleDict which
# is a subset of the current pickleDict, however it only contains the relevant scenarios and not the unselected ones
def save_selected_scenarios(var_list, keys):
    values = []
    keysToBeSaved = []
    for var in var_list:
        values.append(var.get())
    if all(i == 0 for i in values):
        error_popup('Error: No scenarios selected')
    else:
        indices = [i for i, e in enumerate(values) if e == 1]
        x = 0
        for key in keys:
            if x in indices:
                keysToBeSaved.append(key)
            x += 1
        # print(keysToBeSaved)
        homedir = os.environ['HOME']
        root.directory = tk.filedialog.askdirectory(initialdir=homedir)
        pfiles, dict_lines = get_picklefiles(keysToBeSaved, '')
        path = root.directory + '/LGSVL ' + str(
            datetime.strptime(str(datetime.now().replace(microsecond=0)), '%Y-%m-%d %H:%M:%S').strftime(
                '%d-%m-%Y %H:%M:%S'))
        try:
            os.mkdir(path)
        except OSError:
            addEntryContentToScrolledText("Creation of the directory %s failed" % path, tab3_output_scrolledtext)
        else:
            addEntryContentToScrolledText("Successfully created the directory %s " % path, tab3_output_scrolledtext)
        copy_pfiles(pfiles, '', path)
        write_pickledict(dict_lines, path)


# given a list of names of pickle files to be copied and a path for them to be copied to, copy the pickle files to the
# directory at the given path
def copy_pfiles(pfiles, fromPath, toPath):
    if fromPath == '':
        fromPath = tempfile.gettempdir() + '/or'
    if toPath == '':
        if not os.path.isdir(tempfile.gettempdir() + '/or'):
            try:
                os.mkdir(tempfile.gettempdir() + '/or')
            except OSError:
                print("Creation of the directory %s failed" % tempfile.gettempdir() + '/or')
                return
            else:
                print("Successfully created the directory %s " % tempfile.gettempdir() + '/or')
        toPath = tempfile.gettempdir() + '/or'
    directory = os.fsencode(fromPath)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        # str_filename = str(filename)
        if filename in pfiles:
            shutil.copy(fromPath + '/' + filename, toPath)
            continue
        else:
            continue


# given lines to be written in the pickleDict, and the path of where the pickle files will be stored, write a new
# pickleDict file
def write_pickledict(lines, path):
    file = path + '/pickleDict.txt'
    f = open(file, 'w')
    f.write('\n'.join(lines))
    f.close()


# given the keys of the selected scenarios, return a list of corresponding file names, and corresponding lines
# in pickleDict
def get_picklefiles(keys, path):
    if path == '':
        path = tempfile.gettempdir() + '/or/pickleDict.txt'
    else:
        path = path + '/pickleDict.txt'
    files = []
    lines_with_file = []
    with open(path, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            if line[-4:] in keys:
                lines_with_file.append(line)
                files.append(line.replace(line[-6:], ''))
    return files, lines_with_file


# generic error message popup, print passed message with okay button to close popup
def error_popup(msg):
    pop = tk.Toplevel()
    pop.wm_title("ERROR")
    label = tk.Label(pop, text=msg)
    label.grid(row=0, column=0)
    btn = ttk.Button(pop, text="Okay", command=pop.destroy)
    btn.grid(row=1, column=0)


def are_you_sure_popup(msg, command):
    pop = tk.Toplevel()
    label = tk.Label(pop, text=msg)
    label.grid(columnspan=2)
    btn_y = tk.Button(pop, text='Yes', bg='green', command=combine_funcs(command, pop.destroy))
    btn_n = tk.Button(pop, text='No', command=pop.destroy, bg='red')
    btn_y.grid(row=1)
    btn_n.grid(row=1, column=1)
    root.wait_window(pop)


def validate_pickles(path):
    try:
        keys = getKeys(path + '/pickleDict.txt')
    except FileNotFoundError:
        return False
    except TypeError:
        return True, None

    files, lines = get_picklefiles(keys, path)

    directory = os.fsencode(path)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename not in files:
            if filename == 'pickleDict.txt':
                continue
            else:
                return False

    return True, files
    # print(keys)


def update_available_replays(canvas):
    try:
        keys = getKeys('')
        if keys == '':
            canvas.place_forget()
        x = 0
        y = 0
        lbs = []
        for key in keys:
            lb = tk.Label(canvas, text=key)
            lbs.append(lb)
            canvas.create_window(y * 75, x * 20, anchor='nw', window=lb)
            if x == 6:
                y += 1
                x = 0
            else:
                x += 1

        canvas.place(relx=0.5, rely=0.5, anchor='center')
        if len(keys) > 14:
            scroll_x = tk.Scrollbar(tab2, orient="horizontal", command=canvas.xview)
            scroll_x.place(relx=0.5, rely=0.65, anchor='center', width=200)

            canvas.configure(xscrollcommand=scroll_x.set)
            canvas.configure(scrollregion=canvas.bbox("all"))
    except FileNotFoundError:
        canvas.place_forget()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# These functions are ones that are called from different buttons, and rely on the helper functions
# in the code section above

def run():
    tab1_error_label.grid_forget()
    tab1_nameerror_label.grid_forget()

    try:
        msg = Randomizer.run(tab1_vehicle_name_entry.get(), variable_NPCs.get(), tab1_map_entry.get(),
                             tab1_runtime_entry.get(), tab1_seed_entry.get(), tab1_timescale_entry.get())
        addEntryContentToScrolledText(msg, tab3_output_scrolledtext)
    except ZeroDivisionError:
        tab1_nameerror_label.grid(columnspan=2, column=1)
    except ValueError:
        tab1_error_label.grid(columnspan=2, column=1)
    else:
        for x in range(int(tab1_runs_entry.get()) - 1):
            msg = Randomizer.run(tab1_vehicle_name_entry.get(), variable_NPCs.get(), tab1_map_entry.get(),
                                 tab1_runtime_entry.get(), tab1_seed_entry.get(), tab1_timescale_entry.get())
            addEntryContentToScrolledText(msg, tab3_output_scrolledtext)
    update_available_replays(tab2_replays_canvas)


def Replay():
    tab2_error_label.pack_forget()
    try:
        Randomizer.replay(tab2_replaykey_entry.get())
    except ZeroDivisionError:
        tab2_error_label.pack()


def Clear():
    are_you_sure_popup("Doing this will delete all stored scenarios\n Scenarios can be saved in the output tab\n "
                       "Continue?", do_Clear)


def do_Clear():
    shutil.rmtree(tempfile.gettempdir() + '/or', ignore_errors=True)
    clear_output()
    update_available_replays(tab2_replays_canvas)


def clear_output():
    tab3_output_scrolledtext.configure(state='normal')
    tab3_output_scrolledtext.delete('1.0', 'end')
    tab3_output_scrolledtext.configure(state='disabled')


def save_to_file():
    try:
        keys = getKeys('')
    except FileNotFoundError:
        error_popup('Error: no scenarios exist')
    else:
        popup_select_scenarios(keys)


def load_from_file():
    Clear()
    homedir = os.environ['HOME']
    root.directory = tk.filedialog.askdirectory(initialdir=homedir)
    validate, files = validate_pickles(root.directory)
    if not validate:
        error_popup('Error: Can not load file, something has been deleted, renamed, or moved')
    else:
        if files is None:
            return
        else:
            source = root.directory
            if not os.path.isdir(tempfile.gettempdir() + '/or'):
                try:
                    os.mkdir(tempfile.gettempdir() + '/or')
                except OSError:
                    return
            dest = tempfile.gettempdir() + '/or'
            all_files = os.listdir(source)
            for f in all_files:
                src = source + '/' + str(f)
                shutil.copy(src, dest)
            addEntryContentToScrolledText("Successfully loaded from %s " % source, tab3_output_scrolledtext)
            update_available_replays(tab2_replays_canvas)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Run tab widgets
tab1_vehicle_name_label = tk.Label(tab1, text="Vehicle name")
tab1_vehicle_name_note_label = tk.Label(tab1,
                                        text="Important: Enter vehicle name exactly as how it appears on LGSVL "
                                             "control site", wraplength=275)
tab1_seed_label = tk.Label(tab1, text="Seed (leave blank for random)")
tab1_NPCs_label = tk.Label(tab1, text="NPCs")
tab1_map_label = tk.Label(tab1, text="Map")
tab1_runs_label = tk.Label(tab1, text="Runs")
tab1_runtime_label = tk.Label(tab1, text="Runtime")
tab1_timescale_label = tk.Label(tab1, text="Timescale")
tab1_nameerror_label = tk.Label(tab1, text="Error: Vehicle name does not exist")
tab1_error_label = tk.Label(tab1, text="Error: Illegal value entered")
tab1_vehicle_name_entry = tk.Entry(tab1)
OPTIONS_NPCs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
                29, 30]
variable_NPCs = tk.StringVar(root)
variable_NPCs.set(OPTIONS_NPCs[19])
tab1_NPCs_entry = tk.OptionMenu(tab1, variable_NPCs, *OPTIONS_NPCs)
tab1_map_entry = tk.Entry(tab1)
tab1_map_entry.insert(0, "BorregasAve")
vcmd = (root.register(validate_int),
        '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
vcmd2 = (root.register(validate_int_negatives),
         '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
vcmd3 = (root.register(validate_float),
         '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
tab1_seed_entry = tk.Entry(tab1, validate='key', validatecommand=vcmd2)
tab1_runs_entry = tk.Entry(tab1, validate='key', validatecommand=vcmd)
tab1_runtime_entry = tk.Entry(tab1, validate='key', validatecommand=vcmd3)
tab1_timescale_entry = tk.Entry(tab1, validate='key', validatecommand=vcmd3)
tab1_timescale_entry.insert(0, "1")
tab1_run_button = tk.Button(tab1, text="RUN", command=run)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Run tab widget placement
tab1_vehicle_name_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
tab1_vehicle_name_entry.grid(row=0, column=1, pady=15, sticky="w")

tab1_vehicle_name_note_label.grid(row=1, columnspan=2, padx=15, pady=15)

tab1_seed_label.grid(row=2, column=0, padx=15, pady=15, sticky="w")
tab1_seed_entry.grid(row=2, column=1, pady=15, sticky="w")

tab1_NPCs_label.grid(row=3, column=0, padx=15, pady=15, sticky="w")
tab1_NPCs_entry.grid(row=3, column=1, pady=15, sticky="w")

tab1_map_label.grid(row=0, column=2, padx=15, pady=15, sticky="e")
tab1_map_entry.grid(row=0, column=3, padx=15, pady=15, sticky="w")

tab1_runs_label.grid(row=1, column=2, padx=15, pady=15, sticky="e")
tab1_runs_entry.grid(row=1, column=3, padx=15, pady=15, sticky="w")

tab1_runtime_label.grid(row=2, column=2, padx=15, pady=15, sticky="e")
tab1_runtime_entry.grid(row=2, column=3, padx=15, pady=15, sticky="w")

tab1_timescale_label.grid(row=3, column=2, padx=15, pady=15, sticky="e")
tab1_timescale_entry.grid(row=3, column=3, padx=15, pady=15, sticky="w")

tab1_run_button.grid(row=4, columnspan=2, column=1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Replay tab widgets
tab2_replaykey_label = tk.Label(tab2, text="Replay key")
tab2_replaykey_entry = tk.Entry(tab2, validate='key', validatecommand=vcmd, justify='center')
tab2_error_label = tk.Label(tab2, text="Error: Replay key not found")
tab2_replaykey_button = tk.Button(tab2, text="REPLAY", command=Replay)
tab2_clearreplays_button = tk.Button(tab2, text="Clear Stored Replays", command=Clear)

tab2_replaykey_label.config(anchor='center')
tab2_error_label.config(anchor='n')
tab2_replaykey_label.pack()
tab2_replaykey_entry.pack()
tab2_replaykey_button.place(relx=0.5, rely=0.75, anchor='center')
tab2_clearreplays_button.place(relx=0.5, rely=0.95, anchor='s')

tab2_replays_canvas = tk.Canvas(tab2, width=175, height=125)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Output tab widgets
tab3_output_frame = tk.Frame(tab3)
tab3_output_scrolledtext = ScrolledText(tab3_output_frame, font=("Helvetica", 11), width=70, height=20,
                                        state='disabled')
tab3_clear_button = tk.Button(tab3, text="CLEAR", command=clear_output)
tab3_save_button = tk.Button(tab3, text="SAVE", padx=15, command=save_to_file)
tab3_load_button = tk.Button(tab3, text="LOAD", padx=15, command=load_from_file)

# addEntryContentToScrolledText(myEntry, tab3_output_scrolledtext)

tab3_output_frame.pack(side='right')
tab3_output_scrolledtext.pack()
tab3_clear_button.place(relx=0.135, rely=0.10, anchor='e')
tab3_save_button.place(relx=0.135, rely=0.20, anchor='e')
tab3_load_button.place(relx=0.135, rely=0.30, anchor='e')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

tabControl.pack(expan=1, fill="both")
update_available_replays(tab2_replays_canvas)
root.mainloop()
