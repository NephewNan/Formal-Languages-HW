# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  Framework for Automaten en Formele Talen             #
#  Written by: Robin Visser & Tristan Laan              #
#  based on work by: Bas van den Heuvel & Daan de Graaf #
#                                                       #
#  This work is licensed under a Creative Commons       #
#  “Attribution-ShareAlike 4.0 International”  license. #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# DO NOT MODIFY THIS FILE


class TMError(Exception):
    pass


class StateError(TMError):
    pass


class TransitionError(TMError):
    pass


class InputError(TMError):
    pass


class LogicError(TMError):
    pass


class TM:
    """
    Turing machine (TM)
    """

    def __init__(self,
                 Q: list[str] | set[str],
                 Sigma: list[str] | set[str],
                 Gamma: list[str] | set[str],
                 delta: list[tuple[tuple[str, str],
                                   tuple[str, str, str]]],
                 s: str,
                 t: str,
                 r: str,
                 verbose: bool = False,
                 no_halt: int = 1000):
        """
        Creates the TM object and performs input sanitization

        Q:       The finite set of states

        Sigma:   The input alphabet

        Gamma:   The tape alphabet

        delta:   The transition relation, a list of relation tuples containing
                 elements in the form:
                 ((state, tape_symbol), (state, tape_symbol, direction)), where
                 state ∈ Q, tape_symbol ∈ Gamma, and direction ∈ {'L', 'R'},
                 with 'L' indicating movement to the left and 'R' to the right.

        s:       The start state

        t:       The accept state

        r:       The reject state

        verbose: Indicator of whether to print updates after a transition

        no_halt: The amount of steps the TM is allowed to make before it is
                 assumed that it will not halt
        """

        # Verify that Gamma contains the left endmarker and blank symbol
        if '⊔' not in Gamma:
            raise TMError("Blank symbol '⊔' should be an element of Gamma, "
                          f"but it is not: {Gamma}")
        if '⊢' not in Gamma:
            raise TMError("left endmarker '⊢' should be an element of Gamma, "
                          f"but it is not: {Gamma}")

        # Verify that Sigma does not contain the left endmarker or blank
        if '⊔' in Sigma:
            raise TMError("Blank symbol '⊔' should not be an element of "
                          f"Sigma: {Sigma}")
        if '⊢' in Sigma:
            raise TMError("left endmarker '⊢' should not be an element of "
                          f"Sigma: {Sigma}")

        # Verify proper use of states
        if len(Q) != len(set(Q)):
            raise StateError("Q contains duplicates")

        if s not in Q:
            raise StateError(f"Starting state '{s}' not in Q: {Q}")

        if t not in Q:
            raise StateError(f"Accept state '{t}' not in Q: {Q}")

        if r not in Q:
            raise StateError(f"Reject state '{r}' not in Q: {Q}")

        # Verify proper use of transitions
        for lhs, rhs in delta:

            # Left-hand side
            state, tape_symbol = lhs
            if state not in Q:
                raise TransitionError(f"State '{state}' not in Q: {Q}")
            if tape_symbol not in Gamma:
                raise TransitionError(f"Symbol '{tape_symbol}' for relation "
                                      f"'{(lhs, rhs)}' not in Gamma: {Gamma}")

            # Right-hand side
            state, tape_symbol, movement = rhs
            if state not in Q:
                raise TransitionError(f"State '{state}' not in Q: {Q}")
            if tape_symbol not in Gamma:
                raise TransitionError(f"Symbol '{tape_symbol}' for relation "
                                      f"'{(lhs, rhs)}' not in Gamma: {Gamma}")
            if movement not in ['R', 'L']:
                raise TransitionError(f"Movement '{movement}' for relation "
                                      f"'{(lhs, rhs)}' is neither 'L' nor 'R'")

        # Verify that the tape alphabet contains the input alphabet as a subset
        if not set(Sigma).issubset(Gamma):
            raise TMError("Sigma is not a proper subset of Gamma, i.e. "
                          "Gamma does not contain all elements of Sigma")

        # Create states
        self.states = {}
        for new_state_name in Q:
            # Check if the state-to-be has any transitions
            new_state_transitions = []
            for transition in delta:
                if transition[0][0] == new_state_name:
                    new_state_transitions.append(transition)
            new_state = State(new_state_name, new_state_transitions)
            self.states[new_state_name] = new_state

        # Retain and assign variables
        self.input_alphabet = Sigma
        self.tape_alphabet = Gamma
        self.verbose = verbose
        self.max_steps = no_halt
        self.start_state = self.states[s]
        self.accept_state = self.states[t]
        self.reject_state = self.states[r]

        # Setup the tape and the rest of the TM
        self.tape = Tape([])  # init with empty tape
        self.current_state = self.start_state
        self.step_counter = 0
        self.input = None

        if verbose:
            print("TM initialization complete, waiting for input...")

    def reset(self) -> None:
        """
        Reset the TM
        """
        self.tape = Tape([] if self.input is None else self.input)
        self.current_state = self.start_state
        self.step_counter = 0

    def set_input(self, input: str) -> None:
        """
        Reset the TM and write a new input on the tape
        """

        # Verify validity of the input string
        for element in input:
            if element not in self.input_alphabet:
                raise InputError(f"Input symbol '{element}' not in input "
                                 "alphabet")

        self.input = list(input)
        self.reset()

        if self.verbose:
            print(f"Input specified: {self.input}")
            print(f"New tape:\n{self.tape}")

    def transition(self) -> bool:
        """
        Try to take a single step in the TM.
        returns: True if the transition was successful, False otherwise.
        """

        # Check if the TM has an input string
        if self.input is None:
            raise InputError("The TM has no input, specify using the "
                             "`TM.set_input(input)` function")

        # Check whether the TM has already entered the accept or reject state
        if self.current_state == self.accept_state:
            if self.verbose:
                print("The TM has entered the accept state")
            return False

        if self.current_state == self.reject_state:
            if self.verbose:
                print("Warning: the TM has already entered the reject state, "
                      "no transition was made")
            return False

        # Check whether we should assume that the TM is not going to halt
        if self.step_counter > self.max_steps:
            raise LogicError(f"The TM has taken more than {self.max_steps} "
                             "steps without entering the accept or reject "
                             "state, it is unlikely to halt!")

        # Read current element from the tape and try to transition.
        current_tape_element = self.tape.read()

        error = None
        try:
            # Lookup new state, new tape element, and direction of movement
            new_state_name, new_tape_element, movement = \
                self.current_state.transition_table[current_tape_element]
        except KeyError:
            error = f"State '{self.current_state.name}' has no " \
                    "transition for current tape symbol " \
                    f"'{current_tape_element}', the TM has stalled"
        if error:
            raise TMError(error)

        # Write new tape element
        self.tape.write(new_tape_element)

        # Move position of the head
        self.tape.move(movement)

        # Keep track of previous state for printing transition info.
        previous_state = self.current_state

        # Change state in accordance with the transition
        self.current_state = self.states[new_state_name]

        if self.verbose:
            used_transition = ((previous_state.name, current_tape_element),
                               (new_state_name, new_tape_element, movement))
            print(f"Made transition using: {used_transition}")
            print(f"New tape:\n{self.tape}")

        self.step_counter += 1

        return True

    def has_halted(self) -> bool:
        """
        Check whether the TM has halted.
        """
        return self.current_state == self.accept_state or \
            self.current_state == self.reject_state

    def transition_all(self) -> bool:
        """
        Take TM steps until the input is accepted or rejected.
        returns: True if the input is accepted, False if rejected.
        """

        while self.transition():
            pass

        if self.current_state == self.accept_state:
            return True

        if self.current_state == self.reject_state:
            return False

        raise TMError("Input was neither accepted or rejected")

    def get_tape_contents(self) -> list[str]:
        """
        Retrieve a list representing the current finite part of the tape
        touched by the TM
        """
        return self.tape.tape_actual

    def get_execution_trace(self) -> str:
        """
        Retrieve a string representing the execution trace of the steps that
        the TM has taken so far
        """
        # Omit the final space
        return self.tape.execution_trace[:-1]

    @staticmethod
    def visualize(trace_input: str, trace: str) -> None:
        """
        Visualize the computations described by _any_ TM execution trace.
        This method has no error checking (on purpose).
        trace_input: the input on the tape at the start of the trace (as a
                     string, without spaces).
        trace:       the execution trace describing the computations (as a
                     string, including spaces).
        """

        tape = Tape(list(trace_input))
        print(f"Trace specified: {trace}")
        print(f"Input specified: {trace_input}")
        print(f"New tape:\n{tape}")

        trace_elements = trace.split()

        idx_str = 0
        idx_elements = 0
        while idx_elements < len(trace_elements) - 1:
            tape.read()
            tape.write(trace_elements[idx_elements + 3])
            if trace_elements[idx_elements + 4] == "<":
                tape.move("L")
            else:
                tape.move("R")

            print(f"Made transition using step: {trace[idx_str:idx_str + 9]}")
            print(f"New tape:\n{tape}")

            idx_str += 10
            idx_elements += 5

        print("Reached the end of the execution trace")


