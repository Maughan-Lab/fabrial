# Plotting
Finish implementing the plotting system in graph/widgets.py.

# General TODO
Finish implementing the TreeView system.

Implement the sequence wizard by writing a Python file that gets run during a sequence.
Use the exec(open("FILENAME.py").read()) function for this.

# Items to Shamelessly Steal from the Gamry Sequence Wizard
1. Loop (Cycle)
2. Potentiostatic EIS
3. Define a variable
4. Modify a variable by x

# Original (Not Stolen) Items
1. Temperature sequence

# Implementing the Runtime Sequences
- You will need to use the **locals** argument of `exec()` to run external code within the current scope of variables (i.e. getting access to instruments like the oven).
- Use a function that takes local arguments as an input. The names of the local arguments that will be used in the jinja file should be stored in a variable. For example

```
# main.py or somewhere where exec() is called
def run_other_code(myvar: Brain):
    name = "brain"
    env = Environment(loader=FileSystemLoader("templates"))
    output = env.get_template("GUI.py").render({name: name})
    print("running code")
    exec(output, locals={name: myvar})
```

```
# the jinja file
brain_ref = {{brain}}

brain_ref.perish.emit()
```

Here, the name "brain" will be used in the jinja file, and because we pass that name to `exec()`, the executed jinja file will get an actual reference to the variable `myvar`. The only things you need to keep in sync are the value of the `name` variable and the corresponding text in the `{{ }}` entry in the jinja file.