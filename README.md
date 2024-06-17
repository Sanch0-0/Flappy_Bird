# Flappy Bird

## Description

Flappy Bird is a clone of the popular arcade game Flappy Bird, where the player controls a bird trying to pass through a series of pipes without hitting them. The game continues to be one of the most popular games in the arcade genre.

## Installation

1. Make sure you have Python 3.x and pip installed.
2. Clone the repository of the game:

    ```bash
    git clone https://github.com/Sanch0-0/Flappy_Bird.git
    ```

3. Navigate to the downloaded repository directory:

    ```bash
    cd flappy-bird
    ```

4. Install the dependencies from the `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

## Settings

The `config.py` file contains various customizable parameters for the game:

- `SCREEN_WIDTH`: Width of the game screen.
- `SCREEN_HEIGHT`: Height of the game screen.
- `FPS`: Frames per second.
- `BACKGROUND_SPEED`: Speed of the background image movement.
- `GAME_SPEED`: Initial game speed.
- `GAME_SPEED_INCREMENT_RATE`: Rate of increase of the game speed.
- `PIPE_DISTANCE`: Distance between pipes.

## Running the Game

To run the game, execute the following command from the root directory of the repository:

```bash
python main.py
```

## Controls

- Spacebar: Bird jumps upwards.
- Any mouse button: Bird jumps upwards (only in mouse click mode).