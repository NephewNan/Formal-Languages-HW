#!/usr/bin/env python3
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  Framework for Automaten en Formele Talen             #
#  Written by: Robin Visser & Tristan Laan              #
#  based on work by: Bas van den Heuvel & Daan de Graaf #
#                                                       #
#  This work is licensed under a Creative Commons       #
#  “Attribution-ShareAlike 4.0 International”  license. #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Can probably be removed next year, but just to make sure for now,
# since the error is not very clear on Python 3.9.
import sys
if sys.version_info < (3, 10):
    print("FA.py requires Python 3.10 or newer. Cannot continue...")
    sys.exit(1)

from FA import FA, FAError
from pathlib import Path
import string


def create_fa(verbose: bool = False) -> FA:
    """
    Creates the finite automaton (FA) for trace tokenization
    Characters for left endmarker and BLANK: ⊢ , ⊔
    """
    ### Finish the automaton here... (based on Figure 3 in the assignment) ###
    Q = ['START', 'SPACE', 'MLEFT', 'MRIGHT', 'READ', 'WRITE', 'BLANK', 'LEM',
         'SYMBOL']
    Sigma = [' ', '<', '>', '-', '+', '⊔', '⊢', 'character', 'digit']
    delta = {'START': {' ': 'SPACE',
                       '<': 'MLEFT',
                       '>': 'MRIGHT',
                       '-': 'READ',
                       '+': 'WRITE',
                       '⊔': 'BLANK',
                       '⊢': 'LEM',
                       'digit': 'SYMBOL',
                       'character': 'SYMBOL'},
             'SYMBOL': {'character': 'SYMBOL',
                        'digit': 'SYMBOL'}}
    s = 'START'
    F = ['SPACE', 'MLEFT', 'MRIGHT', 'READ', 'WRITE', 'BLANK', 'LEM', 'SYMBOL']

    M = FA(Q, Sigma, delta, s, F, verbose)

    return M


def char_type(char: str) -> str:
    """
    Returns the type of a character found in the trace
    """
    if char in string.digits:
        return 'digit'
    elif char in string.ascii_letters:
        return 'character'
    else:
        return char


def lexer(fa: FA, trace: str) -> list[tuple[str, str]]:
    """
    The lexer iterates through the trace, tokenizing and assigning states to it
    fa: The finite automaton
    trace: A single string
    returns: A list of tuples containing first the token then the state.
    If something goes wrong the function should raise an FAError exception.
    E.g. raise FAError("Error message").
    """

    ### Your explanation of the lexer here ###
    # Iterate over the trace string. For any input, check if it's in alphabet.
    # If not, it means that we have read an letter that is not in the alphabet,
    # raise an error message.
    # If yes, then feed it to the FA.
    # Use transition function to feed a symbol to FA.
    # If transition returns true,
    # it means the current symbol is part of the token we're recognizing.
    # If transition returns false, check if the current state is final.
    # If it is final state, then we have successfully recogized a token.
    # (The current symbol we're reading is not part of this token.)
    # Then reset the FA to starting state and feed the current symbol to it.
    # If now the transistion returns false,
    # then it means the starting state does not accept this symbol,
    # raise an error message.(This step is unnecessary for this FA)
    # If transition returns false and current state is not final,
    # it means we have a token that is not acceptable for this FA,
    # raise an error message.
    # Finally, after reading all the symbols in trace,
    # we need to check if the current state of FA is final.
    # If it's in final, then the token now is the last one we recognize.
    # If it's not in final,
    # hen we have a token that is not acceptable for this FA.
    # (For this particular FA, this situation never happens)

    ### Your code here... ###
    # Attributes
    # ans (list): a list where we stroe (token, state_name) tuples
    # token (str): a string to which we append valid input symbol
    fa.reset()
    ans = []
    token = ""
    for input in trace:
        # Check if the input symbol is in the alphabet.
        # If yes, feed this input symbol to FA.
        # If not, raise an error message.
        if char_type(input) in fa.input_alphabet:
            # Feed the input symbol to FA by transition function.
            # If transition returns true,
            # then append the symbol to variable `token'.
            # If transition returns false, check if the FA is in final state.
            if FA.transition(fa, char_type(input)):
                token += input
            else:
                # Check if the FA in final state.
                # If not, it means the token we have now is unacceptable.
                # If yes, it means the token we have now is acceptable.
                # Append (token, current_state.name) to ans list.
                # Reset the fa and variable `token',
                # then feed the current symbol to the FA.
                if fa.is_final():
                    ans.append((token, fa.current_state.name))
                    fa.reset()
                    token = ""
                    # The FA is in start state, and we feed a symbol to it.
                    # If transition returns true,
                    # which is always the case in this FA,
                    # then append the input symbol to variable `token'.
                    # If transition returns false here,
                    # it means we have fed a symbol
                    # which is not acceptable for start state.
                    # Raise an error message.
                    # In this FA, this condition is redundant.
                    if FA.transition(fa, char_type(input)):
                        token += input
                    else:
                        raise FAError(
                            "The input " +
                            input + " is unacceptable for start state.")
                else:
                    raise FAError(
                        "The token " +
                        token + " is unacceptable for this FA")
        else:
            raise FAError(input + " is not in alphabet.")

    # After reading all the symbols in trace,
    # the final step is to check if the current_state is final state.
    # If yes, it means we still have one last valid token in FA.
    # (For this FA, this condition is always true.)
    # If no, it means the last token in FA is not valid, raise error message.
    if fa.is_final():
        ans.append((token, fa.current_state.name))
    else:
        raise FAError("The token " + token + " is unacceptable for this FA")

    return ans


def main(file: Path, verbose: bool = False) -> None:
    """
    Reads multiple traces from the file at 'file' and feeds them one by one to
    the lexer.
    """
    M = create_fa(verbose)

    with file.open(encoding='utf-8') as f:
        traces = [line.rstrip('\n') for line in f]

    for trace in traces:
        M.reset()
        print(f"Trace : \"{trace}\"")
        lexed_trace = lexer(M, trace)
        print(f"Lexer : {lexed_trace}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Tokenize a TM trace')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable verbose mode of FA')
    parser.add_argument('tracefile', type=Path,
                        help='file containing traces to tokenize')
    args = parser.parse_args()
    main(args.tracefile, args.verbose)
