try:
    _, _, btn, rsp = await self.client.wait_for('interaction_update', timeout=60)
except asyncio.TimeoutError:
    pass
else:
    btn.defer(rsp)
    