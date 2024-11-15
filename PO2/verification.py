#!/usr/bin/env python3
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  Framework for Automaten en Formele Talen             #
#  Written by: Robin Visser & Tristan Laan              #
#  based on work by: Bas van den Heuvel & Daan de Graaf #
#                                                       #
#  This work is licensed under a Creative Commons       #
#  “Attribution-ShareAlike 4.0 International”  license. #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from PDA import PDA
from pathlib import Path


def verify_movement(trace: list[str], verbose=True) -> bool:
    """
    Creates and uses a PDA to verify proper Turing machine (TM) movement in a
    single execution trace
    trace: A list of events (tokens)
    returns: True if the trace behaviour is valid, False otherwise

    Examples:
    >>> verify_movement(['READ', 'LEM', 'WRITE', 'BLANK', 'MRIGHT', 'READ',
                         'SYMBOL', 'WRITE', 'SYMBOL', 'MLEFT', 'READ',
                         'SYMBOL', 'WRITE', 'SYMBOL', 'MRIGHT'])
    True

    >>> verify_movement(['READ', 'LEM', 'WRITE', 'LEM', 'MRIGHT', 'READ',
                         'SYMBOL', 'WRITE', 'SYMBOL', 'MRIGHT', 'READ',
                         'SYMBOL', 'WRITE', 'SYMBOL', 'MLEFT', 'READ',
                         'SYMBOL', 'WRITE', 'SYMBOL', 'MLEFT', 'READ', 'LEM',
                         'WRITE', 'BLANK', 'MLEFT'])
    False
    """

    ### Build and explain your PDA here... (see PDA.py)
    # In this PDA we only care about 'MLEFT' and 'MRIGHT'
    # only two states: final and dead
    # The PDA starts at the final state
    # whenever PDA reads a MRIGHT, put it into stack
    # the number of MRIGHT shows the distance from the leftmost position
    # if there is no MRIGHT in the stack
    # it means we are at the leftmost position
    # whenever PDA reads a MLEFT, if stack-top is MRIGHT
    # cancel them out, if stack is empty.
    # enter dead state
    # in dead state, no matter what PDA reads
    # it does nothing
    # Characters for initial stack symbol and epsilon: ⊥ , ϵ
    Q = ['final', 'dead']
    Sigma = ['MLEFT', 'MRIGHT', 'READ', 'WRITE', 'BLANK', 'LEM', 'SYMBOL']
    Gamma = ['⊥', 'ϵ', 'MRIGHT']
    delta = [(('final', 'MLEFT', '⊥'), ('dead', ['⊥'])),
             # when try to move left at leftmost position, move to dead state
             # now the elements in the stack does not matter anymore
             (('final', 'MLEFT', 'MRIGHT'), ('final', 'ϵ')),
             # when read a MLEFT and stack-top symbol is MRIGHT,
             # cancle them out
             (('final', 'MRIGHT', 'MRIGHT'), ('final', ['MRIGHT', 'MRIGHT'])),
             (('final', 'MRIGHT', '⊥'), ('final', ['MRIGHT', '⊥']))
             # when read a MRIGHT, put it into the stack
             ]
    s = 'final'
    F = ['final']
    pda_type = 'final_state'

    my_pda = PDA(Q, Sigma, Gamma, delta, s, F, pda_type, verbose)

    # Note: you can use my_pda.transition(symbol) to test a single transition.

    return my_pda.transition_all(trace)


