import curses

class BaseElement:
    def __init__(self, x, y, width, height, parent=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.children = []
        self.parent = parent
        # The screen will be initialized when the element is added to a parent
        self.screen = None 

    def add_child(self, child):
        self.children.append(child)
        child.parent = self
        # Initialize the child's screen as a sub-window of the parent's screen
        if self.screen:
            child.screen = self.screen.subwin(child.height, child.width, child.y, child.x)
        child.on_add()

    def on_add(self):
        # This method will be called when the element is added to a parent
        # It can be overridden by subclasses to perform additional actions upon being added to a parent
        pass

    def set_focus(self, focus):
        self.has_focus = focus

    def on_event(self, event, callback):
        self.event_callbacks[event] = callback

    def trigger_event(self, event, *args, **kwargs):
        if event in self.event_callbacks:
            self.event_callbacks[event](*args, **kwargs)

    def render(self):
        # This method will be overridden in subclasses to handle drawing
        pass

    def update(self):
        # This method can be overridden to update the element's state if needed
        pass



class Div(BaseElement):
    def __init__(self, x, y, width, height, parent=None):
        super().__init__(x, y, parent)
        self.width = width
        self.height = height
        # Initialize border characters to None, which represents default border characters
        self.border_chars = None

    def set_border_style(self, ls='|', rs='|', ts='-', bs='-', tl='+', tr='+', bl='+', br='+'):
        self.border_chars = (ls, rs, ts, bs, tl, tr, bl, br)

    def render(self):
        if self.border_chars:
            self.screen.border(*self.border_chars)
        else:
            self.screen.border()

        # Render children
        for child in self.children:
            child.render()

    def update(self):
        # Update the div's state and its children's state
        for child in self.children:
            child.update()



class Root(Div):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Root, cls).__new__(cls)
            cls._is_initialized = False
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            # Initialize curses and set up the screen
            self.stdscr = curses.initscr()
            self.screen = self.stdscr  # For Root, screen is stdscr
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            height, width = self.stdscr.getmaxyx()
            super().__init__(0, 0, width, height)
            self._is_initialized = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # End the curses application
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()


# Usage example
with Root() as root:

    div = Div(0, 0, 20, 10)

    root.add_child(div)
    

    # Your application logic here
    while True:
        root.update()
