// Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
// SPDX-License-Identifier: CC-BY-NC-ND-4.0

import type { Handle } from '@sveltejs/kit';
import { checkPublicLimit, getIdentifier } from '$lib/server/ratelimit';

export const handle: Handle = async ({ event, resolve }) => {
	// Skip static assets and internal Svelte routes
	if (event.url.pathname.startsWith('/_app') || event.url.pathname.startsWith('/favicon')) {
		return resolve(event);
	}

	// Apply rate limiting (observation-only, fail-closed for requester)
	const identifier = getIdentifier(event.request);
	const { success, limit, remaining, reset } = await checkPublicLimit(identifier);

	if (!success) {
		// Rate limit exceeded: fail closed for this requester
		return new Response('Too Many Requests', {
			status: 429,
			headers: {
				'X-RateLimit-Limit': limit.toString(),
				'X-RateLimit-Remaining': remaining.toString(),
				'X-RateLimit-Reset': reset.toString(),
				'Retry-After': Math.ceil((reset - Date.now()) / 1000).toString()
			}
		});
	}

	const response = await resolve(event);

	// Expose soft headers for well-behaved clients (informational, not enforced)
	response.headers.set('X-RateLimit-Limit', limit.toString());
	response.headers.set('X-RateLimit-Remaining', remaining.toString());
	response.headers.set('X-RateLimit-Reset', reset.toString());

	return response;
};
