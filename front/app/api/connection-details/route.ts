// front/app/api/connection-details/route.ts
import { NextResponse }      from 'next/server';
import { AccessToken }       from 'livekit-server-sdk';
import type { VideoGrant }   from 'livekit-server-sdk';

const WS_URL     = process.env.LIVEKIT_URL!;
const API_KEY    = process.env.LIVEKIT_API_KEY!;
const API_SECRET = process.env.LIVEKIT_API_SECRET!;

export async function GET(req: Request) {
  const { searchParams } = new globalThis.URL(req.url);
  const room     = searchParams.get('room')     || 'dev';
  const identity = searchParams.get('identity') || 'guest';

  // build the LiveKit token
  const at = new AccessToken(API_KEY, API_SECRET, { identity });
  const grant: VideoGrant = { room, roomJoin: true };
  at.addGrant(grant);

  // await the promise so token is a string
  const token = await at.toJwt();

  return NextResponse.json({
    serverUrl:        WS_URL,       // renamed from "url"
    apiKey:           API_KEY,
    participantToken: token,        // renamed from "token"
  });
}