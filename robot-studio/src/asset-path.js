export const siteBase = import.meta.env.BASE_URL;
export const modelUrl = (file = '') => `${siteBase}models/so101/${file}`;

// Existing panels contain many generated STL/3MF links. Keep those links
// project-relative when GitHub Pages serves the app under /thenar-arms/.
export function installModelLinkRewriter(root = document) {
  if (siteBase === '/') return;
  const rewrite = node => {
    if (!(node instanceof Element)) return;
    const links = node.matches('a[href]') ? [node] : [];
    links.push(...node.querySelectorAll('a[href]'));
    for (const link of links) {
      const href = link.getAttribute('href');
      if (href?.startsWith('/models/so101/')) {
        link.setAttribute('href', modelUrl(href.slice('/models/so101/'.length)));
      }
    }
  };
  rewrite(root.documentElement ?? root);
  new MutationObserver(records => {
    for (const record of records) {
      if (record.type === 'attributes') rewrite(record.target);
      else for (const node of record.addedNodes) rewrite(node);
    }
  }).observe(root.documentElement ?? root, {subtree: true, childList: true, attributes: true, attributeFilter: ['href']});
}
