// Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
// SPDX-License-Identifier: Apache-2.0

import { listDocs } from '$lib/docs.js';

export const prerender = true;

export function load() {
  return { docs: listDocs() };
}
