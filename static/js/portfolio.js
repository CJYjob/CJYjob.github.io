(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('portfolio-data').textContent);
  const inputs = [...document.querySelectorAll('[name="showcase-topic"]')];
  const allowed = inputs.map(input => input.value);
  const grid = document.getElementById('featured-work');
  const labels = {security:'보안', ai:'AI', development:'개발'};
  function read() {
    const values = new URLSearchParams(location.search).getAll('topics').flatMap(v => v.split(',')).map(v => v.trim().toLowerCase());
    inputs.forEach(input => { input.checked = values.includes(input.value); });
  }
  function render(update) {
    const fields = inputs.filter(i => i.checked).map(i => i.value);
    const projects = data.projects.filter(p => !fields.length || fields.some(f => p.categories.includes(f)))
      .sort((a,b) => a.rank - b.rank || a.title.localeCompare(b.title));
    grid.replaceChildren();
    for (const p of projects) {
      const article = document.createElement('article'); article.className = 'project-card';
      const badge = document.createElement('p'); badge.className = 'project-kind'; badge.textContent = p.kind;
      const h = document.createElement('h3'); const link = document.createElement('a'); link.href = p.url; link.textContent = p.title; h.append(link);
      const summary = document.createElement('p'); summary.textContent = p.summary;
      const proof = document.createElement('p'); proof.className = 'project-evidence'; proof.textContent = p.evidence;
      const tags = document.createElement('p'); tags.className = 'project-fields'; tags.textContent = p.categories.filter(f => allowed.includes(f)).map(f => labels[f]).join(' · ');
      article.append(badge,h,summary,proof,tags); grid.append(article);
    }
    document.getElementById('work-count').textContent = `${projects.length}개 작업`;
    document.getElementById('featured-empty').hidden = projects.length !== 0;
    document.getElementById('field-description').textContent = fields.map(f => data.fields[f]).join(' ');
    const more = new URL(data.explore, location.origin); more.searchParams.set('scope','portfolio');
    if (fields.length) more.searchParams.set('topics',fields.join(','));
    for (const id of ['all-materials','more-materials']) document.getElementById(id).href = more.pathname + more.search;
    if (update) { const url = new URL(location.href); url.searchParams.delete('topics'); if(fields.length) url.searchParams.set('topics',fields.join(',')); history.replaceState(null,'',url.pathname+url.search+url.hash); }
  }
  read(); render(false); inputs.forEach(i => i.addEventListener('change',() => render(true)));
  window.addEventListener('popstate',() => {read();render(false);});
})();
