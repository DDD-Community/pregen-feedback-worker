import asyncio
import json

import aio_pika
import aio_pika.abc

from pregen.pojo.message.slide_message import SlideMessage
from pregen.service.script_generator import ScriptGenerator
from pregen.utils.environment import get_envs
from pregen.utils.logging import logger


async def main(loop):
    mq_connection = await aio_pika.connect_robust(loop=loop, **get_envs().message_queue)

    script_generator = ScriptGenerator()

    async with mq_connection:
        channel: aio_pika.abc.AbstractChannel = await mq_connection.channel()
        queue: aio_pika.abc.AbstractQueue = await channel.get_queue(
            get_envs().message_queue["name"]
        )

        await logger.ainfo("Connection Success.")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:
                    async with message.process():
                        message_body = json.loads(message.body)
                        await logger.ainfo(f"Request: {message_body}")
                        action = message_body["action"]

                        if action == "GENERATE_SLIDE_ERROR":
                            message_request = SlideMessage.parse_obj(
                                message_body["body"]
                            )
                            script_generator.generate(message_request)
                        else:
                            raise AttributeError(f"wrong actions with `{action}`")
                except Exception:
                    await logger.aexception("An error occurred.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
