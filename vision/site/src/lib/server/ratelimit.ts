// Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
// SPDX-License-Identifier: CC-BY-NC-ND-4.0

import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';
import {
	KV_REST_API_URL,
	KV_REST_API_TOKEN
} from '$env/static/private';

// Shared Redis client (server-only)
const redis = new Redis({
	url: KV_REST_API_URL,
	token: KV_REST_API_TOKEN
});

/**
 * General public surface limiter
 * 60 requests per minute per identifier
 */
export const publicLimiter = new Ratelimit({
	redis,
	limiter: Ratelimit.slidingWindow(60, '1 m'),
	analytics: true,
	prefix: 'ratelimit:public'
});

/**
 * Stricter limiter for any future claim / form endpoints
 * 10 requests per minute
 */
export const strictLimiter = new Ratelimit({
	redis,
	limiter: Ratelimit.slidingWindow(10, '1 m'),
	analytics: true,
	prefix: 'ratelimit:strict'
});

/**
 * Helper — returns a safe identifier without storing PII
 * Prefer a hashed or ephemeral value if stronger privacy is required
 */
export function getIdentifier(request: Request): string {
	// Vercel / edge commonly provide this
	const forwarded = request.headers.get('x-forwarded-for');
	if (forwarded) {
		return forwarded.split(',')[0].trim();
	}
	// Fallback — still better than a global bucket
	return 'anonymous';
}
