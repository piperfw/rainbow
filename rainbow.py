import os, random, sys, re
"""
Note: Below, the ANSI escape sequences are prefixed with \u0001b (Unicode), which, in
my environment, appears to be translated to \x1b at runtime
(see https://misc.flogisoft.com/bash/tip_colors_and_formatting).

Please edit the value of the SCRIPT_DIR class variable.

Note to self: If I wanted to add in the option to have colours, blinking or decoration change
after every x characters say, where x is specified by the user, it would probably work to
put an appropriate amount of resets in between entries in any non-zero pools.
"""

class Rainbow:
	# Text file with usage message. Must be in the same directory as this .py
	MAN_PAGE = 'usage'
	# Name of this script
	SCRIPT_NAME = 'rainbow.py'
	# Directory containing rainbow.py and usage
	# ~~~~ To Edit ~~~~~~
	SCRIPT_DIR = "/home/username/example_directory"
	# ~~~~ To Edit ~~~~~~
	# ANSI codes
	# Return cursor to (0,0)
	HOME = "\u001b[0,0H"
	# Clear console window
	CLEAR = "\u001b[2J"
	# Reset and changes to colour of foreground (text) or background, or any decorations
	RESET = "\u001b[0m"
	# Regular (reset), bold, italics and underlined (regular was been added so that 'no decoration' is a possibility).
	# This is a personal choice. Note: Not using reversed -> "\u001b[7m", as this adds nothing when
	# background and foreground colours are considered.
	# N.B. [0m resets EVERYTHING, which [2m seems to just reset decoration, so can be used without interfering with
	# blinking codes. Unfortunately, [2m does not seem to reset decoration, so going to have to use [0m
	# DECORATION = ["\u001b[2m", "\u001b[1m", "\u001b[3m", "\u001b[4m"] 
	DECORATION = ["\u001b[0m", "\u001b[1m", "\u001b[3m", "\u001b[4m"] 
	# Blinking. Note, when using -b with -w, using 2+ spaces counts as a word (?). Ah, fixed it - see * in rainbow_print().
	BLINKING = ["\u001b[5m"]
	# Foreground black colour is not used by default as black text is not clear.
	FG_BLACK = "\u001b[30m"
	BRIGHT_FG_BLACK = "\u001b[30;1m"
	# Codes for non-black foreground colours; for reference only (for loops in self.generate_escape_pools
	#  are used to generate these at runtime)
	FG_NO_BLACK = ["\u001b[31m", "\u001b[32m", "\u001b[33m", "\u001b[34m",
	 "\u001b[35m", "\u001b[36m", "\u001b[37m"]
	BRIGHT_FG_NO_BLACK = ["\u001b[31;1m", "\u001b[32;1m", "\u001b[33;1m", "\u001b[34;1m",
	 "\u001b[35;1m", "\u001b[36;1m", "\u001b[37;1m"]
	# Similarly: Background Colours (including black): \u001b[40m - \u001b[47m
	# and Bright Background Colours (including black): \u001b[40;1m - \u001b[47;1m

	# Permissible command line options, and their corresponding arguments to be passed to __init__
	# Used in main() to call the Rainbow constructor with appropriate options.
	# Note: 'standard_input' is also an allowed 'option', but is handled differently (see call in main()).
	# Additionally, -f/--file is handled separately to the others (can I generalise further in case of future
	# options which are of the form -OPTION SETTING i.e. a 'pair'?)
	ALLOWED_OPTIONS_SHORT = {'h':'help_msg', 'f':'text_file_path','fg':'foreground','bg':'background','dec':'decoration',
	'r':'randomise', 'd':'dim', 'bf':'black_foreground', 'nwf':'no_white_foreground', 'b':'blinking', 'a':'everything',
	'w':'word_split'}
	# The values of ALLOWED_OPTIONS_LONG are kind of redundant, as currently have it that each long command line option
	# is simply the same as the corresponding arg it sets  (except --file, but this is checked separately in main)
	# Help is now different, as help is already a defined function in python.
	ALLOWED_OPTIONS_LONG = {'help':'help_msg','file':'text_file_path','foreground':'foreground','background':'background',
	'decoration':'decoration', 'blinking':'blinking','randomise':'randomise','clear':'clear','home':'home','dim':'dim', 
	'black-foreground':'black_foreground', 'no-white-foreground':'no_white_foreground', 'all':'everything',
	'words':'word_split'}

	def __init__(self, standard_input=None, text_file_path=None, randomise=False, blinking=False, clear=False,
		black_foreground=False, no_white_foreground=False, home=False, dim=False, foreground=False, background=False,
		decoration=False, help_msg=False, everything=False, word_split=False):
		# Print usage message. Note: Currently can be used at the same time as formatting etc.
		if help_msg:
			self.print_usage()
		# String to be formatted
		self.string_to_print = ''
		# If first argument is a string, it must be formatted. Add new line so have a gap between the
		# string defined by standard_input and that obtained from text_file_path (or the command prompt).
		if standard_input:
			self.string_to_print += standard_input + '\n'
		# If -f/--file option was passed, text_file_path is not None and a text file to be formatted & printed.
		if text_file_path:
			self.string_to_print += self.read_file(text_file_path)
		# Whether formatting should occur randomly (or in default ordering). Seed the generator regardless.
		if everything:
			self.randomise = True
		else:
			self.randomise = randomise
		# Could combine this if else statement with the one calling generate_escape_pools below.
		random.seed()
		# Whether string_to_print is to be split by word or not (default: split by character).
		self.word_split = word_split 
		# Clear console and move cursor to top left hand corner (position (0,0)), if appropriate.
		self.clear_home(clear=clear,home=home)
		# Dictionary to hold pools of ANSI codes. Key and values are names (str) and ANSI codes (a list) of each pool.
		self.escape_pools = {}
		# Populate self.escape_pools according to the arguments dim, foreground, background and decoration.
		if everything:
			# The -a or --all option turns on most colours and decorations
			self.generate_escape_pools(dim=dim, foreground=True, background=True, decoration=True,
			black_foreground=True, no_white_foreground=no_white_foreground, blinking=True)
		else:
			self.generate_escape_pools(dim=dim, foreground=foreground, background=background, decoration=decoration,
				black_foreground=black_foreground, no_white_foreground=no_white_foreground, blinking=blinking)
		# Lengths of each pool (list) in escape_pools; used in self.rainbow_print() to get indexing correct.
		self.lengths = {key : len(pool) for key,pool in self.escape_pools.items()}
		# Indices used to draw values from each pool in escape_pools; each initialised to -1 (if exist).
		self.current_indices = {key : -1 for key in self.escape_pools}
		# Format and print string_to_print using the codes contained in the pools of escape_pools.
		self.rainbow_print()

	def print_usage(self):
		"""Print contents of MAN_PAGE text file
		Uses bash escape code for italics (works with urxvt, at least); see main() in diary.py for use of .decode.
		"""
		usage_message = '\n'
		man_page_path = os.path.join(self.SCRIPT_DIR,self.MAN_PAGE)
		try:
			with open(man_page_path, 'r') as man_page:
				for line in man_page:
					usage_message += bytes(line, 'utf-8').decode('unicode_escape')
		except FileNotFoundError:
			print('{} not found. Ensure it is in the same directory as {}'.format(self.MAN_PAGE, self.SCRIPT_NAME))
		# Print file contents to console. Terminate with '' instead of '\n' (final line of usage will be blank)
		print(usage_message, end='')

	def clear_home(self, clear=False, home=False):
		"""Clear console and move cursor to top left hand corner (position (0,0)), if appropriate"""
		# Note: Often get a mess if have home but not clear. Allowing this.
		if clear:
			print(self.CLEAR, end='')
		if home:
			print(self.HOME, end='')

	def read_file(self, text_file_path):
		"""If a file is specified, read it and return to __init__ to be appended to self.string_to_print"""
		try:
			with open(text_file_path, 'r') as f:
				return f.read()
		except FileNotFoundError:
			print('{} not found. After -f or --file, please specify a full pathname or a path relative to \
				the directory of {}'.format(text_file_path, self.SCRIPT_NAME))

	def generate_escape_pools(self, dim=False, foreground=True, background=False, decoration=False,
		black_foreground=False, no_white_foreground=False, blinking=False):
		"""Generate pools on ANSI escape codes and add them to self.escape_pools

		Each pool is a list of strings, each an ANSI escape sequence.
		Each pool appears in self.escape_pools as a key-value pair, where the value is the pool and the key
		is the 'name' (str) of that pool.		
		"""
		# If required, initialise a key-value pair in escape_pools with an empty list as the value.
		if foreground or black_foreground or no_white_foreground:
			self.escape_pools["foreground"] = []
		# Now populate this list with the LEADING CHARCTERS (only) of the relevant escape codes.
		# This is done according to the flags foreground, black_foreground and no_white_foreground
		if foreground:
			for num in range(1,8):
				self.escape_pools["foreground"].append("\u001b[3{}".format(num))
		# If specified, add black. N.B. This must be done outside the foreground loop, so that the -bf
		# setting can be used independently of the -fg option (e.g., to use black text when -bg is specified)
		if black_foreground:
			self.escape_pools["foreground"].insert(0, "\u001b[30")
		# Remove whiteforeground text, if it has been added. If NO foreground colours have been added,
		# then add black. This is so the -nfw option has the expected effect when the -bg option is 
		# used without -fg, while using -nwf with -fg does NOT add black! I think this works as expected!
		if no_white_foreground:
			# Pitfall: Not just 'self.escape_pools'!
			if "\u001b[37" in self.escape_pools["foreground"]:
				# Could simply .pop() as white is last colour
				self.escape_pools["foreground"].remove("\u001b[37")
			elif not self.escape_pools["foreground"]:
				self.escape_pools["foreground"].insert(0, "\u001b[30")
		# Similar to foreground, except now black is considered (range(8) vs. range (1,8)).
		if background:
			self.escape_pools["background"] = []
			for num in range(8):
				self.escape_pools["background"].append("\u001b[4{}".format(num))
		# Final characters of escape code s are 'm' or ;1m' for ordinary (dim) or bright colours, respectively. 
		for key,pool in self.escape_pools.items():
			for index,sequence in enumerate(pool):
				if dim:
					pool[index] = sequence + "m"
				else:
					pool[index] = sequence + ";1m"
		# If user wants decorations or blinking, add a pool using the class variable.
		if decoration:
			self.escape_pools['decoration'] = self.DECORATION
		if blinking:
			# Add reset. Result is every other character blinking
			self.escape_pools['blinking'] = self.BLINKING
			self.escape_pools['blinking'].append(self.RESET)


	def rainbow_print(self):
		"""Print characters of self.string_to_print one at a time, prepending ANSI escape codes for 'rainbow' text."""
		# List of words or characters to iterate through and print
		list_to_print = ''
		if self.word_split:
			# Split string on whitespace. A regular expression is used in order to keep both the whitespace and newline
			# (these are lost when just using .split()). As spaces are retained, it is important .isspace() is used below.
			list_to_print = re.split(r'(\s+)', self.string_to_print)
		else:
			# Otherwise just split by character
			list_to_print = list(self.string_to_print)
		for char_or_word in list_to_print:
			# Do not format spaces. Print RESET escape sequence as previous character was likely formatted. May
			# reconsider this when using background colouring. Also RESET on new line, otherwise get coloured bars 
			# when background formatting is applied.
			# .isspace() is better than just ' ' as the latter does not catch multiple spaces or '\n'. This caused
			# slightly unexpected behaviour when using both -b and -w (i.e. some strings in list_to_print when
			# self.word_split == true could consist of multiple spaces and hence be treated as a word)
			if char_or_word.isspace():
			# if char_or_word == ' ' or char_or_word == '\n':
				print(self.RESET + char_or_word, end='')
				continue
			# Update current index (Note, initiated with -1 value in __init__)
			self.set_indicies()
			# For each pool in escape_pools, prepend the escape code specified by the corresponding index in 
			# current_indices to char.
			for key in self.escape_pools:
				char_or_word = self.escape_pools[key][self.current_indices[key]] + char_or_word
			# Now print the char_or_word with prepended escape code.
			print(char_or_word, end='')
		# Finally, reset any formatting and print a newline
		print(self.RESET)
		# Functionality END.

	def set_indicies(self):
		"""Set indices in self.current_indicies to achieve desired behaviour while avoiding any IndexError.

		if self.randomise, each index is randomly chosen between 0 and one less than the length of the 
		corresponding pool in self.current_pools (each pool is a list to be indexed using a value in self.indices).
		Otherwise each index is simply incremented, rolling over to 0 if the length of the corresponding
		pool in self.escape_pools is reached.
		"""
		for key in self.current_indices:
			if self.randomise:
				self.current_indices[key] = random.randrange(self.lengths[key])
			elif (self.current_indices[key] + 1) >= self.lengths[key]:
				self.current_indices[key] = 0
			else:
				self.current_indices[key] += 1

