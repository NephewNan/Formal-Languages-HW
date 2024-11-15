# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  Framework for Automaten en Formele Talen             #
#  Written by: Robin Visser & Tristan Laan              #
#  based on work by: Bas van den Heuvel & Daan de Graaf #
#                                                       #
#  This work is licensed under a Creative Commons       #
#  “Attribution-ShareAlike 4.0 International”  license. #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# DO NOT MODIFY THIS FILE

import sys


class FAError(Exception):
    pass


class StateError(FAError):
    pass


class TransitionError(FAError):
    pass


class FA:
    """
    Finite Automaton (FA)
    """

    def __init__(self,
                 Q: list[str] | set[str],
                 Sigma: list[str] | set[str],
                 delta: dict[str, dict[str, str]],
                 s: str,
                 F: list[str] | set[str],
                 verbose: bool = False):
        """
        Creates the FA object and performs input sanitization

        Q:       The finite set of states

        Sigma:   The input alphabet

        delta:   The transition table, a dictionary with elements in the form:
                 state: {[symbol: next_state]*}, where state ∈ Q,
                 symbol ∈ Sigma and next_state ∈ Q.

        s:       The start state

        F:       The finite set of final states

        verbose: Indicator specifying whether a warning should be printed if
                 the FA attempts a non-existent transition
        """

        # Verify proper use of states
        if len(Q) != len(set(Q)):
            raise StateError("Q contains duplicates")

        if s not in Q:
            raise StateError(f"Starting state '{s}' not in Q: {Q}")

        for state in F:
            if state not in Q:
                raise StateError(f"Final state '{state}' not in Q: {Q}")

        # Verify proper use of transitions
        for state in delta:
            if state not in Q:
                raise TransitionError(f"State '{state}' not in Q: {Q}")

            for symbol, next_state in delta[state].items():
                if symbol not in Sigma:
                    raise TransitionError(f"Symbol '{symbol}' for state "
                                          f"'{state}' not in Sigma: {Sigma}")
                if next_state not in Q:
                    raise TransitionError(
                        f"State '{next_state}' for symbol '{symbol}' and "
                        f"state '{state}' not in Q: {Q}")

        # Create states
        self.states = {}
        self.final_states = []
        for state_name in Q:
            # Check if the state-to-be has a transition table
            if state_name in delta.keys():
                transition_table = delta[state_name]
            else:
                transition_table = {}

            new_state = State(state_name, transition_table)
            self.states[state_name] = new_state
            if state_name in F:
                self.final_states.append(new_state)

        # Retain and assign variables
        self.verbose = verbose
        self.input_alphabet = Sigma
        self.start_state = self.states[s]
        self.current_state = self.start_state

    def transition(self, symbol: str) -> bool:
        """
        Try to follow the transition 'symbol' from the current state
        returns: True if succeeded, False otherwise
        """

        try:
            self.current_state = self.states[
                self.current_state.transition_table[symbol]]
            return True

        except KeyError:
            if self.verbose:
                print(f"Warning: State '{self.current_state.name}' has no "
                      f"transition for symbol '{symbol}', transition could "
                      "not be performed", file=sys.stderr)
            return False

    def is_final(self) -> bool:
        """
        Check whether the current state is a final state
        """
        return self.current_state in self.final_states

    def reset(self) -> None:
        self.current_state = self.start_state


class State:
    """State in a Finite Automaton (FA)"""

    def __init__(self, name: str, transition_table: dict[str, str]):
        """
        name: State name
        transition_table: Dictionary of key-value pairs, where a key is the
                          transition symbol and a value the name of the state
                          the transition leads to
        """
        self.name = name
        self.transition_table = transition_table
