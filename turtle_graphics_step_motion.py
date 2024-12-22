""" Turtle graphics step motion

Sample:
set distance 25
set angle 45
repeat 8 [
    pendown
    forward distance
    penup
    forward 10
    right angle
]
"""

from matplotlib.figure import Figure
import matplotlib.animation as animation
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_toolkits.mplot3d import proj3d

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

""" Create figure and axes """
title_ax0 = "Turtle graphics"
title_tk = title_ax0

x_min = -100.
x_max = 100.
y_min = -100.
y_max = 100.

fig = Figure()
ax0 = fig.add_subplot(111)
ax0.set_aspect("equal")
ax0.set_xticks(np.arange(x_min, x_max, 10.))
ax0.set_yticks(np.arange(y_min, y_max, 10.))
ax0.grid()
ax0.set_title(title_ax0)
ax0.set_xlabel("x")
ax0.set_ylabel("y")
ax0.set_xlim(x_min, x_max)
ax0.set_ylim(y_min, y_max)

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


class Turtle:
    def __init__(self, ax=None, xy=None, direction=None, size=None, color=None):
        self.ax = ax
        self.xy = np.array(xy, dtype=np.float64)
        self.direction = Decimal(direction)
        self.size = size
        self.color = color

        self.x_body, self.y_body = self.points_polygon(6, self.size, self.xy, self.direction)
        self.body, = self.ax.fill(self.x_body, self.y_body, "-", color=self.color)

        self.xy_head = self.xy + self.size * np.array([np.cos(float(self.direction)), np.sin(float(self.direction))], dtype=np.float64)
        self.x_head, self.y_head = self.points_polygon(4, self.size * 0.4, self.xy_head, self.direction)
        self.head, = self.ax.fill(self.x_head, self.y_head, "-", color=self.color)

        self.xy_arm_right = self.xy + self.size * np.array([np.cos(float(self.direction) - np.pi / 3), np.sin(float(self.direction) - np.pi / 3)], dtype=np.float64)
        self.x_arm_right, self.y_arm_right = self.points_polygon(4, self.size * 0.2, self.xy_arm_right, self.direction)
        self.arm_right, = self.ax.fill(self.x_arm_right, self.y_arm_right, "-", color=self.color)

        self.xy_arm_left = self.xy + self.size * np.array([np.cos(float(self.direction) + np.pi / 3), np.sin(float(self.direction) + np.pi / 3)], dtype=np.float64)
        self.x_arm_left, self.y_arm_left = self.points_polygon(4, self.size * 0.2, self.xy_arm_left, self.direction)
        self.arm_left, = self.ax.fill(self.x_arm_left, self.y_arm_left, "-", color=self.color)

        self.xy_leg_right = self.xy + self.size * np.array([np.cos(float(self.direction) - 2 * np.pi / 3), np.sin(float(self.direction) - 2 * np.pi / 3)], dtype=np.float64)
        self.x_leg_right, self.y_leg_right = self.points_polygon(4, self.size * 0.2, self.xy_leg_right, self.direction)
        self.leg_right, = self.ax.fill(self.x_leg_right, self.y_leg_right, "-", color=self.color)

        self.xy_leg_left = self.xy + self.size * np.array([np.cos(float(self.direction) + 2 * np.pi / 3), np.sin(float(self.direction) + 2 * np.pi / 3)], dtype=np.float64)
        self.x_leg_left, self.y_leg_left = self.points_polygon(4, self.size * 0.2, self.xy_leg_left, self.direction)
        self.leg_left, = self.ax.fill(self.x_leg_left, self.y_leg_left, "-", color=self.color)

        self.x_path = []
        self.y_path = []
        self.path, = self.ax.plot(np.array(self.x_path, dtype=np.float64), np.array(self.y_path, dtype=np.float64))

        self.is_pen_down = False

    def points_polygon(self, num_sides, radius, xy, direction):
        theta = np.linspace(0, 2 * np.pi, num_sides + 1, dtype=np.float64)
        x = radius * np.cos(theta + float(direction)) + xy[0]
        y = radius * np.sin(theta + float(direction)) + xy[1]
        return x, y

    def update_draw(self):
        self.x_body, self.y_body = self.points_polygon(6, self.size, self.xy, self.direction)
        self.body.set_xy(np.column_stack((self.x_body, self.y_body)))

        self.xy_head = self.xy + self.size * np.array([np.cos(float(self.direction)), np.sin(float(self.direction))], dtype=np.float64)
        self.x_head, self.y_head = self.points_polygon(4, self.size * 0.4, self.xy_head, self.direction)
        self.head.set_xy(np.column_stack((self.x_head, self.y_head)))

        self.xy_arm_right = self.xy + self.size * np.array([np.cos(float(self.direction) - np.pi / 3), np.sin(float(self.direction) - np.pi / 3)], dtype=np.float64)
        self.x_arm_right, self.y_arm_right = self.points_polygon(4, self.size * 0.2, self.xy_arm_right, self.direction)
        self.arm_right.set_xy(np.column_stack((self.x_arm_right, self.y_arm_right)))

        self.xy_arm_left = self.xy + self.size * np.array([np.cos(float(self.direction) + np.pi / 3), np.sin(float(self.direction) + np.pi / 3)], dtype=np.float64)
        self.x_arm_left, self.y_arm_left = self.points_polygon(4, self.size * 0.2, self.xy_arm_left, self.direction)
        self.arm_left.set_xy(np.column_stack((self.x_arm_left, self.y_arm_left)))

        self.xy_leg_right = self.xy + self.size * np.array([np.cos(float(self.direction) - 2 * np.pi / 3), np.sin(float(self.direction) - 2 * np.pi / 3)], dtype=np.float64)
        self.x_leg_right, self.y_leg_right = self.points_polygon(4, self.size * 0.2, self.xy_leg_right, self.direction)
        self.leg_right.set_xy(np.column_stack((self.x_leg_right, self.y_leg_right)))

        self.xy_leg_left = self.xy + self.size * np.array([np.cos(float(self.direction) + 2 * np.pi / 3), np.sin(float(self.direction) + 2 * np.pi / 3)], dtype=np.float64)
        self.x_leg_left, self.y_leg_left = self.points_polygon(4, self.size * 0.2, self.xy_leg_left, self.direction)
        self.leg_left.set_xy(np.column_stack((self.x_leg_left, self.y_leg_left)))

        self.path.set_data(np.array(self.x_path, dtype=np.float64), np.array(self.y_path, dtype=np.float64))

    def pendown(self):
        self.is_pen_down = True
        self.x_path.append(self.xy[0])
        self.y_path.append(self.xy[1])

    def penup(self):
        self.is_pen_down = False

    def forward(self, distance):
        self.xy += float(distance) * np.array([np.cos(float(self.direction)), np.sin(float(self.direction))], dtype=np.float64)

        if self.is_pen_down:
            self.x_path.append(self.xy[0])
            self.y_path.append(self.xy[1])
        else:
            self.x_path.append(None)
            self.y_path.append(None)

        self.update_draw()

    def forward_step(self, distance):
        print(f"forward {distance}")
        d = 0
        step = 0.2
        while d + step <= distance:
            self.xy += float(step) * np.array([np.cos(float(self.direction)), np.sin(float(self.direction))],
                                              dtype=np.float64)

            if self.is_pen_down:
                self.x_path.append(self.xy[0])
                self.y_path.append(self.xy[1])
            else:
                self.x_path.append(None)
                self.y_path.append(None)

            self.update_draw()
            d += step

        remaining_distance = distance - d
        if remaining_distance > 0:
            self.xy += float(remaining_distance) * np.array(
                [np.cos(float(self.direction)), np.sin(float(self.direction))], dtype=np.float64)

            if self.is_pen_down:
                self.x_path.append(self.xy[0])
                self.y_path.append(self.xy[1])
            else:
                self.x_path.append(None)
                self.y_path.append(None)

            self.update_draw()

    def right(self, angle_deg):
        print(f"right {angle_deg}")
        self.direction -= Decimal(np.deg2rad(float(angle_deg)))
        self.update_draw()

    def left(self, angle_deg):
        print(f"left {angle_deg}")
        self.direction += Decimal(np.deg2rad(float(angle_deg)))
        self.update_draw()

    def reset(self):
        self.direction = Decimal(np.deg2rad(float(0.)))
        self.xy = np.array([0., 0.], dtype=np.float64)
        self.x_path = []
        self.y_path = []
        self.update_draw()