def main():
	# Remove first sys.argv, which is always rainbow.py.
	del sys.argv[0]
	# Dictionaries to store command line options (dictionaries instead of lists as some commands,
	# viz -f/--file, are of the form --option PARAMETER).
	long_options = {}
	# If no arguments (beyond script name), execute default behaviour: -h/--help (usage message)
	# To avoid index error in below code, just add '--help' to the argument list
	# Note: The second condition (and then assigment of sys.argv to []) is essential in order to
	# avoid IndexError with sys.argv[0][0] if "" is passed as a parameter.
	if len(sys.argv) == 0 or not sys.argv[0]:
		sys.argv = []
		sys.argv.append('--help')
	# If first argument has no option flag ('-'/'--'), take as input to be formatted and printed, 
	# possibly in addition to a text file's contents.
	if sys.argv[0][0] != '-':
		long_options['standard_input'] = sys.argv.pop(0)
	# Loop through any options, updating long_options and removing the option from 
	# sys.argv until none remain.
	while sys.argv:
		arg = sys.argv.pop(0)
		# The -f/--file option is special in that it is followed by a file path (or name, if 
		# file is in current working directory).
		# N.B. In order to generalise my CL options to accommodate options which require 1+
		#  additional parameters, I could add a class dictionary
		# OPTIONS_REQUIRING_MULTIPLE_ARGS similar above but whose values are LISTS of strings
		# instead of just a single string; the length of this list would be used to determine 
		# the number of required parameters following the option (actually, using a separate 
		# dictionary would not be necessary, although cleaner). Alternatively a tuple couple
		# be used as a value; te number of required parameters followed by a list of all
		# possible parameters (to cover the case where there may be two or three parameters following
		# a parameter, say -- actually that's not a good idea; must have a fixed number so 
		# jus tuse the length of the argument list given by the key).
		if arg == '-f' or arg == '--file':
			try:
				# Note: Rainbow.ALLOWED_OPTIONS_SHORT['f'] == 'text_file_path'
				long_options[Rainbow.ALLOWED_OPTIONS_SHORT['f']] = sys.argv.pop(0)
				continue
			# Occurs if -f/--file is not followed by anything. Note, if -f/--file is
			# followed by something other than a valid file name/path, an exception will
			# be thrown in Rainbow.read_file().
			except IndexError:
				print('Please specify a valid file path after the \'-f/--file\' option.')
				sys.exit(1)
		elif arg[:2] == '--' and arg[2:] in Rainbow.ALLOWED_OPTIONS_LONG:
			long_option_name = arg[2:]
			# corresponding_arguement != long_option_name, in general! For example, help vs. help_msg
			corresponding_argument = Rainbow.ALLOWED_OPTIONS_LONG[long_option_name] 
			long_options[corresponding_argument] = True
		elif arg[0] == '-' and arg[1:] in Rainbow.ALLOWED_OPTIONS_SHORT:
			# Populate long_options according to this short option (previously used a separate dict,
			# 'short_options,' and 'for key, value in short_options.items()...' to populate long_options
			short_option_name = arg[1:]
			corresponding_argument = Rainbow.ALLOWED_OPTIONS_SHORT[short_option_name]
			long_options[corresponding_argument] = True
		else:
			print('Invalid argument. See -h or --help for usage.')
			sys.exit(1)
	# Construct anonymous Rainbow object, unpacking long_options (keyword arguments).
	# All functionality occurs with this call (see Rainbow.__init()).
	Rainbow(**long_options)

if __name__ == '__main__':
	main()
