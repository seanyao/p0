#!/usr/bin/env python3
"""
调试LLM API响应的临时脚本
"""

import asyncio
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.llm_service import llm_service

async def test_llm():
    try:
        prompt = '我想去北京、上海旅行'
        full_prompt = llm_service._build_location_parsing_prompt(prompt)
        print('发送的提示词:')
        print(full_prompt)
        print('\n' + '='*50 + '\n')
        
        response = await llm_service._call_llm(full_prompt)
        print('LLM响应内容:')
        print(repr(response))
        print('\n原始响应:')
        print(response)
        print(f'\n响应长度: {len(response)}')
        
        # 尝试解析响应
        locations = llm_service._parse_location_response(response)
        print(f'\n解析出的地点数量: {len(locations)}')
        for i, loc in enumerate(locations):
            print(f'地点{i+1}: {loc.name} - {loc.display_name}')
            
    except Exception as e:
        print(f'测试失败: {e}')
        import traceback
        traceback.print_exc()
    finally:
        await llm_service.close()

if __name__ == "__main__":
    asyncio.run(test_llm())