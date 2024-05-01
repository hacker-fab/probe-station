# Hacker Fab
# Luca Garlati, 2024
# Main probe station script

from tkinter import *
#import sys and use path insert to add lib files
import sys
from os.path import join, dirname, realpath
from typing import Callable, Literal
sys.path.insert(0, join(dirname(dirname(realpath(__file__))), "lib"))
from gui_lib import *
from img_lib import *
from backend_lib import *

THUMBNAIL_SIZE: tuple[int,int] = (160,90)
CHIN_SIZE: int = 200
SPACER_SIZE: int = 20
GRID_SIZE: tuple[int,int] = (6,7)
GUI: GUI_Controller = GUI_Controller(grid_size=GRID_SIZE,
                                     title = "Probe Station",
                                     add_window_size=(0,CHIN_SIZE),
                                     add_projector = False,
                                     )
debug: Debug = Debug(root=GUI.root)
debug.grid( row=GRID_SIZE[0]-1, 
            col=0,
            colspan=GRID_SIZE[1])
GUI.add_widget("debug", debug)
#region: Camera
img_size = (GUI.window_size[0],(GUI.window_size[0]*9)//16)
camera_placeholder = rasterize(Image.new('RGB', img_size, (0,0,0)))
camera: Label = Label(
  GUI.root,
  image=camera_placeholder
  )
camera.grid(
  row = 0,
  column = 0,
  columnspan = GRID_SIZE[1],
  sticky='nesw')
GUI.add_widget("camera", camera)
#endregion

#region: probes
probes_row: int = 1
probes_column: int = 0

stages_busy: bool = False
probe_stages: Multi_Stage = Multi_Stage(names = ["top","bottom","left","right"],
                                        debug = debug,
                                        location_query = lambda: GUI.get_coords("camera", img_size))

#region: label

label: Label = Label(
  GUI.root,
  text="Probe Controls",
  justify = 'center',
  anchor = 'center'
)
label.grid(
  row = probes_row,
  column = probes_column,
  columnspan = 3,
  sticky='nesw')
GUI.add_widget("label", label)

#endregion: label

#region: calibrate button
# make the stage being calibrated have a yellow background

def calibrate_button():
  # check if stages are busy
  global stages_busy
  if(stages_busy):
    debug.warn("Cannot calibrate, stages busy")
    return
  else:
    stages_busy = True
  # calibrate each stage
  calibrate_button.config(bg="yellow")
  calibrated_stages: list[str] = []
  for name in probe_stages.get_enabled():
    # don't clibrate if stage is locked
    if(probe_stages.get(name).is_locked()):
      continue
    # 
    this_cycle: Cycle = GUI.get_widget(name+"_probe_cycle")
    this_cycle.update_state(0, colors = ("black","yellow"))
    this_cycle.update_state(1, colors = ("black","yellow"))
    probe_stages.calibrate( name = name,
                            step_size = (100,100),
                            calibrate_backlash = "None",
                            return_to_start = True)
    this_cycle.update_state(0, colors = ("black","green"))
    this_cycle.update_state(1, colors = ("black","white"))
    calibrated_stages.append(name)
  # finished
  if(len(calibrated_stages) > 0):
    debug.info(f"Calibrated stages: {calibrated_stages}")
  calibrate_button.config(bg="lightgray")
  stages_busy = False
    
calibrate_button: Button = Button(
  GUI.root,
  text="calibrate",
  fg="black",
  bg="lightgray",
  command=calibrate_button)
calibrate_button.grid(
  row = probes_row+3,
  column = probes_column+2,
  sticky='nesw')
GUI.add_widget("button", calibrate_button)

#endregion: calibrate button

#region: lock button
# locks all selected stages, or unlocks locked stages

locked_stages: list[str] = []
def toggle_lock():
  global locked_stages, stages_busy
  # immediately return if none selected and none locked
  if(len(probe_stages.get_enabled()) == 0 and len(locked_stages) == 0):
    return
  # check if stages are busy
  if(stages_busy):
    debug.warn("Cannot lock, stages busy")
    return
  else:
    stages_busy = True
  # if no stages are locked, and at least one stage selected, lock selected
  if(len(locked_stages) == 0 and len(probe_stages.get_enabled()) > 0):
    for name in probe_stages.get_enabled():
      probe_stages.get(name).lock()
      this_cycle: Cycle = GUI.get_widget(name+"_probe_cycle")
      this_cycle.update_state(0, colors = ("black","red"))
      this_cycle.update_state(1, colors = ("black","pink"))
      this_cycle.goto(1)
      locked_stages.append(name)
    lock_button.config(text="unlock", bg="red")
  # if there are locked stages, unlock them all
  else:
    for name in locked_stages:
      probe_stages.get(name).unlock()
      this_cycle: Cycle = GUI.get_widget(name+"_probe_cycle")
      this_cycle.update_state(0, colors = ("black","green"))
      this_cycle.update_state(1, colors = ("black","white"))
    locked_stages = []
    lock_button.config(text="lock", bg="lightgray")
  # finished
  debug.info(f"Locked stages: {locked_stages}")
  stages_busy = False

lock_button: Button = Button(
  GUI.root,
  text="lock",
  fg="black",
  bg="lightgray",
  command=toggle_lock)
lock_button.grid(
  row = probes_row+3,
  column = probes_column,
  sticky='nesw')
GUI.add_widget("button", lock_button)

#endregion: lock button

#region: toggle all button
# deselect all stages if any are selected, if none selected select all

def toggle_all():
  # check if stages are busy
  global stages_busy
  if(stages_busy):
    debug.warn("Cannot toggle all, stages busy")
    return
  else:
    stages_busy = True
  # if any stages are selected, deselect all
  if(len(probe_stages.get_enabled()) > 0):
    for name in probe_stages.get_enabled():
      GUI.get_widget(name+"_probe_cycle").goto(1)
    debug.info("Deselected all stages")
  # if no stages are selected, select all
  else:
    for name in probe_stages.get_names():
      GUI.get_widget(name+"_probe_cycle").goto(0)
    debug.info("Selected all stages")
  # finished
  update_toggle_all_text()
  stages_busy = False

def update_toggle_all_text():
  if(len(probe_stages.get_enabled()) > 0):
    toggle_all_button.config(text="Deselect All")
  else:
    toggle_all_button.config(text="Select All")
  
toggle_all_button: Button = Button(
  GUI.root,
  text="Select All",
  fg="black",
  bg="lightgray",
  command=toggle_all)
toggle_all_button.grid(
  row = probes_row+1,
  column = probes_column,
  sticky='nesw')
GUI.add_widget("button", toggle_all_button)


#endregion: toggle all button

#region: goto button
def goto_button_func():
  # check if stages are busy
  global stages_busy
  if(stages_busy):
    debug.warn("Cannot move, stages busy")
    return
  else:
    stages_busy = True
  goto_button.config(bg="yellow")
  moved_stages: list[str] = []
  for name in probe_stages.get_enabled():
    # don't move if stage is locked
    if(probe_stages.get(name).is_locked()):
      continue
    # can't move if not calibrated
    if(not probe_stages.get(name).is_calibrated()):
      debug.warn(f"Cannot move {name}: not calibrated")
      continue
    this_cycle: Cycle = GUI.get_widget(name+"_probe_cycle")
    this_cycle.update_state(0, colors = ("black","yellow"))
    this_cycle.update_state(1, colors = ("black","yellow"))
    probe_stages.get(name).goto()
    this_cycle.update_state(0, colors = ("black","green"))
    this_cycle.update_state(1, colors = ("black","white"))
    moved_stages.append(name)
  # finished
  if(len(moved_stages) > 0):
    debug.info(f"Moved stages: {moved_stages}")
  goto_button.config(bg="lightgray")
  stages_busy = False
    
  
goto_button: Button = Button(
  GUI.root,
  text="goto",
  fg="black",
  bg="lightgray",
  command=goto_button_func
  )
goto_button.grid(
  row = probes_row+1,
  column = probes_column+2,
  sticky='nesw')
GUI.add_widget("button", goto_button)

#endregion: goto button

#region: Cycle widgets

def probe_toggle(probe_name: str, force: Literal['on','off']):
  probe_stages.toggle(probe_name, force = force)
  update_toggle_all_text()

#region: top probe

# cycle widget
top_probe_cycle: Cycle = Cycle(GUI,"top_probe_cycle")
top_probe_cycle.grid(
  row = probes_row+1,
  col = probes_column+1)
top_probe_cycle.add_state("Top Probe\n(0,0,0)",
                          ("black","green"),
                          enter = lambda: probe_toggle("top", 'on'))
top_probe_cycle.add_state("Top Probe\n(0,0,0)",
                          ("black","white"),
                          enter = lambda: probe_toggle("top", 'off'))
top_probe_cycle.goto(1)
probe_stages.toggle("top",force = 'off')

def update_top_probe_text():
  stage = probe_stages.get("top")
  coords: str = f"({int(stage.x())},{int(stage.y())},{int(stage.z())})"
  top_probe_cycle.update_state(0, text = "Top Probe\n"+coords)
  top_probe_cycle.update_state(1, text = "Top Probe\n"+coords)
probe_stages.get("top").add_callback("any", "update text", update_top_probe_text)

#endregion: top probe

#region: bottom probe


bottom_probe_cycle: Cycle = Cycle(GUI,"bottom_probe_cycle")
bottom_probe_cycle.grid(
  row = probes_row+3,
  col = probes_column+1)
bottom_probe_cycle.add_state("Bottom Probe\n(0,0,0)",
                             ("black","green"),
                              enter = lambda: probe_toggle("bottom", 'on'))
bottom_probe_cycle.add_state("Bottom Probe\n(0,0,0)",
                             ("black","white"),
                              enter = lambda: probe_toggle("bottom", 'off'))
bottom_probe_cycle.goto(1)
probe_stages.toggle("bottom",force = 'off')

def update_bottom_probe_text():
  stage = probe_stages.get("bottom")
  coords: str = f"({int(stage.x())},{int(stage.y())},{int(stage.z())})"
  bottom_probe_cycle.update_state(0, text = "Bottom Probe\n"+coords)
  bottom_probe_cycle.update_state(1, text = "Bottom Probe\n"+coords)
probe_stages.get("bottom").add_callback("any", "update text", update_bottom_probe_text)

#endregion: bottom probe

#region: left probe

left_probe_cycle: Cycle = Cycle(GUI,"left_probe_cycle")
left_probe_cycle.grid(
  row = probes_row+2,
  col = probes_column)
left_probe_cycle.add_state("Left Probe\n(0,0,0)",
                           ("black","green"),
                           enter = lambda: probe_toggle("left", force = 'on'))
left_probe_cycle.add_state("Left Probe\n(0,0,0)",
                           ("black","white"),
                            enter = lambda: probe_toggle("left", force = 'off'))
left_probe_cycle.goto(1)
probe_stages.toggle("left",force = 'off')

def update_left_probe_text():
  stage = probe_stages.get("left")
  coords: str = f"({int(stage.x())},{int(stage.y())},{int(stage.z())})"
  left_probe_cycle.update_state(0, text = "Left Probe\n"+coords)
  left_probe_cycle.update_state(1, text = "Left Probe\n"+coords)
probe_stages.get("left").add_callback("any", "update text", update_left_probe_text)

#endregion: left probe

#region: right probe

right_probe_cycle: Cycle = Cycle(GUI,"right_probe_cycle")
right_probe_cycle.grid(
  row = probes_row+2,
  col = probes_column+2)
right_probe_cycle.add_state("Right Probe\n(0,0,0)",
                            ("black","green"),
                            enter = lambda: probe_toggle("right", force = 'on'))
right_probe_cycle.add_state("Right Probe\n(0,0,0)",
                            ("black","white"),
                            enter = lambda: probe_toggle("right", force = 'off'))
right_probe_cycle.goto(1)
probe_stages.toggle("right",force = 'off')

def update_right_probe_text():
  stage = probe_stages.get("right")
  coords: str = f"({int(stage.x())},{int(stage.y())},{int(stage.z())})"
  right_probe_cycle.update_state(0, text = "Right Probe\n"+coords)
  right_probe_cycle.update_state(1, text = "Right Probe\n"+coords)
probe_stages.get("right").add_callback("any", "update text", update_right_probe_text)

#endregion: right probe

#endregion: Cycle widgets

#endregion: probes

GUI.root.grid_columnconfigure(3, minsize=SPACER_SIZE)

#region: stepping

stepping_row: int = 1
stepping_col: int = 4

def step_update(axis: Literal['-x','+x','-y','+y','-z','+z']):
  # first check if the step size has changed
  if(x_step_intput.changed() or y_step_intput.changed() or z_step_intput.changed()):
    probe_stages.step_size = (x_step_intput.get(), y_step_intput.get(), z_step_intput.get())
  probe_stages.step(axis)

#region: Stage Step size
step_size_text: Label = Label(
  GUI.root,
  text = "Step Size",
  justify = 'center',
  anchor = 'center'
)
step_size_text.grid(
  row = stepping_row,
  column = stepping_col,
  columnspan = 3,
  sticky='nesw'
)
GUI.add_widget("step_size_text", step_size_text)

x_step_intput = Intput(
  gui=GUI,
  name="x_step_intput",
  default=1)
x_step_intput.grid(stepping_row+1,stepping_col)

y_step_intput = Intput(
  gui=GUI,
  name="y_step_intput",
  default=1)
y_step_intput.grid(stepping_row+1,stepping_col+1)

z_step_intput = Intput(
  gui=GUI,
  name="z_step_intput",
  default=1)
z_step_intput.grid(stepping_row+1,stepping_col+2)

#endregion

#region: stepping buttons
step_button_row = 2
### X axis ###
up_x_button: Button = Button(
  GUI.root,
  text = '+x',
  command = lambda : step_update('+x')
  )
up_x_button.grid(
  row = stepping_row+step_button_row,
  column = stepping_col,
  sticky='nesw')
GUI.add_widget("up_x_button", up_x_button)

down_x_button: Button = Button(
  GUI.root,
  text = '-x',
  command = lambda : step_update('-x')
  )
down_x_button.grid(
  row = stepping_row+step_button_row+1,
  column = stepping_col,
  sticky='nesw')
GUI.add_widget("down_x_button", down_x_button)

### Y axis ###
up_y_button: Button = Button(
  GUI.root,
  text = '+y',
  command = lambda : step_update('+y')
  )
up_y_button.grid(
  row = stepping_row+step_button_row,
  column = stepping_col+1,
  sticky='nesw')
GUI.add_widget("up_y_button", up_y_button)

down_y_button: Button = Button(
  GUI.root,
  text = '-y',
  command = lambda : step_update('-y')
  )
down_y_button.grid(
  row = stepping_row+step_button_row+1,
  column = stepping_col+1,
  sticky='nesw')
GUI.add_widget("down_y_button", down_y_button)

### Z axis ###
up_z_button: Button = Button(
  GUI.root,
  text = '+z',
  command = lambda : step_update('+z')
  )
up_z_button.grid(
  row = stepping_row+step_button_row,
  column = stepping_col+2,
  sticky='nesw')
GUI.add_widget("up_z_button", up_z_button)

down_z_button: Button = Button(
  GUI.root,
  text = '-z',
  command = lambda : step_update('-z')
  )
down_z_button.grid(
  row = stepping_row+step_button_row+1,
  column = stepping_col+2,
  sticky='nesw')
GUI.add_widget("down_z_button", down_z_button)

#endregion

#region: keyboard input

def bind_stage_controls() -> None:
  GUI.root.bind('<Up>',           lambda event: step_update('+y'))
  GUI.root.bind('<Down>',         lambda event: step_update('-y'))
  GUI.root.bind('<Left>',         lambda event: step_update('-x'))
  GUI.root.bind('<Right>',        lambda event: step_update('+x'))
  GUI.root.bind('<Control-Up>',   lambda event: step_update('+z'))
  GUI.root.bind('<Control-Down>', lambda event: step_update('-z'))
  GUI.root.bind('<Shift-Up>',     lambda event: step_update('+z'))
  GUI.root.bind('<Shift-Down>',   lambda event: step_update('-z'))
def unbind_stage_controls() -> None:
  GUI.root.unbind('<Up>')
  GUI.root.unbind('<Down>')
  GUI.root.unbind('<Left>')
  GUI.root.unbind('<Right>')
  GUI.root.unbind('<Control-Up>')
  GUI.root.unbind('<Control-Down>')
  GUI.root.unbind('<Shift-Up>')
  GUI.root.unbind('<Shift-Down>')

#endregion

#endregion: stepping

#region: show image ontop button
# #offset calibration (different for each monitor)
# monitor_offset: int = (3,25)
# def show_image(size: tuple[int,int] = (3,3),
#                color: tuple[int,int,int] = (255,0,0),
#                location: tuple[int,int] = (0,0)) -> Tk:
#   #alert=canvas.create_image(100,200,image=alert_panel,anchor=NW)
#   test_img = rasterize(Image.new('RGB', size, color))
#   top = Toplevel(GUI.root)
#   # top.withdraw()
#   top.overrideredirect(True) # make border-less window
#   top.attributes('-topmost', True)
#   # make it like a transparent window
#   trans_color = '#ffffff'  # select a color not used by the alert image
#   top.attributes('-transparentcolor', trans_color)
#   # show the alert image
#   alert = Label(top, image=test_img, bg=trans_color)
#   alert.image = test_img
#   alert.pack()
#   # put the popup at the center of root window
#   top.update()
#   root_xy = (GUI.root.winfo_x(), GUI.root.winfo_y())
#   # rw, rh = GUI.root.winfo_width(), GUI.root.winfo_height()
#   # tw, th = top.winfo_width(), top.winfo_height()
#   coords = add(add(add(location, root_xy), round_tuple(div(size,2))),monitor_offset)
#   top.geometry(f"+{coords[0]}+{coords[1]}")
#   return top

# last_image: Tk = None
# def show_click():
#   GUI.root.update()
#   global last_image
#   if(last_image != None):
#     last_image.destroy()
#   last_image = show_image(location=GUI.get_coords(in_pixels=True))

# main_func_manager.add("show_click", show_click)

# image_button: Button = Button(
#   GUI.root,
#   text="show image",
#   command=main_func_manager
#   )
# image_button.grid(
#   row = 2,
#   column = 4,
#   sticky='nesw'
# )

# #endregion

update_toggle_all_text()
GUI.debug.info("Debug info will appear here")
GUI.mainloop()