from stable_baselines3 import SAC
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback, CallbackList
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.monitor import Monitor
from sim.agent.smart.gym_environment import HEMSEnvironment
import os
import torch
import random

# Seasonal dates (representative days from each season)
SEASONAL_DATES = {
    "winter": "2025-01-15",  # January (Winter)
    "spring": "2025-04-15",  # April (Spring)
    "summer": "2025-07-15",  # July (Summer)
    "autumn": "2025-10-15",  # October (Autumn)
}

def make_seasonal_env(date):
    def _init():
        env = HEMSEnvironment(date=date)
        env = Monitor(env)
        return env
    return _init

def train_sac_agent(total_timesteps=200000, save_path=None, use_gpu=True, 
                            n_envs=4, eval_freq=5000):
    """Train SAC agent on multiple seasons to avoid overfitting"""
    
    if save_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(base_dir, "models")
    
    # Create directories
    os.makedirs(save_path, exist_ok=True)
    log_path = os.path.join(save_path, "logs")
    os.makedirs(log_path, exist_ok=True)
    
    # Check GPU availability
    device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
    print(f"{'='*60}")
    print(f"Training SAC agent on: {device.upper()}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
    print(f"Parallel Environments: {n_envs}")
    print(f"Total Timesteps: {total_timesteps:,}")
    print(f"Timesteps per season: ~{total_timesteps // 4:,}")
    print(f"\nTraining Seasons:")
    for season, date in SEASONAL_DATES.items():
        print(f"  • {season.capitalize()}: {date}")
    print(f"\nSaving to: {save_path}")
    print(f"{'='*60}\n")
    
    # Create vectorized training environments
    env_fns = [make_seasonal_env(date) for date in SEASONAL_DATES.values()]
    
    if n_envs > 1:
        env = SubprocVecEnv(env_fns)
    else:
        env = DummyVecEnv(env_fns)
    
    # Create evaluation environments
    eval_envs = {}
    for season, date in SEASONAL_DATES.items():
        eval_env = DummyVecEnv([make_seasonal_env(date)])
        eval_envs[season] = eval_env
    
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path=save_path,
        name_prefix="sac_hems",
        save_replay_buffer=True,
        save_vecnormalize=True,
    )
    
    # Create evaluation callbacks for each season
    eval_callbacks = []
    for season, eval_env in eval_envs.items():
        season_log_path = os.path.join(log_path, f"eval_{season}")
        os.makedirs(season_log_path, exist_ok=True)
        
        eval_callback = EvalCallback(
            eval_env,
            best_model_save_path=os.path.join(save_path, f"best_model_{season}"),
            log_path=season_log_path,
            eval_freq=eval_freq // len(SEASONAL_DATES),  # Evaluate each season proportionally
            deterministic=True,
            render=False,
            n_eval_episodes=3,
            verbose=0
        )
        eval_callbacks.append(eval_callback)
    
    # Main evaluation callback
    main_eval_env = DummyVecEnv([make_seasonal_env(random.choice(list(SEASONAL_DATES.values())))])
    main_eval_callback = EvalCallback(
        main_eval_env,
        best_model_save_path=save_path,
        log_path=log_path,
        eval_freq=eval_freq,
        deterministic=True,
        render=False,
        n_eval_episodes=5,
        verbose=1
    )
    
    # Combine all callbacks
    callback_list = CallbackList([checkpoint_callback, main_eval_callback] + eval_callbacks)
    
    # Create SAC model
    model = SAC(
        "MlpPolicy",
        env,
        learning_rate=3e-4,
        buffer_size=200000,
        learning_starts=2000,
        batch_size=256,
        tau=0.005,
        gamma=0.99,
        train_freq=1,
        gradient_steps=1,
        ent_coef='auto',
        policy_kwargs=dict(net_arch=[256, 256]),
        verbose=1,
        tensorboard_log=log_path,
        device=device
    )
    
    print("Starting training...")
    
    # Train the model
    model.learn(
        total_timesteps=total_timesteps,
        callback=callback_list,
        progress_bar=True
    )
    
    print(f"\n{'='*60}")
    print(f"TRAINING COMPLETED!")
    print(f"{'='*60}")
    print(f"\nSeason-specific best models:")
    for season in SEASONAL_DATES.keys():
        print(f"  • {season.capitalize()}: best_model_{season}.zip")
    print(f"{'='*60}")
    
    env.close()
    for eval_env in eval_envs.values():
        eval_env.close()
    
    return model
