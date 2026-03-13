/**
 * Integration test for AuthRelay TypeScript SDK
 * 
 * Usage:
 *   API_KEY=ar_live_... npm run build && npx ts-node test/integration.ts
 * 
 * This script will create a real session and demonstrate polling.
 */

import { AuthRelay } from '../src';

const apiKey = process.env.API_KEY;

if (!apiKey) {
  console.error('❌ Error: API_KEY environment variable is required');
  console.error('\nUsage: API_KEY=ar_live_... npx ts-node test/integration.ts');
  process.exit(1);
}

async function testSync() {
  try {
    console.log('📋 AuthRelay SDK Test (TypeScript)\n');
    console.log(`✓ API Key provided: ${apiKey.substring(0, 10)}...`);

    // Create a client
    const relay = new AuthRelay({ apiKey });
    console.log('✓ AuthRelay client initialized');

    // Try creating a session
    console.log('\nCreating test session...');
    const session = await relay.createSession({
      url: 'https://httpbin.org/cookies',
      reason: 'Test authentication',
    });
    console.log(`✓ Session created: ${session.getSessionId()}`);
    console.log(`✓ Operator URL: ${session.getOperatorUrl()}`);

    // Set up event handlers
    session.on('claimed', () => {
      console.log('→ Operator picked it up!');
    });
    session.on('completed', (creds) => {
      console.log('→ Got credentials:', creds);
    });
    session.on('expired', () => {
      console.log('→ Session expired');
    });
    session.on('error', (err) => {
      console.error('→ Error:', err);
    });

    console.log('\n✅ TypeScript SDK test successful!');
    console.log('\nTo test fully:');
    console.log('1. Open the operator URL above');
    console.log('2. Complete authentication');
    console.log('3. SDK will poll automatically and emit events');
  } catch (error) {
    console.error(`❌ Test failed: ${error}`);
    process.exit(1);
  }
}

testSync();
