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
        v = {tuple(draw.data): 0 for draw in state_space}
        delta = self.theta + 1
        while delta > self.theta:
            delta = 0
            for ind, draw in enumerate(state_space):
                tupled_data = tuple(draw.data)
                v_init = v[tupled_data]
                v_candidate = {tupled_data: 0}
                for action in environment.action_space:
                    transitions = environment.get_transitions(draw, action)
                    for next_state, reward, prob in transitions:
                        v_candidate[tupled_data] += policy[tupled_data][action] * prob * (
                                reward + self.gamma * v[tuple(next_state.data)])
                        logger.debug('%s, %s, %s, %s, %s, %s', draw.data, action, next_state.data,
                                     reward, prob, v[tupled_data])
                v[tupled_data] = v_candidate[tupled_data]
                # if ind % 10000 == 0:
                #     logger.info('Draw %d: %s, value %s', ind, draw_list.data, v[tupled_data])
                delta = max(delta, abs(v_init - v[tupled_data]))
            logger.info('Epoch finished. Delta %s', delta)
        return v

    def policy_iteration(self, environment, state_space):
        pi = {tuple(draw.data): {'hit': 0.5, 'stick': 0.5} for draw in state_space}
        policy_stable = False
        while not policy_stable:
            # evaluate the current policy
            value_fn = self.policy_evaluation(pi, environment, state_space)
            logger.info('Value function computed')
            policy_stable = True
            # loop over state space
            for draw in state_space:
                tupled_data = tuple(draw.data)
                # perform one step lookahead
                old_action = pi[tupled_data]
                policy_candidates = {}
                for action in environment.action_space:
                    v_action = 0
                    transitions = environment.get_transitions(draw, action)
                    for next_state, reward, prob in transitions:
                        v_action += prob * (reward + self.gamma * value_fn[tuple(next_state.data)])
                    policy_candidates[action] = v_action
                best_action = max(policy_candidates.items(), key=operator.itemgetter(1))[0]
                pi[tupled_data] = {key: 1. if key == best_action else 0. for key in environment.action_space}
                if old_action != pi[tupled_data]:
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
