from tkinter import *
from tkvideo import tkvideo

w = Tk()
w.title("Video Player")


lblVideo = Label(w)
lblVideo.pack()

player = tkvideo("peaceful.mp4",
                 lblVideo,
                 loop=1,
                 size=(700,500))

player.play()

w.mainloop()