def reset():
    global is_play, is_run, command_counter
    # is_play = False
    is_run = False
    command_counter = 0
    cnt.reset()
    turtle.reset()


def execute_file(filename):
    global commands, expanded_commands, is_run, is_play, command_counter
    commands = read_commands_from_file(filename)
    expanded_commands = expand_commands(commands)
    command_counter = 0
    cnt.reset()
    is_play = True
    is_run = True


def create_animation_control():
    frm_anim = ttk.Labelframe(root, relief="ridge", text="Animation", labelanchor="n")
    frm_anim.pack(side="left", fill=tk.Y)
    btn_play = tk.Button(frm_anim, text="Play/Pause", command=switch)
    btn_play.pack(side="left")
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


def switch():
    global is_play
    is_play = not is_play


def update(frame):
    global command_counter, expanded_commands, variables, commands
    if not is_play:
        return
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

        command_counter += 1
        cnt.count_up()


""" main loop """
if __name__ == "__main__":
    cnt = Counter(ax=ax0, is3d=False, xy=np.array([x_min, y_max]), label="Step=")
    create_animation_control()
    create_file_name_setter()

    # commands = read_commands_from_file('commands.txt')
    # expanded_commands = expand_commands(commands)

    turtle = Turtle(ax=ax0, xy=np.array([0, 0]), direction=0, size=size_turtle, color="green")

    anim = animation.FuncAnimation(fig, update, interval=100, save_count=100)
    root.mainloop()
