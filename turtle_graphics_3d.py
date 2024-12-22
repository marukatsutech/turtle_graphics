""" Turtle graphics 3D

Sample:
penup
set distance 20
set angle_a 110
set angle_b 280
pendown
repeat 50 [
    forward distance
    roll_cw angle_a
    forward distance
    up angle_b
    forward distance
    right angle_a
]
"""

from matplotlib.figure import Figure
import matplotlib.animation as animation
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import mpl_toolkits.mplot3d.art3d as art3d
from scipy.spatial.transform import Rotation

from decimal import Decimal, getcontext
getcontext().prec = 50


""" Global variables """
command_counter = 0
size_turtle = 5
commands = []
expanded_commands = []
variables = {}

""" Animation control """
is_play = False
is_run = False

""" Axis vectors """
vector_x_axis = np.array([1., 0., 0.])
vector_y_axis = np.array([0., 1., 0.])
vector_z_axis = np.array([0., 0., 1.])

""" Create figure and axes """
title_ax0 = "Turtle graphics 3D"
title_tk = title_ax0

x_min = -100.
x_max = 100.
y_min = -100.
y_max = 100.
z_min = -100.
z_max = 100.

fig = Figure()
ax0 = fig.add_subplot(111, projection='3d')
ax0.set_box_aspect((1, 1, 1))
ax0.grid()
ax0.set_title(title_ax0)
ax0.set_xlabel("x")
ax0.set_ylabel("y")
ax0.set_zlabel("z")
ax0.set_xlim(x_min, x_max)
ax0.set_ylim(y_min, y_max)
ax0.set_zlim(z_min, z_max)

""" Embed in Tkinter """
root = tk.Tk()
root.title(title_tk)
canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().pack(expand=True, fill="both")

toolbar = NavigationToolbar2Tk(canvas, root)
canvas.get_tk_widget().pack()


class Counter:
    def __init__(self, is3d=None, ax=None, xy=None, z=None, label=""):
        self.is3d = is3d if is3d is not None else False
        self.ax = ax
        self.x, self.y = xy[0], xy[1]
        self.z = z if z is not None else 0
        self.label = label

        self.count = 0

        if not is3d:
            self.txt_step = self.ax.text(self.x, self.y, self.label + str(self.count))
        else:
            self.txt_step = self.ax.text2D(self.x, self.y, self.label + str(self.count))
            self.xz, self.yz, _ = proj3d.proj_transform(self.x, self.y, self.z, self.ax.get_proj())
            self.txt_step.set_position((self.xz, self.yz))

    def count_up(self):
        self.count += 1
        self.txt_step.set_text(self.label + str(self.count))

    def reset(self):
        self.count = 0
        self.txt_step.set_text(self.label + str(self.count))

    def get(self):
        return self.count


