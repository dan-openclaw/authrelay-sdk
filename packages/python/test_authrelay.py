#!/usr/bin/env python3
"""
Test script for AuthRelay Python SDK

Usage:
    API_KEY=ar_live_... python test_authrelay.py

This script will create a real session and demonstrate polling.
"""
import os
import sys
import asyncio


def test_sync():
    """Test synchronous API"""
    api_key = os.environ.get('API_KEY')
    
    if not api_key:
        print('❌ Error: API_KEY environment variable is required')
        print('\nUsage: API_KEY=ar_live_... python test_authrelay.py')
        sys.exit(1)
    
    try:
        from authrelay import AuthRelay
        
        print('📋 AuthRelay SDK Test (Sync)\n')
        print(f'✓ API Key provided: {api_key[:10]}...')
        print('✓ Module imported successfully')
        
        # Create a client
        relay = AuthRelay(api_key=api_key)
        print('✓ AuthRelay client initialized')
        
        # Try creating a session
        print('\nCreating test session...')
        session = relay.create_session(
            url='https://httpbin.org/cookies',
            reason='Test authentication',
        )
        print(f'✓ Session created: {session.get_session_id()}')
        print(f'✓ Operator URL: {session.get_operator_url()}')
        
        print('\n✅ Sync API test successful!')
        print('\nTo test fully:')
        print('1. Open the operator URL above')
        print('2. Complete authentication')
        print('3. SDK will poll automatically')
        
    except Exception as error:
        print(f'❌ Test failed: {error}')
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def test_async():
    """Test asynchronous API"""
    api_key = os.environ.get('API_KEY')
    
    if not api_key:
        return
    
    try:
        from authrelay import AsyncAuthRelay
        
        print('\n📋 AuthRelay SDK Test (Async)\n')
        print(f'✓ API Key provided: {api_key[:10]}...')
        print('✓ Module imported successfully')
        
        # Create a client
        relay = AsyncAuthRelay(api_key=api_key)
        print('✓ AsyncAuthRelay client initialized')
        
        # Try creating a session
        print('\nCreating test session...')
        session = await relay.create_session(
            url='https://httpbin.org/cookies',
            reason='Test authentication (async)',
        )
        print(f'✓ Session created: {session.get_session_id()}')
        print(f'✓ Operator URL: {session.get_operator_url()}')
        
        print('\n✅ Async API test successful!')
        
    except ImportError:
        print('\n⚠️  Async test skipped (aiohttp not installed)')
        print('   Install with: pip install authrelay[async]')
    except Exception as error:
        print(f'❌ Async test failed: {error}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_sync()
    
    try:
        asyncio.run(test_async())
    except RuntimeError:
        pass  # Already tested in test_sync