def verify_lem(trace: list[str], verbose=True) -> bool:
    """
    Creates and uses a PDA to verify Turing machine (TM) left endmarker for a
    single execution trace
    trace: A list of events (tokens)
    returns: True if the trace behaviour is valid, False otherwise

    Examples:
    >>> verify_lem(['READ', 'LEM', 'WRITE', 'BLANK', 'MRIGHT'])
    False

    >>> verify_lem(['READ', 'LEM', 'WRITE', 'LEM', 'MRIGHT', 'READ', 'SYMBOL',
                    'WRITE', 'LEM', 'MRIGHT'])
    True

    >>> verify_lem(['READ', 'LEM', 'WRITE', 'LEM', 'MRIGHT', 'READ', 'SYMBOL',
                    'WRITE', 'LEM', 'MLEFT'])
    False

    >>> verify_lem(['READ', 'LEM', 'WRITE', 'LEM', 'MRIGHT', 'READ', 'SYMBOL',
                    'WRITE', 'LEM', 'MRIGHT', 'READ', 'SYMBOL', 'WRITE',
                    'SYMBOL', 'MLEFT', 'READ', 'LEM', 'WRITE', 'BLANK',
                    'MRIGHT'])
    False

    >>> verify_lem(['READ', 'LEM', 'WRITE', 'LEM', 'MRIGHT', 'READ', 'SYMBOL',
                    'WRITE', 'BLANK', 'MRIGHT', 'READ', 'LEM', 'WRITE', 'LEM',
                    'MRIGHT'])
    False
    """

    ### Build and explain your PDA here... (see PDA.py)
    # When PDA is in P1 state, it means
    # Characters for initial stack symbol and epsilon: ⊥ , ϵ
    Q = ['S', 'P1', 'P3', 'P4', 'P4R', 'P4W', 'DEAD']
    Sigma = ['MLEFT', 'MRIGHT', 'READ', 'WRITE', 'BLANK', 'LEM', 'SYMBOL']
    Gamma = ['MRIGHT', '⊥', 'ϵ', 'LEM', 'SB', 'READ', 'WRITE']
    delta = [(('S', 'READ', '⊥'), ('P1', ['READ', '⊥'])),
             # when PDA is at starting point
             # it has to read a READ
             (('P1', 'LEM', 'READ'), ('P1', ['LEM'])),
             # first time READ, must READ LEM
             (('P1', 'WRITE', 'LEM'), ('P1', ['WRITE'])),
             # After read a LEM, PDA must read a WRITE
             (('P1', 'LEM', 'WRITE'), ('P3', ['LEM'])),
             # After read a LEM, PDA must Write a LEM back
             # After this PDA enters P3, and never returns to P1
             (('P3', 'MRIGHT', 'LEM'), ('P4', ['MRIGHT'])),
             # P3 means that PDA has written a LEM back
             # so the only legal symbol here is MRIGHT
             # after this PDA enters P4 stage
             # P4 stage verifies property 4

             (('P4', 'READ', 'MRIGHT'), ('P4R', ['MRIGHT'])),
             (('P4', 'READ', '⊥'), ('P4R', ['⊥'])),
             # When PDA is in P4 stage, it is ready to be accepted.
             # When PDA is in P4 stage and it reads a READ
             # It enters P4R state, meaning that it needs to read a symbol

             (('P4R', 'BLANK', 'MRIGHT'), ('P4R', ['SB', 'MRIGHT'])),
             (('P4R', 'SYMBOL', 'MRIGHT'), ('P4R', ['SB', 'MRIGHT'])),
             # When the stacktop symbol is MRIGHT and PDA reads
             # a BLANK or a SYMBOL. 'SB' means BLANK or SYMBOL

             (('P4R', 'LEM', 'MRIGHT'), ('DEAD', ['⊥'])),
             # When the stacktop symbol is MRIGHT, it means
             # the pointer of Turing machine is at the leftmost position
             # so when the stacktop symbol is MRIGHT, the PDA cannot read LEM

             (('P4R', 'BLANK', '⊥'), ('DEAD', ['⊥'])),
             (('P4R', 'SYMBOL', '⊥'), ('DEAD', ['⊥'])),
             (('P4R', 'LEM', '⊥'), ('P4R', ['LEM', '⊥'])),
             # When the stack is empty, it means Turing machine have reached
             # the leftmost position. It should only read a LEM in this case

             (('P4R', 'WRITE', 'SB'), ('P4W', ['SB'])),
             (('P4R', 'WRITE', 'LEM'), ('P4W', ['LEM'])),
             # After reading a thing, PDA should read a WRITE

             (('P4W', 'SYMBOL', 'SB'), ('P4W', 'ϵ')),
             (('P4W', 'BLANK', 'SB'), ('P4W', 'ϵ')),
             # Whenver the PDA READ a SB and WRITE a SB back
             # cancel these two SBs out
             (('P4W', 'LEM', 'SB'), ('P3', ['LEM', '⊥'])),
             # If we write a LEM at the non-leftmost position
             # we need to empty the stack by push a '⊥' into it

             (('P4W', 'SYMBOL', 'LEM'), ('DEAD', ['⊥'])),
             (('P4W', 'BLANK', 'LEM'), ('DEAD', ['⊥'])),
             # When reads a LEM, PDA must write it back in the same step
             (('P4W', 'LEM', 'LEM'), ('P4W', 'ϵ')),

             (('P4W', 'MRIGHT', 'MRIGHT'), ('P4', ['MRIGHT', 'MRIGHT'])),
             (('P4W', 'MLEFT', 'MRIGHT'), ('P4', 'ϵ')),
             (('P4W', 'MRIGHT', '⊥'), ('P4', ['MRIGHT', '⊥']))
             ]
    s = 'S'
    F = ['S', 'P4']
    pda_type = 'final_state'

    my_pda = PDA(Q, Sigma, Gamma, delta, s, F, pda_type, verbose)

    # Note: you can use my_pda.transition(symbol) to test a single transition.

    return my_pda.transition_all(trace)


def main(file: Path, verbose: bool = True) -> None:
    """
    Reads multiple tokenized traces from the file at 'path' and feeds them to
    the various verification functions.
    """
    # Read and parse traces.
    with file.open(encoding='utf-8') as f:
        traces = [trace.split() for trace in [line.rstrip('\n') for line in f]]

    # Verify traces using verification functions
    valid_movement = []
    for trace in traces:
        print(f"Trace          : \"{trace}\"")
        movement_correct = verify_movement(trace, verbose)
        print(f"Verify movement: {movement_correct}")
        if movement_correct:
            valid_movement.append(trace)

    print()

    valid_lem = []
    for trace in valid_movement:
        print(f"Trace          : \"{trace}\"")
        lem_correct = verify_lem(trace, verbose)
        print(f"Verify lem     : {lem_correct}")
        if lem_correct:
            valid_lem.append(trace)

    # Print the remaining valid trace(s)
    print("\nRemaining trace(s):")
    for trace in valid_lem:
        print(trace)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Verifies a TM trace')
    parser.add_argument('-n', '--no-verbose', action='store_true',
                        help='disable verbose mode of PDA')
    parser.add_argument('tracefile', type=Path,
                        help='file containing tokenized traces')
    args = parser.parse_args()
    main(args.tracefile, not args.no_verbose)
