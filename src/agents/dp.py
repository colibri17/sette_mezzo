import logging
import operator

logger = logging.getLogger('sette-mezzo')


class DpAgent:

    def __init__(self, limit=None):
        self.theta = .001
        self.gamma = 1
        self.state_space = None
        self.limit = limit
        self.optimal_policy = None
        self.optimal_state_value = None

    def _learn_policy(self, state):
        """
        Given a game state, learn the optimal policy
        by using a policy iteration algorithm.
        :return: None
        """
        logger.info('Learning optimal policy for DP agent..')
        logger.debug('First we need to generate the state space..')
        player = state.players[state.current_player.id]
        self.state_space = state.generate_state_space(player)
        logger.debug('Then we apply policy iteration algorithm..')
        self.optimal_policy, self.optimal_state_value = self._policy_iteration(state)
        logger.info('Learning completed.')

    def step(self, state):
        """
        Given a game state, learn the optimal policy
        by using a policy iteration algorithm. When
        the policy is learned, it plays accordingly
        :param state: game state
        :return: the optimal action chosen
        """
        if self.optimal_policy is None:
            self._learn_policy(state)

        policy = self.optimal_policy[tuple(state.current_player.draws.data)]
        return max(policy.keys(), key=lambda key: policy[key])

    def _policy_evaluation(self, policy, state):
        """
        Evaluate the value of the current game state
        according to the provided policy
        :param policy: policy to be evaluated
        :param state: game state
        :return: the value of the current game state
        """
        v = {draws.data: 0 for draws in self.state_space}
        # Convergence-tracking variable
        delta = self.theta + 1
        while delta > self.theta:
            delta = 0
            # For each draws in the state_space
            for draws in self.state_space:
                draws_data = draws.data
                # Initial value of the draws
                v_init = v[draws_data]
                # Final value of the draws
                v_candidate = {draws_data: 0}
                # For each action I can apply..
                for action in state.action_space:
                    transitions = state.get_transitions(draws, action)
                    # ..and for each next state and reward and action probability
                    for next_state, reward, prob in transitions:
                        # Bellman update rule
                        v_candidate[draws_data] += policy[draws_data][action] * prob * (
                                reward + self.gamma * v[next_state.data])
                        logger.debug('%s, %s, %s, %s, %s, %s', draws_data, action, next_state.data,
                                     reward, prob, v[draws_data])
                v[draws_data] = v_candidate[draws_data]
                delta = max(delta, abs(v_init - v[draws_data]))
            logger.info('Epoch finished. Delta %s', delta)
        return v

    def _policy_iteration(self, state):
        """
        Apply the policy iteration algorithm, which
        consists of iterative steps of policy evaluation
        and policy improvement. In the policy evaluation
        step, we evaluate the value of each state according to
        the direct policy. In policy improvement we greedly
        update the policy towards the best next possible action
        :param state: game state
        :return: the optimal policy and optimal value of the game state
        """
        # Initial random policy
        pi = {draws.data: {'hit': 0.5, 'stick': 0.5} for draws in self.state_space}
        value_fn = None
        # Convergence-tracking variable
        policy_stable = False
        while not policy_stable:
            # evaluate the current policy
            value_fn = self._policy_evaluation(pi, state)
            logger.debug('Value function computed')
            policy_stable = True
            # loop over state space
            for draws in self.state_space:
                draws_data = draws.data
                # perform one step lookahead
                old_action = pi[draws_data]
                # Will contain the q(s,a) function
                policy_candidates = {}
                for action in state.action_space:
                    q_action = 0
                    transitions = state.get_transitions(draws, action)
                    for next_state, reward, prob in transitions:
                        # We compute the value of the action
                        q_action += prob * (reward + self.gamma * value_fn[draws_data])
                    policy_candidates[action] = q_action
                # Apply greedy action
                best_action = max(policy_candidates.items(), key=operator.itemgetter(1))[0]
                # Zeroing out non-optimal actions
                pi[draws_data] = {key: 1. if key == best_action else 0. for key in state.action_space}
                # Did we converge?
                if old_action != pi[draws_data]:
                    policy_stable = False
            logger.debug('Policy iteration computed')

        return pi, value_fn
