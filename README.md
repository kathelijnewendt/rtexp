# rtexp

**rtexp** is a program for conducting self-paced reading time experiments in the command-line.

A `.csv` file containing stimuli assigned to conditions (one per line) has to be provided as input file. The program also accepts `.txt` files containing only the stimuli, but in this case conditions are created automatically based on the position of the stimulus in the file.

A word may be marked with one or more asterisks `*` as being a *word of interest*, like this: `*interesting`. Note that an asterisk used in this way may not serve any other purposes in a stimulus and that maximally one word per stimulus may be prefaced with an asterisk to avoid problems in the later visualization with `rtviz`.

The words to be read are displayed in the center of the terminal, without the asterisks indicating *words of interest* being shown.

Stimuli can be randomly shuffled using one of the three optional command-line arguments `r1`, `r2`, and `r3`.
The program automatically adds indices to the stimuli and words, and includes them in the output `.csv` file, to help identify the original order of the stimuli (before shuffling) and for enhanced visualization with `rtviz`.

### Install

### Use

Using the provided sample file `example_stimuli.csv`, you can execute the following line to run a reading times experiment with basic random shuffling of the stimuli:
```bash
$ rtexp example_stimuli.csv example_readingtimes.csv -r1
```
With `rtviz`, you can visualize the obtained reading times saved in `example_readingtimes.csv`.
