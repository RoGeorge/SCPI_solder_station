__author__ = 'RoGeorge'

from Tkinter import *
import turtle

# t1 = turtle.Turtle()
# # turtle.Canvas()
# t1.down()
# t1.forward(100)

root = Tk()
root.wm_title("Crazy Solder Station")


l1_text = StringVar()
l1 = Label(root, textvariable=l1_text)
# l1["width"] = 100
# l1.pack()
l1.grid(row=0, column=0, columnspan=2)
l1_text.set("Temp *C")

l2_text = StringVar()
l2 = Label(root, textvariable=l2_text)
l2.grid(row=1, column=1)
l2_text.set("*C")


tb1_val = IntVar()
tb1 = Entry(root, textvariable=tb1_val, justify="right")
tb1["width"] = 5
tb1.grid(row=1, column=0)
# tb1.grid(row=2, column=1)
tb1_val.set(250)

def b1_press():
	tb1_val.set(tb1_val.get() - 10)

def b2_press():
	tb1_val.set(tb1_val.get() + 10)

b1 = Button(root, text="DOWN", command=b1_press)
b1["width"] = 5
# b1.pack(side="left")
b1.grid(row=2, column=0)

b2 = Button(root, text="UP", command=b2_press)
b2["width"] = 5
# b2.pack()
b2.grid(row=2, column=1)

def b3_press():
	# tb1_val.set(l2_text.get())
	if l2_text.get() == "*F":
		l1_text.set("Temp *C")
		l2_text.set("*C")
		tb1_val.set(int((tb1_val.get() - 32) * 5 / 9.0))

def b4_press():
	if l2_text.get() == "*C":
		l1_text.set("Temp *F")
		l2_text.set("*F")
		tb1_val.set(int(tb1_val.get() * 9 / 5.0 + 32))

b3 = Button(root, text="*C", command=b3_press)
b3["width"] = 5
# b3.pack(side="left")
b3.grid(row=3, column=0)

b4 = Button(root, text="*F", command=b4_press)
b4["width"] = 5
# b4.pack()
b4.grid(row=3, column=1)


# f1 = Frame(root, bg='gray', width=200, height=200)
f1 = Frame(root, width=200, height=200)
# c1 = Canvas(f1, width=100, height=100)
c1 = Canvas(f1, width=150, height=150)
c1.grid(row=1, column=2, rowspan=3)
f1.grid(row=1, column=2, rowspan=3)

t1 = turtle.RawTurtle(c1)
t1.hideturtle()
t1.pendown()
t1.forward(20)
# root.deiconify()

root.mainloop()
