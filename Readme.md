#Shellblend

##Summary

This library allows you to write scripts that blend the functionality of shell scripting with that of python scripting. If you've ever had to decide between writing a bash script or a Python script, weighing the benefits of either, this is the library for you. Bash allows you to easily invoke system commands and manipulate files, whereas Python allows stronger programming facilities and better string manipulation. Using shellblend, you get invoke commands easily and flexibly from within Python and pipe files into and out of them.

This library isn't very well written (I wrote most of v1 in a sleep deprived haze on a flight between the US and Israel), but it provides a useful API for utility scripts (which, in the course of my day-to-day work I write a large amount of), and allows the blending of shell-style and python-style programming more easily.

##Examples

To invoke a command:

```python
import shell

shell.c("git commit -a").run()
```

To pipe a command to another command:

```python
import shell

shell.c("ps aux").c("grep java").run()
```

To pipe the output of a command to a string:

```python

processes = shell.c("ps aux").c("grep java").to_string().run()
```

To pipe a string to the input of a command:

```python

shell.s("Hello world\nWhat's up?").c("grep what").run()
```

To pipe a file to the input of a command:

```python

shell.f("myfile.txt").c("grep what").run()
```

To pipe the output of a command to a file:

```python

shell.c("ps aux").to_file("myfile.txt").run()
```

To pipe the output of a command to /dev/null:

```python

shell.c("ps aux").to_dev_null().run()
```

To get the status of a command:

```python

status = shell.c("ps aux").c("grep java").to_dev_null().run()
```

To run a command in the background
```python

handle = shell.c("./my_binary").start()
handle.wait()```

Note that not everything (nor anything, really) in this readme has been tested. As the ancient romans used to say, "caveat emptor!".