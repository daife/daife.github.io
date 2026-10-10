"""Generate a buildless GitHub Pages portfolio from reviewed project data."""
import json
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    'agent': ('AI 应用与 Agent', '从工具调用、生成校验，到多端同步与记忆内核。'),
    'game': ('游戏模组与自动化', '围绕虚拟玩家、控制权与游戏互动扩展系统能力。'),
    'robot': ('机器人与嵌入式', '把感知、通信、控制与操作界面连接到硬件。'),
    'compute': ('NPU、通信与状态估计', '计算图部署、算子调优与滤波方法的工程探索。'),
    'vision': ('视觉、OCR 与语言工具', '从文字采集、图像识别，到词汇与假名学习。'),
    'tool': ('独立工具与运行时', '围绕桌面、移动端和底层运行时解决具体问题。'),
    'web': ('Web 产品与协作', '账号、问卷、匹配与多端入口的产品实践。'),
    'opensource': ('开源二次开发', '在上游基础上处理输入交互、图形运行时和版本适配。'),
    'learning': ('课程实践与科研复现', '把算法、论文与实验流程落实为可检查的工程。'),
}

def links(items):
    return ''.join(f'<a href="{e(i["url"], quote=True)}">{e(i["label"] if "label" in i else i["name"])} <span aria-hidden="true">↗</span></a>' for i in items)

def card(p, featured=False):
    search = ' '.join([p['name'], CATEGORIES[p['category']][0], p['summary'], p['kind'], *p['tags'], *p['highlights'], p['note']]).casefold()
    tags = ''.join(f'<li>{e(t)}</li>' for t in p['tags'])
    bullets = ''.join(f'<li>{e(h)}</li>' for h in p['highlights'])
    details = ''
    if bullets or p['note'] or p['evidence']:
        details = '<details><summary>实现亮点与说明</summary><div class="detail-body">'
        if bullets: details += f'<ul class="highlights">{bullets}</ul>'
        if p['note']: details += f'<p class="note">{e(p["note"])}</p>'
        if p.get('upstream'): details += f'<div class="upstream">{links([p["upstream"]])}</div>'
        if p['evidence']: details += f'<div class="evidence"><span>代码与提交</span>{links(p["evidence"])}</div>'
        details += '</div></details>'
    repo_links = links(p['repos']) if p['repos'] else '<span class="private-note">源码未公开 · 可阅读项目概要</span>'
    return f'''<article class="project-card {'featured-card' if featured else ''}" id="{e(p['id'])}" data-project data-category="{p['category']}" data-search="{e(search, quote=True)}">
<div class="card-top"><span class="project-kind">{e(p['kind'])}</span><span class="visibility {'private' if p['visibility'] != '公开源码' else ''}">{p['visibility']}</span></div>
<h3><a class="permalink" href="#{p['id']}">{e(p['name'])}</a></h3>
<p class="description">{e(p['summary'])}</p><ul class="tags" aria-label="技术栈">{tags}</ul>
{details}<div class="repo-links">{repo_links}</div></article>'''

def build():
    data = json.loads((ROOT / 'projects.json').read_text())
    projects = data['projects']
    ids = [p['id'] for p in projects]
    assert len(ids) == len(set(ids)), 'Duplicate project IDs'
    assert all(p['category'] in CATEGORIES for p in projects)
    featured = [p for p in projects if p['featured']]
    output = '<section class="project-section" data-section><div class="section-heading"><div><span class="eyebrow">SELECTED WORK</span><h2>精选项目</h2><p>六个切面，认识我关注的问题与实现方式。</p></div><span class="section-count">06</span></div><div class="featured-grid">'
    output += ''.join(card(p, True) for p in featured) + '</div></section>'
    for idx, (key, (name, description)) in enumerate(CATEGORIES.items(), 1):
        group = [p for p in projects if p['category'] == key and not p['featured']]
        if not group: continue
        output += f'<section class="project-section" data-section><div class="section-heading"><div><span class="eyebrow">{idx:02d} / EXPLORE</span><h2>{name}</h2><p>{description}</p></div><span class="section-count">{len(group):02d}</span></div><div class="project-grid">'
        output += ''.join(card(p) for p in group) + '</div></section>'
    counts = {k: sum(p['category'] == k for p in projects) for k in CATEGORIES}
    filters = '<button type="button" class="filter active" data-filter="all" aria-pressed="true">全部 <span>'+str(len(projects))+'</span></button>'
    filters += ''.join(f'<button type="button" class="filter" data-filter="{k}" aria-pressed="false">{v[0]} <span>{counts[k]}</span></button>' for k,v in CATEGORIES.items())
    template = (ROOT / 'templates/index.html').read_text()
    for key,value in {'PROJECTS':output, 'FILTERS':filters, 'TOTAL':str(len(projects)), 'UPDATED':data['updated'], 'EVIDENCE_DATE':data['evidence_date']}.items():
        template = template.replace('{{'+key+'}}', value)
    assert '{{' not in template, 'Unresolved template placeholder'
    (ROOT / 'index.html').write_text(template)
    print(f'Built {len(projects)} project groups, {len(featured)} featured, {len(CATEGORIES)} directions.')

if __name__ == '__main__':
    build()
