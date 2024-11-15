#!/usr/bin/env python3
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  Framework for Automaten en Formele Talen             #
#  Written by: Robin Visser & Tristan Laan              #
#  based on work by: Bas van den Heuvel & Daan de Graaf #
#                                                       #
#  This work is licensed under a Creative Commons       #
#  “Attribution-ShareAlike 4.0 International”  license. #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from TM import TM
from pathlib import Path


def extract_input(trace: str,
                  trace_tokenized: list[str] | None = None) -> str:
    """
    Determines (and returns) the input string given to the TM that caused it to
    perform the computation that produced the given trace.

    In principle you don't need to use trace_tokenized, but you can assume both
    trace, and trace_tokenized are provided during grading.

    trace:            a single TM trace (as a string with spaces).
    trace_tokenized:  optional, the same trace tokenized (as a list of tokens).
    returns:          the input (as a string without spaces)
    """

    ### Your code + explanation here
    # Characters for left endmarker and BLANK: ⊢ , ⊔
    # variable TMinput stores the input of the TM
    # variable 'pos' tracks the postion on the tape
    # pos = 0 means TM is handling the beginning of the tape
    # when read a '>', pos +1
    # when read a '<', pos -1
    # given a trace, the index of a symbol that is read satisfies:
    # index % 10 ==2
    # condtion "i%10 == 2 and trace[i] == '⊔' and pos == len(TMinput)"
    # means that TM is reading a '⊔', and input ends here
    TMinput = ""
    pos = -1
    for i in range(len(trace)):
        if trace[i] == '>':
            pos += 1
        elif trace[i] == '<':
            pos -= 1
        elif i % 10 == 2 and trace[i] == '⊔' and pos == len(TMinput):
            break
        elif i % 10 == 2 and trace[i] != '⊢' and pos == len(TMinput):
            TMinput += trace[i]
    if TMinput is not None:
        return TMinput
    return None


def extract_output(trace: str,
                   trace_tokenized: list[str] | None = None) -> str:
    """
    Determines (and returns) the tape output produced by the TM when performing
    the computation that produced the given trace. The ouput is the longest
    possible string _after_ the left endmarker that does not end in
    a BLANK ('⊔').

    In principle you don't need to use trace_tokenized, but you can assume both
    trace, and trace_tokenized are provided during grading.

    trace:            a single TM trace (as a string with spaces).
    trace_tokenized:  optional, the same trace tokenized (as a list of tokens).
    returns:          the output (as a string without spaces)
    """

    ### Your code + explanation here
    # keep track on the postion
    # Characters for left endmarker and BLANK: ⊢ , ⊔
    # TMouput stores the output of the TM
    # check the trace from the end.
    # pos = 0 means TM is handling the ending of the tape
    TMoutput = ""
    pos = 0
    for i in range(len(trace)-1, -1, -1):
        if trace[i] == '>':
            pos += 1
        elif trace[i] == '<':
            pos -= 1
        elif i % 10 == 6 and trace[i] == '⊔' and len(TMoutput) == 0:
            pos -= 1
        elif i % 10 == 6 and pos > len(TMoutput):
            TMoutput = trace[i] + TMoutput
    TMoutput = TMoutput[1:]

    if TMoutput is not None:
        return TMoutput
    return None


