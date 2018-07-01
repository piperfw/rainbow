# rainbow
Python script to format and print text with fun colours

### Description
Enter `rainbow` _string_ to formant _string_ and print the result to the console (standard output). Use `rainbow --file` _file_ to format the contents of the text file _file_ and print the results. By default, the text is split by character; specify `-w` to instead have the formatting applied on a word by word basis. For a detailed description of the available formatting, see `rainbow --help`.

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
rainbow "$(cal)" -fg -b
```
(note that double quotes, not single quotes, must be used here).

Have some fun with the available formatting. A personal favourite is the simple combination `-w -fg`.

### Future features
- Hidden character formatting
- 256 colour formatting
- Finer control over formatting (e.g. every 1 in 3 characters blinking)

### Bugs
- If `-dec` is used in conjunction with `-b`, the frequency of occurrence of blinking characters or words is reduced.

Tested in the `rxvt-unicode` terminal emulator running bash.


### Changelog
#### V1.0 (2018-06-24)
#### V1.1 (2018-07-01)
- Added `-a` and `-w` options
- Fixed handling of `-nfw` and `-bf` options when used in conjunction with each other and `-fg`, `-bg`
- Fixed error when an empty string is passed as an arguement
