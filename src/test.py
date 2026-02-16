import tkinter as tk
# File belajar tkiner testing
root = tk.Tk()
canvas = tk.Canvas(root, width=200, height=100, bg="white")
canvas.pack()

canvas.create_text(100, 50, text="Hello Tkinter", anchor=tk.W)

root.mainloop()
