import curses
from collections import deque
import sys
import json


class View:

    def __init__(self, graph):
        self.stack = deque()
        self.stack.append(graph)
    
    @property
    def current(self):
        return self.stack[-1]

    def current_view(self):
        return [ item["name"] for item in self.current ]
    
    def descend(self, index) -> "View":
        if self.current[index]["children"]:
            
            self.stack.append(self.current[index]["children"])
        return self
    
    def ascend(self) -> "View":
        if len(self.stack) == 1:
            return self
        self.stack.pop()
        return self

    def child_view(self, index):
        if self.current[index]["children"]:
            return [ item["name"] for item in self.current[index]["children"] ]
        else:
            elt = self.current[index]
            filename = elt["path"]
            with open(filename) as fp:
                line_no = elt["line"] - 1
                return fp.readlines()[line_no:]

     
    def parent_view(self):
        if len(self.stack) == 1:
            return []
        return [item["name"] for item in self.stack[-2]]
    

        

class App:

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_pos = 0
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # For highlighting

        max_y, max_x = self.stdscr.getmaxyx()
        
        # Calculate widths for the three panels
        panel_width = max_x // 3
        panel_a_x = 0  # Panel A starts at the left edge
        panel_b_x = panel_width  # Panel B starts where Panel A ends
        panel_c_x = 2 * panel_width  # Panel C starts where Panel B ends
        # Divide the screen into three panels
        # Panel A and B are on the left, split horizontally
        # Panel C is on the right
        mid_x = max_x // 2
        mid_y = max_y // 2

        self.panel_a = curses.newwin(max_y, panel_width, 0, panel_a_x)
        self.panel_b = curses.newwin(max_y, panel_width, 0, panel_b_x)
        self.panel_c = curses.newwin(max_y, max_x - 2 * panel_width, 0, panel_c_x)  # Ensure Panel C fills the rest

    def render(self, parent_content: list[str], current_content: list[str], file_content: str) -> None:
        self.panel_a.clear()
        self.panel_b.clear()
        self.panel_c.clear()

        # Fill in the content for Panel A
        self.fill_panel(self.panel_a, parent_content)

        # Fill in the content for Panel B, with highlighting
        self.fill_panel(self.panel_b, current_content, highlight_index=self.current_pos)

        # Fill in the content for Panel C
        self.fill_panel(self.panel_c, file_content, is_string=True)

        # Refresh panels to update the screen
        self.panel_a.refresh()
        self.panel_b.refresh()
        self.panel_c.refresh()

    def fill_panel(self, panel, content, highlight_index=None, is_string=False):
        for idx, line in enumerate(content):
            if highlight_index == idx and not is_string:
                panel.addstr(1 + idx, 1, line, curses.color_pair(1))
            else:
                try:
                    panel.addstr(1 + idx, 1, line)
                except: # Happens when we overflow on Y direction
                    break
        panel.box()

# Main function to start the curses application
def main(stdscr):
    
    with open(sys.argv[1]) as fp:
        graph = json.load(fp)
    
    view = View(graph)
    app = App(stdscr)
    # Example usage with dummy content
   

    while True:
        current_content = view.current_view()
        char = stdscr.getch()
        if char == curses.KEY_UP and len(current_content):
            app.current_pos = (app.current_pos - 1) % len(current_content)
        elif char == curses.KEY_DOWN:
            app.current_pos = (app.current_pos + 1) % len(current_content)
        elif char == ord("\n"):
            view.descend(app.current_pos)
            app.current_pos = 0
        elif char == 27: # ESCAPE
            view.ascend()
            app.current_pos = 0
  
        app.render(view.parent_view(), view.current_view(), view.child_view(app.current_pos))

# Run the curses application
if __name__ == "__main__":


    curses.wrapper(main)