# rainbow
Python script to format and print text with fun colours

### Description
Enter `rainbow` _string_ to formant _string_ and print the result to the console (standard output). Use `rainbow --file` _file_ to format the contents of the text file _file_ and print the results. For a detailed description of the available formatting, see `rainbow --help`.

### Setup
- Ensure `rainbow.py` and `usage' are in the same directory
- Edit the `SCRIPT_DIR` variable at the top of the ```Rainbow()``` class in `rainbow.py`
- Create an alias, for example in `~/.bashrc`
```sh 
alias rainbow="python full_path_to_rainbow.py"
```
(Otherwise `python full_path_to_rainbow.py` will be required to invoke the script).
Here `python` should refer to your python3 executable (`python3` on some systems).

### Tip
Apply formatting to the standard output of bash commands using command substitution. For example,
```sh
rainbow "$(ls)" -bg
```
(note that double quotes, not single quotes, must be used here).

### Future features
-  `-a` option to apply _all_ possible formatting at once
- Hidden character formatting
- 256 colour formatting
- Option to format by word instead of by character
- Finer control over formatting (e.g. every 1 in 3 characters blinking)

Tested in the `rxvt-unicode` terminal emulator running bash.
