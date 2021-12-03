import json
import os

import gym
import websocket

from reference.game_state import GameState


WORLD_SEED = os.environ.get("WORLD_SEED") or 1234
PRNG_SEED = os.environ.get("PRNG_SEED") or 4322


class BomberEnv(gym.Env):
    def __init__(self, uri, unit_id):
        self.unit_id = unit_id
        self.tick_num = 0
        self.uri = uri
        self.state = None
        self.ws = websocket.WebSocket()
        print("trying to connect")
        self.ws.connect(self.uri)
        print('connected')

    def step(self, action):
        """
        :param action: valid ActionPacket
        :return:
        """
        # action_packet = self._client.send(action)
        # Send action
        data = dict(
            type="next_game_state",
            sequence_id=self.tick_num,
            state=self.state,
            actions=[
                dict(
                    agent_id=self.unit_id,
                    action=action
                )
            ]
        )
        self._send(data)
        # Get next state
        data = self._recv()
        if data.get("type") == "game_state":
            self.state = data.get("payload")
        else:
            print(data)
            raise Exception("That didnt work.")
        self.tick_num += 1


    def reset(self):
        """
        {
            type: "request_game_reset",
            "world_seed": number,
            "prng_seed": number,
        }
        :return:
        """
        self._send(dict(
            type="request_game_reset",
            # world_seed=WORLD_SEED,
            # prng_seed=PRNG_SEED,
        ))
        data = self._recv()
        data_type = data.get("type")
        if data_type == "game_state":
            self.state = data.get("payload")
        else:
            print(data)
            raise Exception("That didnt work.")
        # ask game to tick
        # self._tick()
        resp = self._recv()

    def render(self, mode='human'):
        pass

    def _tick(self):
        self._send(dict(type="request_tick"))

    def _send(self, data: dict):
        return self.ws.send(json.dumps(data))

    def _recv(self):
        return json.loads(self.ws.recv())


if __name__ == '__main__':
    uri = os.environ.get('GAME_CONNECTION_STRING') or "ws://127.0.0.1:3000/?role=admin&agentId=agentA&name=python3-agent-dev"
    env = BomberEnv(uri, "a")
    env.reset()
    # print(env.state)
    action_packet = dict(
        type="move",
        unit_id="a",
        move="right"
    )
    env.step(action_packet)
    # print('='*1000)
    # print(env.state)
    print('stepped env')