def reverse_manually(verbose: bool = True) -> TM:
    """
    The original TM was designed to: given two bitstrings as inputs,
    perform bitwise XOR operation on them and returns the result.

    The algorithm used by the original TM works as follows:
    The TM first reads one bit from the first input string, records it somehow,
    then writes back a '⊔'. Then TM moves rightwards until it reaches '|',
    meaning that it has reached the boundary of the two inputs.
    Then the TM reads '|', and writes back whatever it has recorded earlier.
    Then the TM moves right, until it reaches a '0' or '1' bit.
    Then the TM reads this bit and records it, and writes back a '⊔'.
    Then the TM moves leftwards until it reaches a '0' or '1' bit.
    This bit is the one we have wriiten back when reads '|'.
    Now the TM is able to compute an answer,
    by doing XOR operation on the digit it's reading now,
    and the digit it has recorded. After getting the answer,
    record the answer, write back a '|',
    and move left until it reaches a '⊔' for the first time,
    then write the answer back, then move right.
    If now the TM reads a '|', it means the TM has done all the calculation,
    the program should end, the TM reads '|' and writes back a '⊔'.
    If now the TM reads a '0' or '1', repeat the process above.

    verbose: Whether verbose mode of TM is enabled

    returns: A TM object of no more than 20 states, capable of reproducing the
             traces given by the assignment.
    """

    ### Your reverse-engineered TM + explanation here
    # Explanation of states:
    # Start: the starting state of TM
    # from start state, TM only accept a '⊢' and moves to Q1 state
    # Q1 state means the TM is looking for a digit from the first input
    # There are three different conditions
    # if TM reads a '0' or '1' in Q1, then it goes into 'RPass' state
    # meaning it should move right to look for the second input
    # the number behind RPass indicates what the first input is
    # if TM reads a '|', then the TM goes into accept state
    # when in 'RPass' state, whenever the TM reads a '0' or '1'
    # it writes back what it reads and moves right
    # until it reads a '|'
    # this means the TM is now at the boundary of input1 and input2
    # The TM should now enter 'Q2' state and write back what it has recorded
    # '1' if 'RPass1', '0' if 'RPass0'
    # 'Q2' means that the TM should now look for the second input
    # when reads a '⊔' in 'Q2' state, the TM does nothing but moves right
    # when reads a digit, the TM records it and enters 'LPass' state,
    # and moves left
    # when in 'LPass' state
    # the TM does nothing but moves left when it reads '⊔'
    # when reads a digit, it computes the answer and records the answer
    # then enter into 'Result' state
    # When in 'Result' state,
    # when reads a digit, the TM does nothing but moves left
    # when reads a '⊔', the TM writes back the answer and moves right
    Q = ['t', 'r', 'Start', 'Q1', 'RPass0', 'RPass1',
         'Q2', 'LPass0', 'LPass1', 'Result1', 'Result0']
    Sigma = ['0', '1', '|']
    Gamma = ['⊔', '⊢', '0', '1', '|']
    delta = [
        (('Start', '⊢'), ('Q1', '⊢', 'R')),

        (('Q1', '0'), ('RPass0', '⊔', 'R')),
        (('Q1', '1'), ('RPass1', '⊔', 'R')),
        (('Q1', '|'), ('t', '⊔', 'R')),

        (('RPass0', '1'), ('RPass0', '1', 'R')),
        (('RPass0', '0'), ('RPass0', '0', 'R')),
        (('RPass1', '1'), ('RPass1', '1', 'R')),
        (('RPass1', '0'), ('RPass1', '0', 'R')),

        (('RPass0', '|'), ('Q2', '0', 'R')),
        (('RPass1', '|'), ('Q2', '1', 'R')),

        (('Q2', '0'), ('LPass0', '⊔', 'L')),
        (('Q2', '1'), ('LPass1', '⊔', 'L')),
        (('Q2', '⊔'), ('Q2', '⊔', 'R')),

        (('LPass0', '⊔'), ('LPass0', '⊔', 'L')),
        (('LPass1', '⊔'), ('LPass1', '⊔', 'L')),

        (('LPass0', '0'), ('Result0', '|', 'L')),
        (('LPass0', '1'), ('Result1', '|', 'L')),
        (('LPass1', '0'), ('Result1', '|', 'L')),
        (('LPass1', '1'), ('Result0', '|', 'L')),

        (('Result0', '0'), ('Result0', '0', 'L')),
        (('Result0', '1'), ('Result0', '1', 'L')),
        (('Result1', '0'), ('Result1', '0', 'L')),
        (('Result1', '1'), ('Result1', '1', 'L')),

        (('Result0', '⊔'), ('Q1', '0', 'R')),
        (('Result1', '⊔'), ('Q1', '1', 'R'))

    ]
    s = 'Start'
    t = 't'
    r = 'r'

    tm = TM(Q, Sigma, Gamma, delta, s, t, r, verbose)

    return tm