class Turtle3d:
    def __init__(self, ax=None, xyz=None, direction=None, size=None, color=None):
        self.ax = ax
        self.xyz = np.array(xyz, dtype=np.float64)
        self.direction = Decimal(direction)
        self.size = size
        self.color = color

        self.roll_axis = np.array([1., 0., 0.])
        self.pitch_axis = np.array([0., 1., 0.])
        self.yaw_axis = np.array([0., 0., 1.])

        self.body_vertices = [[self.pitch_axis * -10. + self.xyz,
                               self.roll_axis * 10. + self.xyz,
                               self.pitch_axis * 10. + self.xyz]]
        self.body = Poly3DCollection(self.body_vertices, facecolors=self.color, linewidths=1, edgecolors=self.color, alpha=.25)
        self.ax.add_collection3d(self.body)

        self.x_path = []
        self.y_path = []
        self.z_path = []
        self.path, = self.ax.plot(np.array(self.x_path, dtype=np.float64),
                                  np.array(self.y_path, dtype=np.float64),
                                  np.array(self.z_path, dtype=np.float64))

        self.is_pen_down = False

    def pendown(self):
        self.is_pen_down = True
        self.x_path.append(self.xyz[0])
        self.y_path.append(self.xyz[1])
        self.z_path.append(self.xyz[2])

    def penup(self):
        self.is_pen_down = False

    def forward(self, distance):
        normalized_vector = self.roll_axis / np.linalg.norm(self.roll_axis)
        self.xyz = self.xyz + normalized_vector * float(distance)

        if self.is_pen_down:
            self.x_path.append(self.xyz[0])
            self.y_path.append(self.xyz[1])
            self.z_path.append(self.xyz[2])
        else:
            self.x_path.append(None)
            self.y_path.append(None)
            self.z_path.append(None)

        self.update_draw()

    def forward_step(self, distance):
        d = 0
        step = 1
        while d + step <= distance:
            normalized_vector = self.roll_axis / np.linalg.norm(self.roll_axis)
            self.xyz = self.xyz + normalized_vector * float(step)

            if self.is_pen_down:
                self.x_path.append(self.xyz[0])
                self.y_path.append(self.xyz[1])
                self.z_path.append(self.xyz[2])
            else:
                self.x_path.append(None)
                self.y_path.append(None)
                self.z_path.append(None)

            self.update_draw()
            d += step

        remaining_distance = distance - d
        if remaining_distance > 0:
            normalized_vector = self.roll_axis / np.linalg.norm(self.roll_axis)
            self.xyz = self.xyz + normalized_vector * float(remaining_distance)

            if self.is_pen_down:
                self.x_path.append(self.xyz[0])
                self.y_path.append(self.xyz[1])
                self.z_path.append(self.xyz[2])
            else:
                self.x_path.append(None)
                self.y_path.append(None)
                self.z_path.append(None)

            self.update_draw()

    def right(self, angle):
        self.yaw(- angle)

    def left(self, angle):
        self.yaw(angle)

    def up(self, angle):
        self.pitch(- angle)

    def down(self, angle):
        self.pitch(angle)

    def roll_cw(self, angle):
        self.roll(angle)

    def roll_ccw(self, angle):
        self.roll(- angle)

    def roll(self, angle):
        self.roll_axis = self.roll_axis / np.linalg.norm(self.roll_axis)
        rot_matrix = Rotation.from_rotvec(np.deg2rad(angle) * self.roll_axis)
        self.pitch_axis = rot_matrix.apply(self.pitch_axis)
        self.yaw_axis = rot_matrix.apply(self.yaw_axis)
        self.update_draw()

    def pitch(self, angle):
        self.pitch_axis = self.pitch_axis / np.linalg.norm(self.pitch_axis)
        rot_matrix = Rotation.from_rotvec(np.deg2rad(angle) * self.pitch_axis)
        self.roll_axis = rot_matrix.apply(self.roll_axis)
        self.yaw_axis = rot_matrix.apply(self.yaw_axis)
        self.update_draw()

    def yaw(self, angle):
        self.yaw_axis = self.yaw_axis / np.linalg.norm(self.yaw_axis)
        rot_matrix = Rotation.from_rotvec(np.deg2rad(angle) * self.yaw_axis)
        self.roll_axis = rot_matrix.apply(self.roll_axis)
        self.pitch_axis = rot_matrix.apply(self.pitch_axis)
        self.update_draw()

    def reset(self):
        self.xyz = np.array([0., 0., 0.])
        self.roll_axis = np.array([1., 0., 0.])
        self.pitch_axis = np.array([0., 1., 0.])
        self.yaw_axis = np.array([0., 0., 1.])

        self.x_path = []
        self.y_path = []
        self.z_path = []

        self.update_draw()

    def update_draw(self):
        self.body_vertices = [[self.pitch_axis * -10. + self.xyz,
                               self.roll_axis * 10. + self.xyz,
                               self.pitch_axis * 10. + self.xyz]]
        self.body.set_verts(self.body_vertices)

        self.path.set_xdata(np.array(self.x_path, dtype=np.float64))
        self.path.set_ydata(np.array(self.y_path, dtype=np.float64))
        self.path.set_3d_properties(np.array(self.z_path, dtype=np.float64))


def create_center_lines():
    line_axis_x = art3d.Line3D([0., 0.], [0., 0.], [z_min, z_max], color="gray", ls="-.", linewidth=1)
    ax0.add_line(line_axis_x)
    line_axis_y = art3d.Line3D([x_min, x_max], [0., 0.], [0., 0.], color="gray", ls="-.", linewidth=1)
    ax0.add_line(line_axis_y)
    line_axis_z = art3d.Line3D([0., 0.], [y_min, y_max], [0., 0.], color="gray", ls="-.", linewidth=1)
    ax0.add_line(line_axis_z)


def draw_static_diagrams():
    create_center_lines()


def reset():
    global is_play, is_run, command_counter
    # is_play = False
    is_run = False
    command_counter = 0
    cnt.reset()
    turtle.reset()


def execute_file(filename):
    global commands, expanded_commands, is_run, command_counter
    commands = read_commands_from_file(filename)
    expanded_commands = expand_commands(commands)
    command_counter = 0
    cnt.reset()
    is_run = True


