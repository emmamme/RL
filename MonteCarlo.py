# -*- coding: utf-8 -*-
"""A2_CartPoleWithRendering.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BWByzHhOpSfXEcMfoLH96XjIkMXdOJgU
"""

!apt-get install -y xvfb python-opengl > /dev/null 2>&1

!pip install gym pyvirtualdisplay > /dev/null 2>&1

import gym
import math
import numpy as np
import matplotlib.pyplot as plt
from IPython import display as ipythondisplay
from collections import defaultdict
from pyvirtualdisplay import Display

display = Display(visible=0, size=(400, 300))
display.start()

"""#### Exploring CartPole-v0 environment"""

# Setup and explore CartPole-v0 environemnt

env = gym.make("CartPole-v0")
env.reset()
prev_screen = env.render(mode='rgb_array')
plt.imshow(prev_screen)

for i in range(50000):
  action = env.action_space.sample()
  print("step i",i,"action=",action)
  obs, reward, done, info = env.step(action)
  print("obs=",obs,"reward=",reward,"done=",done,"info=",info)
  screen = env.render(mode='rgb_array')
  
  plt.imshow(screen)
  ipythondisplay.clear_output(wait=True)
  ipythondisplay.display(plt.gcf())

  if done:
    break
    
ipythondisplay.clear_output(wait=True)
env.close()
print("Iterations that were run:",i)

env.action_space

random_state = env.reset()
print('Random State', random_state)

random_action = env.action_space.sample()
print('Random Action', random_action)

# Off-policy MC implementation

def get_random_policy():
    return np.ones(env.action_space.n, dtype=float)/env.action_space.n

def get_greedy_policy(policy, Q, state):
    A = np.zeros(env.action_space.n, dtype=float)
    best_action = np.argmax(Q[state])
    A[best_action] = 1.0
    policy[state] = A
    return policy

def get_discrete_state(state):
    bucket = list(zip(env.observation_space.low, env.observation_space.high))
    bucket[0] = [-2.4, 2.4]
    bucket[1] = [-2.4, 2.4]
    bucket[2] = [-0.5, 0.5]
    bucket[3] = [-2.0, 2.0]
    bucket_num = (8, 8, 8, 8)
    bucket_indice = []
    for i in range(len(state)):
        if state[i] <= bucket[i][0]:
            bucket_index = 0
        elif state[i] >= bucket[i][1]:
            bucket_index = bucket_num[i] - 1
        else:
            # Mapping state to bucket
            scale = (bucket[i][1] - bucket[i][0])/(bucket_num[i]-1)
            state_offset = state[i] - bucket[i][0]
            bucket_index = int(round(state_offset/scale))
        bucket_indice.append(bucket_index)
    return tuple(bucket_indice)

def test_policy(Q):
    avg_steps = []
    for iter in range(1):
      obs = env.reset()
      for i in range(50000):
        state_key = get_discrete_state(obs)
        if state_key in Q:
          # print("State found in ")
          action = np.argmax(Q[state_key])
        else:
          action = env.action_space.sample()
        # print("step i",i,"action=",action)
        obs, reward, done, info = env.step(action)
        # print("obs=",obs,"reward=",reward,"done=",done,"info=",info)
        if done:
          avg_steps.append(i+1)
          # print("Iterations that were run:", i+1)
          break
    avg = sum(avg_steps)/len(avg_steps)
    # print("Average steps for policy:", avg)
    return avg
    
def mc_off_policy(env, num_episodes, gamma=1.0):
    Q = defaultdict(lambda:np.zeros(env.action_space.n))
    C = defaultdict(lambda:np.zeros(env.action_space.n))

    target_policy = {}
    avg_step_list = []

    for i_episode in range(num_episodes):
        episode = []
        state = env.reset()
        iteration = 0
        for t in range(200):
            iteration += 1
            state_key = get_discrete_state(state)
            probs = get_random_policy()
            # print("prob:", probs)
            action = np.random.choice(np.arange(len(probs)), p=probs)
            # print("Action chosen:", action)
            next_state, reward, done, _ = env.step(action)
            episode.append((state, action, reward))
            if done:
                # print("This is iteration:", iteration)
                break
            state = next_state
        
        G = 0.0
        W = 1.0
        for t in range(len(episode))[::-1]:
            state, action, reward = episode[t]
            state_key = get_discrete_state(state)
            G = gamma * G + reward
            # print(G)
            C[state_key][action] += W
            Q[state_key][action] += (W / C[state_key][action]) * (G - Q[state_key][action])
            # Update target policy
            target_policy = get_greedy_policy(target_policy, Q, state_key)
            best_action = np.argmax(target_policy[state_key])
            # print("Best action:", best_action)
            if action != best_action:
                break
            W = W * 1./get_random_policy()[action]

        # Test target policy for each episode
        ep_step_avg = test_policy(Q)
        avg_step_list.append(ep_step_avg)
        # Output episode result
        if i_episode % 1000 == 0:
            print("Episode number:", i_episode, "total steps target policy achieve:", ep_step_avg)
    return Q, target_policy, avg_step_list

# Test discretized states
state = [0.00685821, 0.03951754, 0.04130733, 0.04158863]
get_discrete_state(state)

# Test behaviour policy
get_random_policy()

# Running off-poicy MC
Q, policy, avg_list = mc_off_policy(env, num_episodes=40000)

# Visualize target policy of episodes
plt.plot(avg_list)
plt.xscale("log")
plt.xlabel("Episodes")
plt.ylabel("Steps can achieve")
plt.title("Average steps of MC Target Policy")

# Testing the final policy

env.reset()
prev_screen = env.render(mode='rgb_array')
plt.imshow(prev_screen)

for i in range(50000):
  state_key = get_discrete_state(obs)
  if state_key in Q:
      action = np.argmax(Q[state_key])
  else:
      action = env.action_space.sample()
  print("step i",i,"action=",action)
  obs, reward, done, info = env.step(action)
  print("obs=",obs,"reward=",reward,"done=",done,"info=",info)
  screen = env.render(mode='rgb_array')
  
  plt.imshow(screen)
  ipythondisplay.clear_output(wait=True)
  ipythondisplay.display(plt.gcf())

  if done:
    break
    
ipythondisplay.clear_output(wait=True)
env.close()
print("Iterations that were run:",i)