def reverse_generic(traces: list[str],
                    traces_tokenized: list[list[str]] | None = None,
                    verbose: bool = True) -> TM:
    """
    Recreates (reverse-engineers) a TM which behaves identically to the TM that
    produced the supplied list of traces. Note: 'behaves identically' implies
    that the recreated TM must produce (given the same input) the exact same
    execution traces as the original.

    In principle you don't need to use trace_tokenized, but you can assume both
    trace, and trace_tokenized are provided during grading.

    traces:           a list of traces produced by the original TM.
    traces_tokenized: optional, tokenized versions of the original traces.
    returns:          a TM object capable of reproducing the traces given
                      the same input.
    """

    ### Your code + explanation here
    # the fundamental idea here is to reverse engineer one trace at one time,
    # and merge Sigmma, Gamma, delta together
    Sigma = []
    Gamma = ['⊔', '⊢']
    delta = []
    Q = ['t', 'r']

    # first let's compute Sigma and Gamma
    # iterate traces and extract the inputs
    # any symbol in input should also in Sigma and Gamma
    # Gamma should also include the symbols that we can write back to the tape
    # when i%10 == 6, trace[i] is a symbol that TM write back to the tape
    for trace in traces:
        input = extract_input(trace)
        for symbol in input:
            if symbol not in Sigma:
                Sigma.append(symbol)
            if symbol not in Gamma:
                Gamma.append(symbol)
        for i in range(len(trace)):
            if i % 10 == 6 and trace[i] not in Gamma:
                Gamma.append(trace[i])

    # Next we compute delta
    # when i%10 == 2
    # trace[i] is what the TM reads
    # trace [i+4] is what the TM write back
    # trace [i+6] is to which direction the TM moves
    # we only care about these three elements
    # for each new trace, the TM always starts at state '1'
    # that is, current_state = '1'
    # given a 'step' (e.g. - x + y z), z is either > or <
    # we check if there is a transition function for
    # (current_state, x)
    # if there is, then we use that function
    # and update current_state accordingly
    # if not, we need create a new state and update delta
    # that is, put ((current_state, x), (new_state, y, z)) into delta
    # then current_state = new_state
    stateNum = 1
    deltaDic = {}
    for trace in traces:
        currentState = '1'
        for i in range(len(trace)):
            if i % 10 == 2:
                movement = None
                if trace[i+6] == '<':
                    movement = 'L'
                elif trace[i+6] == '>':
                    movement = 'R'
                if (currentState, trace[i]) in deltaDic:
                    currentState = deltaDic[(currentState, trace[i])][0]
                else:
                    if i+10 < len(trace):
                        deltaDic.update({(currentState, trace[i]):
                                        (str(stateNum+1),
                                         trace[i+4], movement)})
                        delta.append(((currentState, trace[i]),
                                      (str(stateNum+1), trace[i+4], movement)))
                        tempTuple = deltaDic[(currentState, trace[i])]
                        currentState = tempTuple[0]
                        stateNum += 1
                    else:
                        deltaDic.update({(str(stateNum), trace[i]):
                                        ('t', trace[i+4], movement)})
                        delta.append(((str(stateNum), trace[i]),
                                      ('t', trace[i+4], movement)))
                        tempTuple = deltaDic[(str(stateNum), trace[i])]
                        currentState = tempTuple[0]
                        stateNum += 1

    # After computing delta, we need to compute Q
    # iterate over the functions in delta
    # put all the states into Q
    for function in delta:
        if function[0][0] not in Q:
            Q.append(function[0][0])
        if function[1][0] not in Q:
            Q.append(function[1][0])

    s = '1'
    t = 't'
    r = 'r'

    tm = TM(Q, Sigma, Gamma, delta, s, t, r, verbose)

    return tm


