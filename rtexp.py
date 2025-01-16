#!/usr/bin/env python

from os import name, system
from time import time
import csv
import argparse
from random import shuffle
from rich.console import Console
import shutil

console = Console()


def main():
    parser = argparse.ArgumentParser(description='A tool for conducting a self-paced reading experiment.')
    parser.add_argument('input_file', help='Path to the .csv or .txt file with stimuli.')
    parser.add_argument('output_file', help='Path to the .csv file to save the output reading times and'
                                            'some metadata.')
    parser.add_argument('-r1', action='store_true', required=False,
                        help='Randomize the presentation order of the stimuli without any constraints.')
    parser.add_argument('-r2', action='store_true', required=False,
                        help='Randomize the presentation order of the stimuli, consecutive conditions are avoided.')
    parser.add_argument('-r3', action='store_true', required=False,
                        help='Randomize the presentation order of the stimuli within conditions; the order of '
                             'conditions is randomized, but conditions are kept together.')
    args = parser.parse_args()

    if args.input_file.endswith('.csv'):
        stimuli = read_stimuli_from_csv(args.input_file)
    elif args.input_file.endswith('.txt'):
        stimuli = read_stimuli_from_txt(args.input_file)
    else:
        raise ValueError('Input file must be a .csv or a .txt file.')

    assign_sentence_indices(stimuli)
    prepare_stimuli(stimuli)
    flag_words_of_interest(stimuli)

    if args.r1:
        shuffle(stimuli)
    if args.r2:
        stimuli = shuffle_separate_conditions(stimuli)
    if args.r3:
        stimuli = shuffle_keep_conditions(stimuli)

    collect_reading_data(stimuli, args.output_file)


def read_stimuli_from_csv(path) -> list[dict]:
    with open(path, 'r') as file:
        nonempty_lines = [line for line in file if line.strip()]
        csvreader = csv.DictReader(nonempty_lines, fieldnames=['condition', 'sentence'])
        return list(csvreader)


def read_stimuli_from_txt(path) -> list[dict]:
    with open(path, 'r') as file:
        nonempty_lines = [{'condition': f'{i + 1}', 'sentence': line.strip()}
                          for i, line in enumerate(file) if line.strip()]
        return nonempty_lines


def assign_sentence_indices(stimuli: list[dict]) -> None:
    """Assigns a global and condition-specific index to each stimulus in the input file."""
    condition_sentence_counts = {}
    for i, stimulus in enumerate(stimuli):
        condition = stimulus['condition']
        if condition not in condition_sentence_counts:
            condition_sentence_counts[condition] = 0
        condition_sentence_counts[condition] += 1
        stimulus['sentence_index'] = condition_sentence_counts[condition]
        stimulus['global_index'] = i + 1


def shuffle_separate_conditions(stimuli: list[dict]) -> list[dict]:
    """Shuffles the stimuli in a way that the same conditions don't appear consecutively."""
    while True:
        shuffle(stimuli)
        if all(stimuli[i]['condition'] != stimuli[i + 1]['condition'] for i in range(len(stimuli) - 1)):
            break
    return stimuli


def shuffle_keep_conditions(stimuli: list[dict]) -> list[dict]:
    """Shuffles the stimuli while keeping conditions together."""
    condition_groups = {}
    for stimulus in stimuli:
        condition = stimulus['condition']
        if condition not in condition_groups:
            condition_groups[condition] = []
        condition_groups[condition].append(stimulus)

    for condition in condition_groups:
        shuffle(condition_groups[condition])

    shuffled_conditions = list(condition_groups.keys())
    shuffle(shuffled_conditions)

    shuffled_stimuli = []
    for condition in shuffled_conditions:
        shuffled_stimuli.extend(condition_groups[condition])

    return shuffled_stimuli


def prepare_stimuli(stimuli: list[dict]) -> None:
    for stimulus in stimuli:
        stimulus['sentence'] = tokenize(stimulus['sentence'])


def tokenize(sentence: str) -> list[str]:
    return sentence.split()


def flag_words_of_interest(stimuli: list[dict]) -> None:
    """Removes the asterisk and instead adds an 'is_word_of_interest' flag to each word of the stimuli."""
    for stimulus in stimuli:
        words = stimulus['sentence']
        flagged_words = [{'word': word.lstrip('*'), 'is_word_of_interest': word.startswith('*')} for word in words]
        stimulus['sentence'] = flagged_words


def clear_terminal():
    if name == 'nt':    # Windows
        system('cls')
    else:               # Linux/MacOS
        system('clear')


def print_centered(word: str):
    """Prints the words centered in the terminal with minimal flickering."""
    center_line = int(shutil.get_terminal_size().lines / 2)
    filler_lines = '\n' * center_line
    console.print(filler_lines, end='')
    console.print(word, justify='center')


def collect_reading_data(stimuli: list[dict], output_file):
    """Runs the self-paced reading experiment in the terminal and writes the reading times to the output file."""
    clear_terminal()
    input('Press ENTER to start the experiment!' + '\n')
    clear_terminal()

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Condition', 'IsWordOfInterest', 'Global Index', 'Sentence Index', 'Word Index', 'Word',
                         'RT(s)'])

        for stimulus in stimuli:
            tokenized_stimulus = stimulus['sentence']
            for word_index, flagged_word in enumerate(tokenized_stimulus, start=1):
                word = flagged_word['word']
                is_word_of_interest = flagged_word['is_word_of_interest']

                time_before = time()
                print_centered(word)
                input()
                time_after = time()

                reading_time = time_after - time_before
                writer.writerow((
                    stimulus['condition'],
                    is_word_of_interest,
                    stimulus['global_index'],
                    stimulus['sentence_index'],
                    word_index,
                    word,
                    reading_time
                ))
                clear_terminal()

    print(f'End of the experiment. Reading times are saved to \'{output_file}\'.')


if __name__ == '__main__':
    main()
