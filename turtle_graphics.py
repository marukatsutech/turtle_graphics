""" Turtle graphics

Sample:
set x 100
set y 150
penup
left 90
forward 50
right 165
pendown
repeat 12 [
    forward x
    right y
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
is_play = False

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

    def right(self, angle_deg):
        self.direction -= Decimal(np.deg2rad(float(angle_deg)))
        self.update_draw()

    def left(self, angle_deg):
        self.direction += Decimal(np.deg2rad(float(angle_deg)))
        self.update_draw()

    def reset(self):
        self.direction = Decimal(np.deg2rad(float(0.)))
        self.xy = np.array([0., 0.], dtype=np.float64)
        self.x_path = []
        self.y_path = []
        self.update_draw()


class TurtleInterpreter:
    def __init__(self):
        self.variables = {}

    def execute_file(self, filename):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
                block = None
                repeat_count = 0
                for line in lines:
                    line = line.strip()
                    if line:
                        if line.startswith("repeat"):
                            tokens = self.tokenize(line)
                            repeat_count = int(tokens[1])
                            block = []
                        elif line == "[":
                            # No action needed, start collecting block
                            pass
                        elif line == "]":
                            if block is not None:
                                self.execute(("repeat", [repeat_count]), block=block)
                                block = None
                        elif block is not None:
                            block.append(line)
                        else:
                            tokens = self.tokenize(line)
                            parsed = self.parse(tokens)
                            self.execute(parsed)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except Exception as e:
            print(f"Error while processing file: {e}")

    def tokenize(self, command):
        return command.split()

    def parse(self, tokens):
        if not tokens:
            return None
        cmd = tokens[0]
        args = tokens[1:]
        return cmd, args

    def resolve_variable(self, value):
        try:
            if value in self.variables:
                return self.variables[value]
            return float(value)
        except ValueError:
            raise ValueError(f"Invalid value: {value}")

    def execute(self, parsed, block=None):
        if parsed is None:
            return

        cmd, args = parsed

        if cmd == "penup":
            my_turtle.penup()
            print("penup")

        elif cmd == "pendown":
            my_turtle.pendown()
            print("pendown")

        elif cmd == "forward" and len(args) == 1:
            try:
                my_turtle.forward(self.resolve_variable(args[0]))
                print(f"forward: {self.resolve_variable(args[0])}")
            except ValueError:
                print("Error: Invalid numbers")

        elif cmd == "right" and len(args) == 1:
            try:
                my_turtle.right(self.resolve_variable(args[0]))
                print(f"right: {self.resolve_variable(args[0])}")
            except ValueError:
                print("Error: Invalid numbers")

        elif cmd == "left" and len(args) == 1:
            try:
                my_turtle.left(self.resolve_variable(args[0]))
                print(f"left: {self.resolve_variable(args[0])}")
            except ValueError:
                print("Error: Invalid numbers")

        elif cmd == "set" and len(args) == 2:
            var_name = args[0]
            value = self.resolve_variable(args[1])
            self.variables[var_name] = value
            print(f"'{var_name}' = {value}")

        elif cmd == "print" and len(args) == 1:
            try:
                value = self.resolve_variable(args[0])
                print(f"Value: {value}")
            except KeyError:
                print(f"Error: Variable '{args[0]}' not found")

        elif cmd == "repeat" and len(args) == 1:
            repeat_count = int(args[0])
            for _ in range(repeat_count):
                for sub_command in block:
                    tokens = self.tokenize(sub_command)
                    parsed = self.parse(tokens)
                    self.execute(parsed)

        elif cmd == "exit":
            print("Exiting...")
            exit()

        else:
            print(f"Unknown command: {cmd}")


def execute_file(filename):
    interpreter.execute_file(filename)


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


def create_parameter_setter():
    pass


def draw_static_diagrams():
    pass


def update_diagrams():
    pass


def reset():
    global is_play
    is_play = False
    # cnt.reset()
    my_turtle.reset()


def switch():
    global is_play
    is_play = not is_play


def update(f):
    if is_play:
        # cnt.count_up()
        update_diagrams()


""" main loop """
if __name__ == "__main__":
    # cnt = Counter(ax=ax0, is3d=False, xy=np.array([x_min, y_max]), label="Step=")
    draw_static_diagrams()

    create_animation_control()
    create_parameter_setter()
    create_file_name_setter()

    my_turtle = Turtle(ax=ax0, xy=np.array([0, 0]), direction=0, size=size_turtle, color="green")
    interpreter = TurtleInterpreter()

    anim = animation.FuncAnimation(fig, update, interval=100, save_count=100)
    root.mainloop()
