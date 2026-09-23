"""Invoke the task-local MCP bridge with structured arguments."""
import asyncio,json,sys
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    p=StdioServerParameters(command=sys.executable,args=[str(Path(__file__).with_name('solidworks_mcp.py'))])
    async with stdio_client(p) as (r,w):
        async with ClientSession(r,w) as session:
            await session.initialize()
            result=await session.call_tool(sys.argv[1],json.loads(sys.argv[2]) if len(sys.argv)>2 else {})
            print(result.model_dump_json())
if __name__=='__main__':asyncio.run(main())
