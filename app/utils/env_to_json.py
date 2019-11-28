import os
from dotenv import load_dotenv

load_dotenv()


def override(config):
    env = os.environ
    # print(env)
    for k, v in env.items():
        kwords = k.lower().split('_')

        def walkin(lookup, level, data):
            if lookup in data.keys():
                value = data.get(lookup)
                if isinstance(value, dict):
                    level += 1
                    walkin(kwords[level], level, value)
                else:
                    data[lookup] = v
            else:
                pass

        walkin(kwords[0], 0, config)

    return config