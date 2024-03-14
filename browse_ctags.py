import curses
import os
import subprocess
import json

def draw_files(window, current_row, files, active):
    window.clear()
    for idx, row in enumerate(files):
        if idx == current_row and active:
            window.attron(curses.color_pair(1))
            window.addstr(idx, 0, row)
            window.attroff(curses.color_pair(1))
        else:
            window.addstr(idx, 0, row)
    window.refresh()

def render_tag_tree(window, tags, indent=0, row=0):
    positions = []
    for tag in tags:
        if row < curses.LINES and indent < curses.COLS // 2:
            window.addstr(row, indent, tag['name'])
            positions.append((row, indent, tag['name'], tag["path"], tag["line"]))
            row += 1
            if 'children' in tag and tag['children']:
                child_positions, row = render_tag_tree(window, list(tag['children'].values()), indent + 2, row)
                positions.extend(child_positions)
    return positions, row

def highlight_tag(window, positions, current_row):
    if 0 <= current_row < len(positions):
        row, indent, name, file, line = positions[current_row]
        window.attron(curses.color_pair(1))
        window.addstr(row, indent, name)
        window.attroff(curses.color_pair(1))
    window.refresh()

def execute_ctags(file_path):
    cmd = f"ctags --output-format=json --sort=off --fields=+n {file_path} | python3 parse_tags.py"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return [{"name": "Error parsing tag output", "children": {}}]

def file_explorer(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    stdscr.clear()

    current_file_row = 0
    current_tag_row = 0
    path = os.getcwd()
    files = os.listdir(path)
    files = ["[D] " + file if os.path.isdir(os.path.join(path, file)) else file for file in files]

    file_window = curses.newwin(curses.LINES, curses.COLS // 2, 0, 0)
    tag_window = curses.newwin(curses.LINES, curses.COLS // 2, 0, curses.COLS // 2)

    focus_on_files = True
    tags = []

    while True:
        selected_file = os.path.join(path, files[current_file_row].replace("[D] ", ""))
        if not os.path.isdir(selected_file):
            tags = execute_ctags(selected_file)

        draw_files(file_window, current_file_row, files, focus_on_files)
        tag_window.clear()
        positions, _ = render_tag_tree(tag_window, tags)
        if not focus_on_files:
            highlight_tag(tag_window, positions, current_tag_row)
        tag_window.refresh()

        key = stdscr.getch()

        if focus_on_files:
            if key == curses.KEY_UP and current_file_row > 0:
                current_file_row -= 1
            elif key == curses.KEY_DOWN and current_file_row < len(files) - 1:
                current_file_row += 1
            elif key == curses.KEY_RIGHT:
                focus_on_files = False
            elif key == curses.KEY_ENTER or key in [10, 13]:
                name = files[current_file_row].replace("[D] ", "")
                new_path = os.path.join(path, name)
                if os.path.isdir(new_path):
                    path = new_path
                    files = os.listdir(path)
                    files = ["[D] " + file if os.path.isdir(os.path.join(path, file)) else file for file in files]
                    current_file_row = 0
                    tags = []
        else:
            if key == curses.KEY_LEFT:
                focus_on_files = True
            elif key == curses.KEY_UP and current_tag_row > 0:
                current_tag_row -= 1
            elif key == curses.KEY_DOWN and current_tag_row < len(positions) - 1:
                current_tag_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                file, line = positions[current_tag_row][3], positions[current_tag_row][4]
                cmd = f"vim {file} +{line}"
                subprocess.run(cmd, shell=True)
                exit()
def main():
    curses.wrapper(file_explorer)

if __name__ == "__main__":
    main()
