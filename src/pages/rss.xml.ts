import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const posts = (await getCollection('blog', ({ data }) => !data.draft))
    .sort((a, b) => b.data.date.getTime() - a.data.date.getTime());

  return rss({
    title: 'chrisdlg.com',
    description: 'Field notes on infrastructure, security, and open source.',
    site: context.site!,
    // rel=self is the one spot the feed's own absolute URL belongs
    // (W3C feed validator flags its absence).
    xmlns: { atom: 'http://www.w3.org/2005/Atom' },
    customData: `<atom:link href="${new URL('rss.xml', context.site).href}" rel="self" type="application/rss+xml"/>`,
    items: posts.map((post) => ({
      title: post.data.title,
      pubDate: post.data.date,
      description: post.data.description,
      link: post.data.external ?? `/blog/${post.id}/`,
    })),
  });
}
