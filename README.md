# browse_ctags

Function requires the compiling ctags from source. First install libjansson, which allows ctags to output in JSON format

`sudo apt-get install libjansson-dev`

Then compile by following the directions here:

https://github.com/universal-ctags/ctags

The ctags version I installed had a bug where it didn't add line number to the JSON output so I had to compile it. Maybe it's because I didn't run `apt update && apt upgrade` 

For quick reference this is the command I use to run ctags:

`ctags --output-format=json --sort=off --fields=+n {file_path} | python3 parse_tags.py`


MVP Demo for ctags browser. CD into the directory and run `python3 browse_ctags.py`. Screen will be black. Use arrow key to navigate.
Highlight a ctag, press enter, and it will open up VIM at the line of that tag.


![](https://github.com/BnetButter/browse_ctags/blob/master/browse_ctags_v0.gif)