def main(path_traces: Path | None = None,
         path_tokenized: Path | None = None,
         verbose: bool = True) -> None:
    """
    Area to test different parts of your implementation.

    The present code is just an example, feel free to modify at will.
    While it is strongly recommended to write some tests here, the code
    produced will not directly influence your grade.
    """

    """ Input/output extraction """
    test_traces = [
                    # Test trace 1
                    '- ⊢ + ⊢ > '
                    '- 0 + 1 > '
                    '- 0 + 1 < '
                    '- 1 + ⊔ > '
                    '- 1 + ⊔ > '
                    '- ⊔ + a >',
                    # Test trace 2
                    '- ⊢ + ⊢ > '
                    '- a + c < '
                    '- ⊢ + ⊢ > '
                    '- c + ⊔ > '
                    '- b + ⊔ < '
                    '- ⊔ + ⊢ > '
                    '- ⊔ + ⊔ > '
                    '- ⊔ + ⊢ >'
                  ]

    test_traces_tokenized = [
                             # Test trace 1
                             ['READ', 'LEM',    'WRITE', 'LEM',    'MRIGHT',
                              'READ', 'SYMBOL', 'WRITE', 'SYMBOL', 'MRIGHT',
                              'READ', 'SYMBOL', 'WRITE', 'SYMBOL', 'MLEFT',
                              'READ', 'SYMBOL', 'WRITE', 'BLANK',  'MRIGHT',
                              'READ', 'SYMBOL', 'WRITE', 'BLANK',  'MRIGHT',
                              'READ', 'BLANK',  'WRITE', 'SYMBOL', 'MRIGHT'],
                             # Test trace 2
                             ['READ', 'LEM',    'WRITE', 'LEM',    'MRIGHT',
                              'READ', 'SYMBOL', 'WRITE', 'SYMBOL', 'MLEFT',
                              'READ', 'LEM',    'WRITE', 'LEM',    'MRIGHT',
                              'READ', 'SYMBOL', 'WRITE', 'BLANK',  'MRIGHT',
                              'READ', 'SYMBOL', 'WRITE', 'BLANK',  'MLEFT',
                              'READ', 'BLANK',  'WRITE', 'LEM',    'MRIGHT',
                              'READ', 'BLANK',  'WRITE', 'BLANK',  'MRIGHT',
                              'READ', 'BLANK',  'WRITE', 'LEM',    'MRIGHT']
                            ]

    correct_inputs = [
                      '00',
                      'ab'
                     ]

    correct_outputs = [
                       '⊔⊔a',
                       '⊢⊔⊢'
                      ]

    # Only test input/output extraction functions that do not return "None"
    for idx in range(len(test_traces)):
        feedback = ""
        extracted_input = extract_input(test_traces[idx],
                                        test_traces_tokenized[idx])
        if extracted_input is not None and \
           extracted_input != correct_inputs[idx]:
            feedback += f"\nextracted input: '{extracted_input}' " \
                        f"incorrect! (expected: '{correct_inputs[idx]}')"
        extracted_output = extract_output(test_traces[idx],
                                          test_traces_tokenized[idx])
        if extracted_output is not None and \
           extracted_output != correct_outputs[idx]:
            feedback += f"\nextracted output: '{extracted_output}' " \
                        f"incorrect! (expected: '{correct_outputs[idx]}')"
        if feedback:
            feedback = test_traces[idx] + feedback
            print(feedback)

    """ Reverse engineering """
    # Read execution traces (as strings with spaces), if available.
    traces = None
    if path_traces:
        with path_traces.open(encoding='utf-8') as f:
            traces = [trace for trace in [line.rstrip('\n') for line in f]]

    # Read tokenized traces (as lists of tokens, excluding 'SPACE'),
    # if available.
    traces_tokenized = None
    if path_tokenized:
        with path_tokenized.open(encoding='utf-8') as f:
            traces_tokenized = [trace.split() for trace in [line.rstrip('\n')
                                for line in f]]

    # Scratchpad, try to Reverse engineer the TM using the framework!
    # Examples:
    # if traces:
    #    i = 2
    #    print(traces[i])
    #    print(extract_input(traces[i]))
    #    print(extract_output(traces[i]))
    #    TM.visualize(extract_input(traces[i]), traces[i])
    #    for trace in traces:
    #       print(trace)
    #       print(extract_input(trace))
    #       print(extract_output(trace))
    #       TM.visualize(extract_input(trace), trace)
    #       break

    # Validate your solution by checking if it produces the original traces
    # given the original inputs...

    tm = reverse_generic(traces)
    if traces:
        for trace in traces:
            tm.set_input(extract_input(trace))
            tm.transition_all()
            produced_trace = tm.get_execution_trace()
            if trace != produced_trace:
                print("TM produced an incorrect trace!")
                print(f"original: {trace}")
                print(f"TM:       {produced_trace}")
                input("Press enter to continue...")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Reverse engineers a TM')
    parser.add_argument('-n', '--no-verbose', action='store_true',
                        help='disable verbose mode of TM')
    parser.add_argument('traces', type=Path, nargs='?',
                        help='file containing traces (optional)')
    parser.add_argument('tokenized_traces', type=Path, nargs='?',
                        help='file containing tokenized traces (optional)')
    args = parser.parse_args()
    main(args.traces, args.tokenized_traces, not args.no_verbose)
