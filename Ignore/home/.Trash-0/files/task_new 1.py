import numpy as np
from physics_sim import PhysicsSim

#Changed file to change task
class Task():#To land softly at the origin 
    """Task (environment) that defines the goal and provides feedback to the agent."""
    def __init__(self, init_pose=None, init_vel=None, 
        init_angle_velocities=None, runtime=5., target_pose=None, target_vel=None):
        """Initialize a Task object.
        Params
        ======
            init_pose: initial position of the quadcopter in (x,y,z) dimensions and the Euler angles
            init_velocities: initial velocity of the quadcopter in (x,y,z) dimensions
            init_angle_velocities: initial radians/second for each of the three Euler angles
            runtime: time limit for each episode
            target_pos: target/goal (x,y,z) position for the agent
        """
        # Simulation
        self.sim = PhysicsSim(init_pose, init_vel, init_angle_velocities, runtime) 
        self.action_repeat = 3

        self.state_size = self.action_repeat * 6
        self.action_low = 0
        self.action_high = 900
        self.action_size = 4

        # Goal
        self.target_pose = target_pose if target_pose is not None else np.array([0., 0., 0., 0., 0., 0.])
        self.target_vel = target_vel if target_vel is not None else np.array([0., 0., 0.])

    def get_reward(self):
        """Uses current pose of sim to return reward."""
        alpha = .3
        beta = .3
        gamma = 1.
        reward = - alpha*(abs(self.sim.pose[:3] - self.target_pose[:3])).sum() - beta*(abs(self.sim.v[:3] - self.target_vel)).sum()/(1 + gamma*(abs(self.sim.pose[:3] - self.target_pose[:3])).sum() ) #velocity only counts when close to ground
       
        return reward

    def step(self, rotor_speeds):
        """Uses action to obtain next state, reward, done."""
        reward = 0
        pose_all = []
        for _ in range(self.action_repeat):
            done = self.sim.next_timestep(rotor_speeds) # update the sim pose and velocities
            reward += self.get_reward() 
            pose_all.append(self.sim.pose)
        next_state = np.concatenate(pose_all)
        return next_state, reward, done

    def reset(self):
        """Reset the sim to start a new episode."""
        self.sim.reset()
        state = np.concatenate([self.sim.pose] * self.action_repeat) 
        return state