import logging
import operator

from players.player import Player

logger = logging.getLogger('sette-mezzo')


class DynamicProgrammer(Player):

    def __init__(self):
        super().__init__()
        self.theta = .001
        self.gamma = 1
        self.policy = None

    def random_policy(self, state):
        return {"hit": .50, "stick": .50}

    def policy_evaluation(self, policy, environment, state_space):
        v = {tuple(draw.draw_data): 0 for draw in state_space}
        delta = self.theta + 1
        while delta > self.theta:
            delta = 0
            for ind, draw in enumerate(state_space):
                tupled_draw_data = tuple(draw.draw_data)
                v_init = v[tupled_draw_data]
                v_candidate = {tupled_draw_data: 0}
                for action in environment.action_space:
                    transitions = environment.get_transitions(draw, action)
                    for next_state, reward, prob in transitions:
                        v_candidate[tupled_draw_data] += policy[tupled_draw_data][action] * prob * (
                                reward + self.gamma * v[tuple(next_state.draw_data)])
                        logger.debug('%s, %s, %s, %s, %s, %s', draw.draw_data, action, next_state.draw_data,
                                     reward, prob, v[tupled_draw_data])
                v[tupled_draw_data] = v_candidate[tupled_draw_data]
                # if ind % 10000 == 0:
                #     logger.info('Draw %d: %s, value %s', ind, draw.draw_data, v[tupled_draw_data])
                delta = max(delta, abs(v_init - v[tupled_draw_data]))
            logger.info('Epoch finished. Delta %s', delta)
        return v

    def policy_iteration(self, environment, state_space):
        pi = {tuple(draw.draw_data): {'hit': 0.5, 'stick': 0.5} for draw in state_space}
        policy_stable = False
        while not policy_stable:
            # evaluate the current policy
            value_fn = self.policy_evaluation(pi, environment, state_space)
            logger.info('Value function computed')
            policy_stable = True
            # loop over state space
            for draw in state_space:
                tupled_draw_data = tuple(draw.draw_data)
                # perform one step lookahead
                old_action = pi[tupled_draw_data]
                policy_candidates = {}
                for action in environment.action_space:
                    v_action = 0
                    transitions = environment.get_transitions(draw, action)
                    for next_state, reward, prob in transitions:
                        v_action += prob * (reward + self.gamma * value_fn[tuple(next_state.draw_data)])
                    policy_candidates[action] = v_action
                best_action = max(policy_candidates.items(), key=operator.itemgetter(1))[0]
                pi[tupled_draw_data] = {key: 1. if key == best_action else 0. for key in environment.action_space}
                if old_action != pi[tupled_draw_data]:
                    policy_stable = False
            logger.info('Policy iteration computed')

            if policy_stable:
                return value_fn, pi

    def learn(self, environment):
        logger.info('Learning..')
        state_space = environment.generate_state_space()
        value_fn, pi = self.policy_iteration(environment, state_space)
        logger.info('Learning completed.')
        self.policy = pi

    def act(self):
        policy = self.policy[tuple(self.draw.draw_data)]
        return max(policy.keys(), key=lambda key: policy[key])
