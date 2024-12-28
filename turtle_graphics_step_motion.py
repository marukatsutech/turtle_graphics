""" Turtle graphics

Sample of commands
set times_a 30
set times_b 4
set length 10
set angle 90
set angle_step 20
set length_step 3
pendown
repeat times_a [
    repeat times_b [
        forward length
        right angle
    ]
    right angle_step
    add length length_step
]
"""

import numpy as np
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import tkinter as tk
from tkinter import ttk
from mpl_toolkits.mplot3d import proj3d

from decimal import Decimal, getcontext
getcontext().prec = 50

""" Global variables """
size_turtle = 5

""" Animation control """
is_play = True
is_run = False

""" Axis vectors """
vector_x_axis = np.array([1., 0., 0.])
vector_y_axis = np.array([0., 1., 0.])
vector_z_axis = np.array([0., 0., 1.])

""" Other parameters """
theta_init_deg, phi_init_deg = 0., 0.
rot_velocity_x, rot_velocity_y, rot_velocity_z = 1., 1., 1.

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

""" Global objects of Tkinter """

""" Classes and functions """


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
        self.pendown()

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
        print("pendown")
        self.is_pen_down = True
        self.x_path.append(self.xy[0])
        self.y_path.append(self.xy[1])

        self.body.set_facecolor(self.color)
        self.body.set_edgecolor(self.color)
        self.head.set_facecolor(self.color)
        self.head.set_edgecolor(self.color)
        self.arm_right.set_facecolor(self.color)
        self.arm_right.set_edgecolor(self.color)
        self.arm_left.set_facecolor(self.color)
        self.arm_left.set_edgecolor(self.color)
        self.leg_right.set_facecolor(self.color)
        self.leg_right.set_edgecolor(self.color)
        self.leg_left.set_facecolor(self.color)
        self.leg_left.set_edgecolor(self.color)
        self.update_draw()

    def penup(self):
        print("penup")
        self.is_pen_down = False

        self.body.set_facecolor("gray")
        self.body.set_edgecolor("gray")
        self.head.set_facecolor("gray")
        self.head.set_edgecolor("gray")
        self.arm_right.set_facecolor("gray")
        self.arm_right.set_edgecolor("gray")
        self.arm_left.set_facecolor("gray")
        self.arm_left.set_edgecolor("gray")
        self.leg_right.set_facecolor("gray")
        self.leg_right.set_edgecolor("gray")
        self.leg_left.set_facecolor("gray")
        self.leg_left.set_edgecolor("gray")
        self.update_draw()

    def forward(self, distance):
        print(f"forward {distance}")
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


class Interpreter:
    def __init__(self):
        self.variables = {}  # Global variables
        self.commands = []   # Commands
        self.pc = 0          # Program counter
        self.context_stack = []  # State management stack for repeat blocks

    def set_variable(self, name, value):
        self.variables[name] = int(value)
        print(f"Set variable {name} = {value}")

    def get_variable(self, name):
        if name not in self.variables:
            raise NameError(f"Variable '{name}' is not defined")
        return self.variables[name]

    def get_value(self, value):
        """Determine if the input is a variable name or a literal number and return its value."""
        if value.isdigit():
            return int(value)  # Return the integer if it's a number
        elif value in self.variables:
            return self.get_variable(value)  # Return the value of the variable
        else:
            raise ValueError(f"Invalid value or undefined variable: '{value}'")

    def execute_command(self, command, *args):
        """ Execute commands """
        if command == "set":
            self.set_variable(args[0], args[1])
            print(f"set {args[0]} {args[1]}")
        elif command == "penup":
            print(f"penup")
            my_turtle.penup()
        elif command == "pendown":
            print(f"pendown")
            my_turtle.pendown()
        elif command == "forward":
            steps = self.get_value(args[0])
            print(f"forward {steps}")
            my_turtle.forward_step(steps)
        elif command == "right":
            angle = self.get_value(args[0])
            print(f"right {angle}")
            my_turtle.right(angle)
        elif command == "left":
            angle = self.get_value(args[0])
            print(f"left {angle}")
            my_turtle.left(angle)
        elif command == "add":
            var_name = args[0]
            increment = self.get_value(args[1])
            self.variables[var_name] += increment
            print(f"add {var_name} {increment}")
        elif command == "repeat":
            count = self.get_value(args[0])
            block_commands = args[1]
            self.context_stack.append({
                "commands": block_commands,
                "count": count,
                "iteration": 0,
                "index": 0
            })
            print(f"repeat {count}")
        elif command == "reset":
            print(f"reset")
            my_turtle.reset()
        else:
            print(f"Unknown command: {command}")

    def step(self):
        if self.context_stack:
            # Process the current context
            current_context = self.context_stack[-1]
            commands = current_context["commands"]
            index = current_context["index"]
            iteration = current_context["iteration"]
            count = current_context["count"]

            if index < len(commands):
                # Execute commands in current block
                command, *args = commands[index]
                self.execute_command(command, *args)
                current_context["index"] += 1
            else:
                # Continue repeat block
                current_context["iteration"] += 1
                if current_context["iteration"] < count:
                    current_context["index"] = 0
                    print(f"Repeat iteration {current_context['iteration']} of {count}")
                else:
                    # Finish repeat block
                    self.context_stack.pop()
                    print("End repeat block")
        elif self.pc < len(self.commands):
            # Execute global commands
            command, *args = self.commands[self.pc]
            self.pc += 1
            self.execute_command(command, *args)
        else:
            print("Program finished")
            return False  # Finish program
        return True  # Continue program

    def parse_block(self, lines, start_index):
        """ parse repeat block """
        commands = []
        i = start_index
        while i < len(lines):
            line = lines[i].strip()
            if line == "]":
                return commands, i
            parts = line.split()
            command = parts[0]
            if command == "repeat":
                block_var = parts[1]
                if parts[2] != "[":
                    raise SyntaxError("Repeat block must start with '['")
                nested_commands, new_index = self.parse_block(lines, i + 1)
                commands.append((command, block_var, nested_commands))
                i = new_index
            else:
                commands.append((command, *parts[1:]))
            i += 1
        raise SyntaxError("No closing ']' found for a repeat block")

    def load_program(self, lines):
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith("#"):
                i += 1
                continue

            parts = line.split()
            command = parts[0]
            if command == "repeat":
                block_var = parts[1]
                if parts[2] != "[":
                    raise SyntaxError("Repeat block must start with '['")
                block_commands, new_index = self.parse_block(lines, i + 1)
                self.commands.append((command, block_var, block_commands))
                i = new_index
            else:
                self.commands.append((command, *parts[1:]))
            i += 1

    def reset(self):
        self.pc = 0
        self.context_stack = []

    def clear(self):
        self.pc = 0
        self.context_stack = []
        self.commands = []


