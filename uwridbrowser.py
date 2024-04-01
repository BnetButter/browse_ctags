from collections.abc import Hashable, Iterable
import typing
import urwid

log = open("error.txt", "w")

class ExampleTreeWidget(urwid.TreeWidget):


    def keypress(self, size: tuple[int] | tuple[()], key: str) -> str | None:
        # log keypress
        super().keypress(size, key)
    
    def get_display_text(self):
        print(self.get_node().get_value(), file=log)
        return self.get_node().get_value()["name"]
    
    def selectable(self) -> bool:
        return True
    

class ExampleNode(urwid.TreeNode):
    
    def load_widget(self):
        return ExampleTreeWidget(self)
    
class ExampleParentNode(urwid.ParentNode):

    def load_widget(self):
        return ExampleTreeWidget(self)

    def load_child_keys(self):
        data = self.get_value()
        return range(len(data["children"]))
    
    def load_child_node(self, key):
        childdata = self.get_value()["children"][key]
        childdepth = self.get_depth() + 1
        if "children" in childdata:
            childclass = ExampleParentNode
        else:
            childclass = ExampleNode
        
        return childclass(childdata, parent=self, key=key, depth=childdepth)
    

class ExampleTreeBrowser:
    palette = [
        ("body", "black", "light gray"),
        ("focus", "light gray", "dark blue", "standout"),
        ("head", "yellow", "black", "standout"),
        ("foot", "light gray", "black"),
        ("key", "light cyan", "black", "underline"),
        ("title", "white", "black", "bold"),
        ("flag", "dark gray", "light gray"),
        ("error", "dark red", "light gray"),
    ]

    footer_text = [
        ("title", "Example Data Browser"),
        "    ",
        ("key", "UP"),
        ",",
        ("key", "DOWN"),
        ",",
        ("key", "PAGE UP"),
        ",",
        ("key", "PAGE DOWN"),
        "  ",
        ("key", "+"),
        ",",
        ("key", "-"),
        "  ",
        ("key", "LEFT"),
        "  ",
        ("key", "HOME"),
        "  ",
        ("key", "END"),
        "  ",
        ("key", "Q"),
    ]

    def __init__(self, data=None):
        self.topnode = ExampleParentNode(data)
        self.listbox = urwid.TreeListBox(urwid.TreeWalker(self.topnode))
        self.listbox.offset_rows=1
        self.header = urwid.Text("")
        self.footer = urwid.AttrMap(urwid.Text(self.footer_text), "foot")
        self.view = urwid.Frame(
            urwid.AttrMap(self.listbox, "body"),
            header=urwid.AttrMap(self.header, "head"),
            footer=self.footer
        )

    def main(self):
        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.unhandled_input)
        self.loop.run()
        
    def unhandled_input(self, k):
        if k in {'q', "Q"}:
            raise urwid.ExitMainLoop()
    

def get_example_tree():
    """generate a quick 100 leaf tree for demo purposes"""
    import json
    import sys
    with open(sys.argv[1]) as fp:
        data = json.load(fp)

    return { "name": "root", "children": data }


def main() -> None:
    sample = get_example_tree()
    ExampleTreeBrowser(sample).main()


if __name__ == "__main__":
    main()