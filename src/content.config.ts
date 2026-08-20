import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({
    pattern: '**/*.md',
    base: './src/content/blog',
    generateId: ({ entry }: { entry: string }) => entry.replace(/\.mdx?$/, ''),
  }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    description: z.string(),
    tags: z.array(z.string()).optional().default([]),
    draft: z.boolean().optional().default(false),
    // Linkpost: published elsewhere (e.g. the Teleport blog). Entries with
    // `external` render in lists pointing at the canonical URL and get no
    // local page.
    external: z.string().url().optional(),
  }),
});

export const collections = { blog };