class State:
    """State in a Turing machine (TM)"""
    def __init__(self,
                 name: str,
                 relations: list[tuple[tuple[str, str, str],
                                 tuple[str, list[str] | str]]]):
        """
        name:        State name
        relations:   A list of relation tuples containing elements in the form:
                     ((state, tape_symbol), (state, tape_symbol, direction)),
                     where state ∈ Q, tape_symbol ∈ Gamma, and
                     direction ∈ {'L', 'R'}, with 'L' indicating movement to
                     the left and 'R' to the right.
        """
        self.name = name

        transition_table = {}
        for lhs, rhs in relations:
            transition_table[lhs[-1]] = rhs

        self.transition_table = transition_table


class TapeError(Exception):
    pass


class Tape:
    """
    Tape (and head) of a Turing machine (TM)
    The tape also keeps track of the produced execution trace.
    """
    def __init__(self, tm_input: list[str]):

        # The (initial) relevant 'finite' part of the tape
        self.tape_actual = ['⊢']

        # Append the input to the tape
        self.tape_actual += tm_input

        # The current index of the TM head
        self.index = 0

        self.execution_trace = ""

    def __str__(self) -> str:
        # Assume a monospace terminal font.
        tape_result = ""
        head_result = ""

        for index in range(0, len(self.tape_actual)):
            if index > 0:
                tape_result += ' '
                head_result += ' '

            # Check if the head should be pointing to the current element
            if index == self.index:
                head_result += '^'
            else:
                head_result += ' ' * len(self.tape_actual[index])

            tape_result += self.tape_actual[index]

        tape_result += " ⊔ ⊔ ⊔ ..."

        return f"{tape_result}\n{head_result}"

    def read(self) -> str:
        """ Read tape contents at the current position of the head """

        self.execution_trace += "- " + self.tape_actual[self.index]
        return self.tape_actual[self.index]

    def write(self, symbol: str) -> None:
        """ Write symbol to the current position of the head """

        # Verify left endmarker safety
        if self.index == 0 and symbol != '⊢':
            raise TapeError("The TM has overwritten the left endmarker at the "
                            "leftmost piece of tape")

        self.execution_trace += " + " + symbol
        self.tape_actual[self.index] = symbol

    def move(self, direction) -> None:
        """ Move position of the head either to the left or to the right """
        if direction == 'R':
            # Check if we are at the end of the current 'finite' part.
            if self.index == (len(self.tape_actual) - 1):
                # Extend the finite part of the tape
                self.tape_actual.append('⊔')
            self.index += 1
            self.execution_trace += " > "
        elif direction == 'L':
            # Check if we are at the beginning of the tape
            if self.index == 0:
                raise TapeError("The TM has moved off the tape")
            self.index -= 1
            self.execution_trace += " < "
        else:
            raise TapeError(f"Movement '{direction}' is neither 'L' nor 'R'")
