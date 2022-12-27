import os
import asyncio


async def sync():
    prev_val = None
    while True:
        new_val = os.listdir("/home/zdv/projects/my/sound_project/uploads/")
        if new_val != prev_val:
            print("sync")
            print(new_val)
            prev_val = new_val
            os.system("rsync -a /home/zdv/projects/my/sound_project/uploads/ root@149.154.68.62:/root/sound_project/uploads/")
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(sync())

