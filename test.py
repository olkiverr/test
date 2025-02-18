import asyncio
import aiohttp
import random
import time
import string

def generate_random_string(length=5):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def create_user(session):
    url = "http://172.16.20.219/4TTJ/Mustafi%20Kamil/Site/Monproject/php/inscription.php"

    name = "qzdqz"

    email = "test3+" + generate_random_string() + "@gmail.com"

    payload = {
        "username": name,
        "email": email,
        "password": "zz",
        "confirm-password": "zz"
    }

    try:
        async with session.post(url, data=payload, timeout=5) as response:
            return response.status == 200
    except Exception as e:
        return False
    
async def main():
    num_users = 500
    start_time = time.time()

    connector = aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [asyncio.create_task(create_user(session)) for _ in range(num_users)]
        results = await asyncio.gather(*tasks)

    end_time = time.time()
    success_count = sum(1 for result in results if result)
    duration = end_time - start_time

    print(f"Total users created: {success_count}")
    print(f"Time taken: {duration:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
    
    
    