def create_animation_control():
    frm_anim = ttk.Labelframe(root, relief="ridge", text="Animation", labelanchor="n")
    frm_anim.pack(side="left", fill=tk.Y)
    # btn_play = tk.Button(frm_anim, text="Play/Pause", command=switch)
    # btn_play.pack(side="left")
    btn_reset = tk.Button(frm_anim, text="Reset", command=reset)
    btn_reset.pack(side="left")


def create_file_name_setter():
    frm_fn = ttk.Labelframe(root, relief="ridge", text="File name", labelanchor="n")
    frm_fn.pack(side='left')
    ent_fn = tk.Entry(frm_fn)
    ent_fn.pack(side='left')
    btn_run = tk.Button(frm_fn, text="Run", command=lambda: execute_file(ent_fn.get()))
    btn_run.pack(side='left')


def parse_command_line(line):
    tokens = line.split()
    cmd = tokens[0].lower()
    if cmd == "repeat":
        count = int(tokens[1])
        return (cmd, count, [])
    elif cmd == "set":
        if len(tokens) != 3:
            raise ValueError("Invalid SET command format")
        var_name = tokens[1]
        value = int(tokens[2])
        return (cmd, var_name, value)
    else:
        if len(tokens) > 1:
            value = tokens[1]
            # Treat as a number or variable name.
            try:
                value = int(value)
            except ValueError:
                value = variables.get(value, value)
            return (cmd, value)
        else:
            return (cmd, )


def read_commands_from_file(filename):
    global commands
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

        commands = []
        stack = []
        for line in lines:
            line = line.strip()
            if line.startswith("repeat"):
                cmd, count, sub_commands = parse_command_line(line)
                stack.append((commands, count))
                commands = []
            elif line == "[":
                pass  # Start sub commands
            elif line == "]":
                if stack:
                    parent_commands, count = stack.pop()
                    parent_commands.append(("repeat", count, commands))
                    commands = parent_commands
            else:
                cmd_value = parse_command_line(line)
                commands.append(cmd_value)
        return commands
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []
    except Exception as e:
        print(f"Error while processing file: {e}")
        return []


def expand_commands(commands):
    expanded = []
    for command in commands:
        if command[0] == "repeat":
            count, sub_commands = command[1], command[2]
            if count <= 0:
                continue  # Ignore
            for _ in range(count):
                expanded.extend(expand_commands(sub_commands))
        else:
            expanded.append(command)
    return expanded


def replace_variables(command):
    # Replace command value
    if command[0] == "set":
        return command  # Return the SET command as is."
    if len(command) > 1:
        cmd, value = command
        if isinstance(value, str):
            value = variables.get(value, value)
            if isinstance(value, str):
                raise ValueError(f"Undefined variable: {value}")
        return (cmd, value)
    return command


def update(frame):
    global command_counter, expanded_commands, variables, commands
    if not is_run:
        return
    if command_counter < len(expanded_commands):
        command_data = expanded_commands[command_counter]
        command_data = replace_variables(command_data)
        command = command_data[0]

        if command == "forward":
            turtle.forward_step(command_data[1])
            print("forward", command_data[1])
        elif command == "right":
            turtle.right(command_data[1])
            print("right", command_data[1])
        elif command == "left":
            turtle.left(command_data[1])
            print("left", command_data[1])
        elif command == "penup":
            turtle.penup()
            print("penup")
        elif command == "pendown":
            turtle.pendown()
            print("pendown")
        elif command == "set":
            var_name, value = command_data[1], command_data[2]
            variables[var_name] = value
            print(f"set {var_name} = {value}")
        elif command == "up":
            turtle.up(command_data[1])
            print("up", command_data[1])
        elif command == "down":
            turtle.down(command_data[1])
            print("up", command_data[1])
        elif command == "roll_cw":
            turtle.roll_cw(command_data[1])
            print("roll_cw", command_data[1])
        elif command == "roll_ccw":
            turtle.roll_ccw(command_data[1])
            print("roll_ccw", command_data[1])

        command_counter += 1
        cnt.count_up()


""" main loop """
if __name__ == "__main__":
    cnt = Counter(ax=ax0, is3d=True, xy=np.array([x_min, y_max]),z=z_max, label="Step=")
    create_animation_control()
    create_file_name_setter()
    draw_static_diagrams()

    # commands = read_commands_from_file('commands.txt')
    # expanded_commands = expand_commands(commands)

    turtle = Turtle3d(ax=ax0, xyz=np.array([0., 0., 0.]), direction=0., size=size_turtle, color="green")
    turtle.pendown()

    anim = animation.FuncAnimation(fig, update, interval=10, save_count=100)
    root.mainloop()