def execute_file(filename):
    global is_run, is_play
    interpreter.clear()
    try:
        with open(filename) as f:
            lines = f.readlines()
    except FileNotFoundError:
        pass
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error while processing file: {e}")

    interpreter.load_program(lines)
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


def create_manual_control():
    frm_man = ttk.Labelframe(root, relief="ridge", text="Manual control", labelanchor="n")
    frm_man.pack(side='left')

    btn_pu = tk.Button(frm_man, text="penup", command=lambda: my_turtle.penup())
    btn_pu.pack(side='left')

    btn_pd = tk.Button(frm_man, text="pendown", command=lambda: my_turtle.pendown())
    btn_pd.pack(side='left')

    var_fd = tk.StringVar(root)
    var_fd.set(str(1))
    btn_fd = tk.Button(frm_man, text="forward", command=lambda: my_turtle.forward(float(var_fd.get())))
    btn_fd.pack(side='left')
    spn_fd = tk.Spinbox(
        frm_man, textvariable=var_fd, format="%.0f", from_=1, to=100, increment=1, width=4
    )
    spn_fd.pack(side="left")

    var_rt = tk.StringVar(root)
    var_rt.set(str(1))
    btn_rt = tk.Button(frm_man, text="right", command=lambda: my_turtle.right(float(var_rt.get())))
    btn_rt.pack(side='left')
    spn_rt = tk.Spinbox(
        frm_man, textvariable=var_rt, format="%.0f", from_=1, to=360, increment=1, width=4
    )
    spn_rt.pack(side="left")

    var_lt = tk.StringVar(root)
    var_lt.set(str(1))
    btn_lt = tk.Button(frm_man, text="left", command=lambda: my_turtle.left(float(var_lt.get())))
    btn_lt.pack(side='left')
    spn_lt = tk.Spinbox(
        frm_man, textvariable=var_lt, format="%.0f", from_=1, to=360, increment=1, width=4
    )
    spn_lt.pack(side="left")


def reset():
    global is_play, is_run
    is_play = False
    is_run = False
    interpreter.reset()
    cnt.reset()
    my_turtle.reset()


def switch():
    global is_play
    is_play = not is_play


def update(f):
    global is_run
    if not is_play:
        return
    if not is_run:
        return
    cnt.count_up()
    if not interpreter.step():
        is_run = False


""" main loop """
if __name__ == "__main__":
    create_animation_control()
    create_file_name_setter()
    create_manual_control()
    cnt = Counter(ax=ax0, is3d=False, xy=np.array([x_min, y_max]), label="Step=")

    interpreter = Interpreter()
    my_turtle = Turtle(ax=ax0, xy=np.array([0, 0]), direction=0, size=size_turtle, color="green")

    anim = animation.FuncAnimation(fig, update, interval=100, save_count=100)
    root.mainloop()