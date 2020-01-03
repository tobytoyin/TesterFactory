import asyncio


async def count():
    print("123")
    await asyncio.sleep(2)
    print("sleep finish")


async def count_again():
    print("678")


async def main():
    await asyncio.gather(count(), count_again())

asyncio.run(main())
