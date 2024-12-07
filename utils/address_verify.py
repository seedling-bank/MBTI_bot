import asyncio
import traceback

import loguru
from eth_utils import is_checksum_address, is_address
from web3 import Web3

import hashlib


async def address_verification(address):
    try:
        if not is_address(address):
            return False

        # 检查地址是否是 EIP-55 校验和格式
        # if not is_checksum_address(checksum_address):
        #     return False

        # 如果通过以上两个检查，则是合法的 BSC 地址
        return True

    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())
        return False


async def main():
    result = await address_verification("0x816a05896f0d04b61e7eb60a0ea92498e8ca6366")
    # result = await address_verification(0xf64c725C05660d9A4864E1914a294729271c48f8)
    # result = await address_verification("0x36039469989cFF7d4419e4404B78bF7Ff62987fa")
    print(result)


if __name__ == '__main__':
    asyncio.run(main())
