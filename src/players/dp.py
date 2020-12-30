import logging
import operator

from players.player import Player

logger = logging.getLogger('sette-mezzo')


class DynamicProgrammer(Player):

    def __init__(self, draw_collection=None, policy=None, limit=None):
        super().__init__(draw_collection=draw_collection,
                         policy=policy, limit=limit)
        self.theta = .001
        self.gamma = 1
        self.value_fn = None

    def policy_evaluation(self, policy, environment, state_space):
        v = {draw.data: 0 for draw in state_space}
        delta = self.theta + 1
        while delta > self.theta:
            delta = 0
            for ind, draw in enumerate(state_space):
                state = draw.data
                v_init = v[state]
                v_candidate = {state: 0}
                for action in environment.action_space:
                    transitions = environment.get_transitions(draw, action)
                    for next_state, reward, prob in transitions:
                        # Bellman update rule
                        v_candidate[state] += policy[state][action] * prob * (
                                reward + self.gamma * v[next_state.data])
                        logger.debug('%s, %s, %s, %s, %s, %s', draw.data, action, next_state.data,
                                     reward, prob, v[state])
                v[state] = v_candidate[state]
                delta = max(delta, abs(v_init - v[state]))
            logger.info('Epoch finished. Delta %s', delta)
        return v

    def policy_iteration(self, environment, state_space):
        pi = {draw.data: {'hit': 0.5, 'stick': 0.5} for draw in state_space}
        policy_stable = False
        while not policy_stable:
            # evaluate the current policy
            value_fn = self.policy_evaluation(pi, environment, state_space)
            logger.info('Value function computed')
            policy_stable = True
            # loop over state space
            for draw in state_space:
                state = draw.data
                # perform one step lookahead
                old_action = pi[state]
                policy_candidates = {}
                for action in environment.action_space:
                    v_action = 0
                    transitions = environment.get_transitions(draw, action)
                    for next_state, reward, prob in transitions:
                        # Update rule
                        v_action += prob * (reward + self.gamma * value_fn[state])
                    policy_candidates[action] = v_action
                best_action = max(policy_candidates.items(), key=operator.itemgetter(1))[0]
                pi[state] = {key: 1. if key == best_action else 0. for key in environment.action_space}
                if old_action != pi[state]:
                    policy_stable = False
            logger.info('Policy iteration computed')

            if policy_stable:
                self.policy = pi
                self.value_fn = value_fn,

    def learn(self, environment):
        logger.info('Learning..')
        state_space = environment.generate_state_space(self)
        self.policy_iteration(environment, state_space)
        logger.info('Learning completed.')

    def act(self):
        policy = self.policy[tuple(self.draw_collection.data)]
        return max(policy.keys(), key=lambda key: policy[key])

    def copy(self):
        return DynamicProgrammer(draw_collection=self.draw_collection.copy(),
                                 policy=self.policy,
                                 limit=self.limit)
