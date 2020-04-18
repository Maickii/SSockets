import curses
from time import sleep
import threading
import queue
import random
import sys
import os

prompt = '[Ctrl-C to exit] Enter a message: '
q = queue.Queue()

def main(stdscr, functions=None):
	curses.use_default_colors()
	curses.echo()
	body, in_box, winy, winx = init_boxes(stdscr)
	init_threads(in_box, functions)
	try:
		main_body_loop(body, winy, winx)
	except KeyboardInterrupt:
		close_curses_and_exit(stdscr)

def setup_borders(box):
	box.border()
	box.refresh()

def create_input_box(winy, winx):
	begin_x = 0; begin_y = winy - 1
	height = 1; width = winx
	win = curses.newwin(height, width, begin_y, begin_x)
	win.addstr(0, 0, prompt)
	win.refresh()
	return win

def create_body_box(winy, winx):
	begin_x = 0; begin_y = 0
	height = winy-1; width = winx
	bod = curses.newwin(height, width, begin_y, begin_x)
	bod.refresh()
	return bod

def clear_prompt(win):
	win.clear()
	win.addstr(0, 0, prompt)
	win.refresh()

def get_input(in_box):
	curses.echo()
	global q
	while True:
		val = in_box.getstr(0, len(prompt))
		clear_prompt(in_box)
		q.put((False, val))

def get_input_from_other_person():
	global q
	while True:
		val = str(random.random())
		q.put((True, val))
		sleep(2)

def init_boxes(stdscr):
	winy, winx = stdscr.getmaxyx()
	body = create_body_box(winy, winx)
	setup_borders(body)
	in_box = create_input_box(winy, winx)
	curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_WHITE)
	curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_WHITE)
	return body, in_box, winy, winx

def init_threads(in_box, functions=None):
	if functions == None:
		prompt_thread = threading.Thread(target=get_input, args=(in_box,)).start()
		sender_thread = threading.Thread(target=get_input_from_other_person).start()
	elif type(functions) is tuple:
		try:
			prompt_thread = threading.Thread(target=functions[0], args=(in_box,)).start()
			sender_thread = threading.Thread(target=functions[1]).start()
		except:
			raise ValueError("One of the functions passed could not be started as a thread")
	else:
		raise ValueError("functions must be a tuple of the two thread functions to run, or None for default behaviour")

def main_body_loop(body, winy, winx):
	i = 0
	curses.curs_set(0)
	while True:
		data = q.get()
		if ((i%(winy-3))) == 0:
			body.clear()
			setup_borders(body)
		if data[0]:
			body.addstr((i%(winy-3))+1, 1, data[1], curses.color_pair(1))
		else:
			body.addstr((i%(winy-3))+1, winx-len(data[1])-1, data[1], curses.color_pair(2))
		setup_borders(body)
		body.refresh()
		i = i + 1

def close_curses_and_exit(stdscr):
	curses.nocbreak()
	stdscr.keypad(0)
	curses.echo()
	curses.endwin()
	os._exit(0)

#if __name__ == "__main__":
#def call_main(functions):

def init(callback, functions=None):
	threading.Thread(target=callback).start()
	curses.wrapper(main, functions)
