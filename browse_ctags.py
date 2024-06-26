import curses
from collections import deque
import sys
import json
import subprocess

from typing import List

def editor(filename, line):
    return f"vim +{line} {filename}"

class View:

    def __init__(self, graph):
        self.stack = deque()
        self.stack.append(graph)

    def start_editor(self, index):
        path = self.current[index]["path"]
        line_no = self.current[index]["line"]
        command = editor(path, line_no)
        subprocess.call(command, shell=True)
        


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

        self.height = max_y
        self.max_x = max_x

        self.top_line = 0
        
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
        self.panel_a.clear()
        self.panel_b = curses.newwin(max_y, panel_width, 0, panel_b_x)

        self.panel_b.scrollok(True)

        self.panel_c = curses.newwin(max_y, max_x - 2 * panel_width, 0, panel_c_x)  # Ensure Panel C fills the rest

    def render(self, parent_content: List[str], current_content: List[str], file_content: List[str], view:View) -> None:
        self.panel_a.clear()
        self.panel_b.clear()
        self.panel_c.clear()

        # Fill in the content for Panel A
        self.fill_panel(self.panel_a, parent_content)

        # Fill in the content for Panel B, with highlighting
        #self.fill_panel(self.panel_b, current_content, highlight_index=self.current_pos)

        self.fill_panel_scroll(self.top_line, self.current_pos, current_content, view)

        # Fill in the content for Panel C
        self.fill_panel(self.panel_c, file_content, is_string=True)

        # Refresh panels to update the screen
        self.panel_a.refresh()
        self.panel_b.refresh()
        self.panel_c.refresh()
    

    def fill_panel_scroll(self, top_line, selected_row, content, view):
        self.panel_b.clear()
        height, width = self.stdscr.getmaxyx()
        for i in range(top_line, min(len(content), top_line + height - 2)):
            real_i = i - top_line
            if i == selected_row:
                self.panel_b.addstr(1+real_i, 1, content[i] + "\n", curses.A_REVERSE)
            else:
                if view.current[i]["children"]:
                    self.panel_b.addstr(1+real_i, 1, content[i] + "\n", curses.color_pair(2))
                else:
                    self.panel_b.addstr(1+real_i, 1, content[i] + "\n")

        self.panel_b.refresh()



    def fill_panel(self, panel, content, highlight_index=None, is_string=False):
        for idx, line in enumerate(content):
            if highlight_index == idx and not is_string:
                panel.addstr(1 + idx, 1, line, curses.color_pair(1))
            else:
                try:
                    panel.addstr(1 + idx, 1, line)
                except: # Happens when we overflow on Y direction
                    break


def parse_tags(items:list):
    """
    Take each individual JSON element and add it as a child of its parent
    """

    for item in items:
        item["children"] = []
        if "scope" in item:
            item["scope"] = item["scope"].split(".")
        else:
            item["scope"] = []

    for i, item in enumerate(items):
        if item["scope"]:
            last_item = item["scope"][-1]
            last_item_index = i - 1
            while last_item_index >= 0:
                last = items[last_item_index]
                if last["name"] == last_item and len(last["scope"]) != len(item["scope"]):
                    break
                last_item_index -= 1
            
            items[last_item_index]["children"].append(item)

    return [ item for item in items if not item["scope"] ]

def run_ctags(file_path):
    # Construct the command
    command = ["ctags", "--output-format=json", "--sort=off", "--fields=+n", file_path]
    
    # Run the command and capture the output
    result = subprocess.check_output(" ".join(command), shell=True)

    # each line is a JSON object
    result = str(result, encoding="utf-8")
    result = result.split("\n")

    return [json.loads(line) for line in result if line]


# Main function to start the curses application
def main():

    filename = sys.argv[1]
    data = run_ctags(filename)
    
    if not data:
        exit(1)
    
    graph = parse_tags(data)

    def _main(stdscr):
        curses.start_color()

        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)     

        view = View(graph)
        app = App(stdscr)
        # Example usage with dummy content

        while True:
            current_content = view.current_view()
            char = stdscr.getch()

            keyname = curses.keyname(char).decode()

            if keyname == "q":
                exit()
            if keyname == "k" and len(current_content):
                if app.current_pos > 0:
                    app.current_pos -= 1
                    if app.current_pos < app.top_line:
                        app.top_line -= 1
            elif keyname == "j":
                if app.current_pos < len(current_content) - 1:
                    app.current_pos += 1
                    if app.current_pos == app.top_line + app.height - 3:
                        app.top_line += 1
            elif keyname == "l":
                view.descend(app.current_pos)
                app.current_pos = 0
                app.top_line = 0
            elif keyname == "h": # ESCAPE
                view.ascend()
                app.current_pos = 0
            
            elif char == ord("\n"):
                view.start_editor(app.current_pos)
            app.render(view.parent_view(), view.current_view(), view.child_view(app.current_pos), view)
    
    curses.wrapper(_main)

# Run the curses application
if __name__ == "__main__":
    main()