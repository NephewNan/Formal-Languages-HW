# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  Framework for Automaten en Formele Talen             #
#  Written by: Robin Visser & Tristan Laan              #
#  based on work by: Bas van den Heuvel & Daan de Graaf #
#                                                       #
#  This work is licensed under a Creative Commons       #
#  “Attribution-ShareAlike 4.0 International”  license. #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# DO NOT MODIFY THIS FILE


class PDAError(Exception):
    pass


class StateError(PDAError):
    pass


class TransitionError(PDAError):
    pass


class PDA:
    """
    Pushdown Automaton (PDA)
    """

    def __init__(self,
                 Q: list[str] | set[str],
                 Sigma: list[str] | set[str],
                 Gamma: list[str] | set[str],
                 delta: list[tuple[tuple[str, str, str],
                                   tuple[str, list[str] | str]]],
                 s: str,
                 F: list[str] | set[str],
                 pda_type: str = "final_state",
                 verbose: bool = False):
        """
        Creates the PDA object and performs input sanitization

        Q:        The finite set of states

        Sigma:    The input alphabet

        Gamma:    The stack alphabet

        delta:    The transition relation, a list of relation tuples containing
                  elements in the form:
                  ((state, input_symbol, top_stack), (state, [stack_symbol*])),
                  where state ∈ Q, input_symbol ∈ Sigma, top_stack ∈ Gamma, and
                  stack_symbol ∈ Gamma. Both 'top_stack' in the left-hand side
                  and '[stack_symbol*]' in the right-hand side may be
                  (individually) replaced with 'ϵ'.

        s:        The start state

        F:        The finite set of final states

        pda_type: Specification of the type of PDA: "final_state" or
                  "empty_stack"

        verbose:  Indicator of whether to print the new configuration after a
                  transition

        For an example of how to use delta, the definition in slide 67 of
        lecture 5 (with '[]' replaced by '<>' to avoid confusion):
        δ = { ((1, <, ⊥), (1, <⊥)), ((1, >, <), (1, ϵ)), ... }
        Would become:
        delta = [((1, '<', '⊥'), (1, ['<', '⊥'])), ((1, '>', '<'), (1, 'ϵ')),
                 ...]
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
        for lhs, rhs in delta:
            # Left-hand side
            state, input_symbol, top_stack = lhs
            if state not in Q:
                raise TransitionError(f"State '{state}' not in Q: {Q}")
            if input_symbol not in Sigma:
                raise TransitionError(f"Symbol '{input_symbol}' for relation "
                                      f"'{(lhs, rhs)}' not in Sigma: {Sigma}")
            if top_stack not in Gamma and top_stack != "ϵ":
                raise TransitionError(f"Stack symbol '{top_stack}' for "
                                      f"relation '{(lhs, rhs)}' not in Gamma: "
                                      f"{Gamma}")
            # Right-hand side
            state, top_stack_list = rhs
            if state not in Q:
                raise TransitionError(f"State '{state}' not in Q: {Q}")
            if top_stack_list != "ϵ":
                for stack_symbol in top_stack_list:
                    if stack_symbol not in Gamma:
                        raise TransitionError(
                            f"Stack symbol '{stack_symbol}' for relation "
                            f"'{(lhs, rhs)}' not in Gamma: {Gamma}")

        # Create states
        self.states = {}
        self.final_states = []
        for state_name in Q:
            # Check if the state-to-be has any transitions/relations
            state_transitions = []
            for relation in delta:
                if relation[0][0] == state_name:
                    state_transitions.append(relation)

            new_state = State(state_name, state_transitions)
            self.states[state_name] = new_state
            if state_name in F:
                self.final_states.append(new_state)

        # Retain and assign variables
        self.pda_type = pda_type
        self.verbose = verbose
        self.input_alphabet = Sigma
        self.stack_alphabet = Gamma
        self.start_state = self.states[s]
        self.current_state = self.start_state

        # Setup stack
        self.stack = ['⊥']

    def transition(self, symbol: str) -> bool:
        """
        Try to follow the input 'symbol' from the current state
        returns: True if succeeded, false otherwise
        """

        if self.stack:
            top_stack_symbol = self.stack.pop()
        else:
            top_stack_symbol = "ϵ"

        try:
            # Lookup new state and stack top
            new_state_name, new_top_stack = \
                self.current_state.transition_table[(symbol, top_stack_symbol)]

        except KeyError:
            if self.verbose:
                print(f"Warning: State '{self.current_state.name}' has no "
                      f"transition for input-symbol '{symbol}', and top "
                      f"stack-symbol: '{top_stack_symbol}', no changes were "
                      "made.")

            # Reappend the removed stack symbol
            if top_stack_symbol != "ϵ":
                self.stack.append(top_stack_symbol)

            return False

        # Keep track of previous state for printing transition info
        previous_state = self.current_state

        self.current_state = self.states[new_state_name]

        # Add new stack symbols to existing stack. Unfortunately Kozen notation
        # has the top of the stack on the left, while Python has it on the
        # right --> reverse append the symbols.
        if new_top_stack != "ϵ":
            for element in reversed(new_top_stack):
                self.stack.append(element)

        if self.verbose:
            used_relation = ((previous_state.name, symbol, top_stack_symbol),
                             (self.current_state.name, new_top_stack))
            print(f"Made transition using relation: {used_relation}")
            stack_visual = ' '.join(reversed(self.stack))
            print(f"State: '{self.current_state.name}'| "
                  f"Stack: top -> {stack_visual}")

        return True

    def is_final(self) -> bool:
        """
        Check whether the current state is a final state
        """
        return self.current_state in self.final_states

    def is_empty(self) -> bool:
        """
        Check whether the PDA stack is empty
        """
        return not self.stack

    def transition_all(self, list_of_symbols: list[str]) -> bool:
        """
        Run PDA against the complete input 'list_of_symbols'
        returns: True if the input is accepted, False otherwise
        """

        for symbol in list_of_symbols:
            self.transition(symbol)

        if self.is_final() and self.pda_type == "final_state":
            return True

        if self.is_empty() and self.pda_type == "empty_stack":
            return True

        return False

    def reset(self) -> None:
        self.current_state = self.start_state
        self.stack = ['⊥']


class State:
    """State in a Pushdown Automaton (PDA)"""
    def __init__(self,
                 name: str,
                 relations: list[tuple[tuple[str, str, str],
                                 tuple[str, list[str] | str]]]):
        """
        name:       State name

        relations:  A list of relation tuples containing elements in the form:
                    ((state, input_symbol, top_stack),
                     (state, [stack_symbol*])), where state ∈ Q,
                    input_symbol ∈ Sigma, top_stack ∈ Gamma, and
                    stack_symbol ∈ Gamma. Both 'top_stack' in the left-hand
                    side and '[stack_symbol*]' in the right-hand side may be
                    (individually) replaced with 'ϵ'.
        """
        self.name = name

        transition_table = {}
        for lhs, rhs in relations:
            transition_table[lhs[1:]] = rhs
        self.transition_table = transition_table
