// 程式繪製的故事角色（SVG 字串產生器）
// 色票取自第 1 幕分鏡圖
const C = {
  cream: '#F7DCC1', moon: '#FDEDD4', peach: '#E6BEA7', apricot: '#E1A27C', lamp: '#F1BD89',
  rose: '#C3A197', mocha: '#AF8271', mauve: '#8F7073', cocoa: '#775244', brown: '#4F2F21', dark: '#2B1810',
  navy: '#3F476B', lav: '#908DB2', peri: '#BDBEE2', skin: '#FBE3D2', skinS: '#EFC3AA', blush: '#F2A7A0',
  gold: '#E9B96A', goldS: '#C98E4A', white: '#FFF9F2', pink: '#E8AFB4', red: '#D98A7E',
};

// 共用 defs：柔光漸層、陰影
function defs() {
  return `<defs>
  <radialGradient id="gSkin" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#FFF1E6"/><stop offset=".6" stop-color="${C.skin}"/><stop offset="1" stop-color="${C.skinS}"/></radialGradient>
  <radialGradient id="gHair" cx="35%" cy="25%" r="80%"><stop offset="0" stop-color="#7A5140"/><stop offset=".55" stop-color="${C.brown}"/><stop offset="1" stop-color="${C.dark}"/></radialGradient>
  <radialGradient id="gSun" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#FFF4C8"/><stop offset=".55" stop-color="#FFD27A"/><stop offset="1" stop-color="${C.apricot}"/></radialGradient>
  <radialGradient id="gGold" cx="35%" cy="30%" r="80%"><stop offset="0" stop-color="#FFF0C0"/><stop offset=".5" stop-color="${C.gold}"/><stop offset="1" stop-color="${C.goldS}"/></radialGradient>
  <radialGradient id="gMoon" cx="42%" cy="40%" r="60%"><stop offset="0" stop-color="#FFFDF5"/><stop offset=".7" stop-color="${C.moon}"/><stop offset="1" stop-color="#F3D9B8"/></radialGradient>
  <radialGradient id="gGlow"><stop offset="0" stop-color="#FFF6DC" stop-opacity=".95"/><stop offset=".35" stop-color="#FFE7B8" stop-opacity=".45"/><stop offset="1" stop-color="#FFE7B8" stop-opacity="0"/></radialGradient>
  <radialGradient id="gWarm"><stop offset="0" stop-color="${C.lamp}" stop-opacity=".85"/><stop offset="1" stop-color="${C.lamp}" stop-opacity="0"/></radialGradient>
  <linearGradient id="gLav" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E4DDF4"/><stop offset=".6" stop-color="${C.peri}"/><stop offset="1" stop-color="${C.lav}"/></linearGradient>
  <linearGradient id="gPink" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F9DCDA"/><stop offset="1" stop-color="${C.pink}"/></linearGradient>
  <linearGradient id="gMocha" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C79B85"/><stop offset="1" stop-color="${C.cocoa}"/></linearGradient>
  <linearGradient id="gRobe" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C98A86"/><stop offset="1" stop-color="#9C5E62"/></linearGradient>
  <linearGradient id="gCream" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${C.white}"/><stop offset="1" stop-color="${C.peach}"/></linearGradient>
  <filter id="fSoft" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="${C.dark}" flood-opacity=".22"/></filter>
  <filter id="fBlur"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="fBlurL"><feGaussianBlur stdDeviation="22"/></filter>
  </defs>`;
}

// 眼睛：open 0~1（眨眼），look 視線偏移，lash 睫毛
function eye(x, y, s, open = 1, look = [0, 0], lash = false, mood = 'normal') {
  const h = 30 * s * Math.max(open, 0.08);
  if (mood === 'happy') // 瞇眼笑 ^^
    return `<path d="M${x - 22 * s},${y + 4 * s} Q${x},${y - 20 * s} ${x + 22 * s},${y + 4 * s}" stroke="${C.dark}" stroke-width="${6 * s}" fill="none" stroke-linecap="round"/>`;
  let g = `<ellipse cx="${x}" cy="${y}" rx="${21 * s}" ry="${h}" fill="${C.dark}"/>`;
  if (open > 0.3) {
    g += `<ellipse cx="${x + look[0] * s}" cy="${y + 4 * s + look[1] * s}" rx="${15 * s}" ry="${h * 0.72}" fill="#6B3E2A"/>`;
    g += `<circle cx="${x + 7 * s + look[0] * s}" cy="${y - 9 * s + look[1] * s}" r="${7.5 * s}" fill="#fff"/>`;
    g += `<circle cx="${x - 7 * s + look[0] * s}" cy="${y + 10 * s + look[1] * s}" r="${3.5 * s}" fill="#fff" opacity=".85"/>`;
  }
  if (lash) g += `<path d="M${x - 22 * s},${y - h + 6 * s} Q${x},${y - h - 8 * s} ${x + 24 * s},${y - h + 2 * s} l${8 * s},${-6 * s}" stroke="${C.dark}" stroke-width="${4 * s}" fill="none" stroke-linecap="round"/>`;
  return g;
}

// 嘴巴：talk 0~1 開合，mood
function mouth(x, y, s, talk = 0, mood = 'smile') {
  if (mood === 'frown')
    return `<path d="M${x - 16 * s},${y + 8 * s} Q${x},${y - 6 * s} ${x + 16 * s},${y + 8 * s}" stroke="#8A4A3C" stroke-width="${5 * s}" fill="none" stroke-linecap="round"/>`;
  if (mood === 'worry')
    return `<path d="M${x - 12 * s},${y + 4 * s} Q${x - 4 * s},${y - 2 * s} ${x},${y + 3 * s} Q${x + 4 * s},${y + 8 * s} ${x + 12 * s},${y + 2 * s}" stroke="#8A4A3C" stroke-width="${4.5 * s}" fill="none" stroke-linecap="round"/>`;
  if (mood === 'o' || talk > 0.05) {
    const o = mood === 'o' ? 1 : talk;
    return `<ellipse cx="${x}" cy="${y + 4 * s}" rx="${(9 + 5 * o) * s}" ry="${(4 + 11 * o) * s}" fill="#9C4A45"/><ellipse cx="${x}" cy="${y + (8 + 6 * o) * s}" rx="${7 * s}" ry="${4 * o * s}" fill="#E48A87"/>`;
  }
  return `<path d="M${x - 15 * s},${y} Q${x},${y + 15 * s} ${x + 15 * s},${y}" stroke="#8A4A3C" stroke-width="${5 * s}" fill="none" stroke-linecap="round"/>`;
}

function face(o) { // 共用臉：o={s, blink, look, talk, mood, lash, brow}
  const s = o.s || 1;
  let g = `<ellipse cx="0" cy="0" rx="${118 * s}" ry="${108 * s}" fill="url(#gSkin)"/>`;
  g += `<ellipse cx="${-62 * s}" cy="${32 * s}" rx="${22 * s}" ry="${13 * s}" fill="${C.blush}" opacity=".55"/><ellipse cx="${62 * s}" cy="${32 * s}" rx="${22 * s}" ry="${13 * s}" fill="${C.blush}" opacity=".55"/>`;
  const em = o.mood === 'happy' ? 'happy' : 'normal';
  g += eye(-44 * s, 0, s, o.blink ?? 1, o.look || [0, 0], o.lash, em) + eye(44 * s, 0, s, o.blink ?? 1, o.look || [0, 0], o.lash, em);
  if (o.brow === 'angry') g += `<path d="M${-72 * s},${-50 * s} L${-22 * s},${-32 * s} M${72 * s},${-50 * s} L${22 * s},${-32 * s}" stroke="${C.dark}" stroke-width="${9 * s}" stroke-linecap="round"/>`;
  else if (o.brow === 'worry') g += `<path d="M${-66 * s},${-38 * s} Q${-44 * s},${-54 * s} ${-24 * s},${-48 * s} M${66 * s},${-38 * s} Q${44 * s},${-54 * s} ${24 * s},${-48 * s}" stroke="${C.brown}" stroke-width="${6 * s}" fill="none" stroke-linecap="round"/>`;
  g += `<ellipse cx="0" cy="${22 * s}" rx="${6 * s}" ry="${4 * s}" fill="${C.skinS}"/>`;
  g += mouth(0, 50 * s, s, o.talk || 0, o.mouth || 'smile');
  return g;
}

// 波浪瀏海：從 x0 到 x1，n 束
function fringe(x0, x1, y, depth, n) {
  const w = (x1 - x0) / n; let d = `M${x0},${y - 10}`;
  for (let k = 0; k < n; k++) { const a = x0 + k * w; d += ` Q${a + w / 2},${y + depth} ${a + w},${y - 10}`; }
  d += ` Q${x1 + 8},${y - 90} 0,${y - 92} Q${x0 - 8},${y - 90} ${x0},${y - 10}Z`;
  return `<path d="${d}" fill="url(#gHair)"/>`;
}
function shine(r) { return `<path d="M${-r * 0.7},${-r * 0.55} Q${-r * 0.2},${-r * 0.95} ${r * 0.45},${-r * 0.78}" stroke="#A77A62" stroke-width="${r * 0.08}" fill="none" stroke-linecap="round" opacity=".7"/>`; }

// 通用 Q 版身體（衣服色、手臂角度）
function arm(x, y, ang, len, col, s) {
  return `<g transform="translate(${x},${y}) rotate(${ang})"><rect x="${-17 * s}" y="0" width="${34 * s}" height="${len * s}" rx="${17 * s}" fill="${col}"/><circle cx="0" cy="${len * s}" r="${17 * s}" fill="url(#gSkin)"/></g>`;
}

// ---------- 后羿（英雄 / 國王） ----------
function houyi(o) {
  // o: {x,y,sc,t,blink,talk,king,armL,armR,bow,draw,bob}
  const s = 1, t = o.t || 0;
  const robe = o.king ? 'url(#gRobe)' : 'url(#gMocha)';
  let g = `<g transform="translate(${o.x},${o.y + (o.bob || 0)}) scale(${o.sc || 1})" filter="url(#fSoft)">`;
  // 腳
  g += `<ellipse cx="-40" cy="245" rx="34" ry="20" fill="${C.cocoa}"/><ellipse cx="40" cy="245" rx="34" ry="20" fill="${C.cocoa}"/>`;
  g += `<rect x="-58" y="175" width="40" height="70" rx="16" fill="${C.cream}"/><rect x="18" y="175" width="40" height="70" rx="16" fill="${C.cream}"/>`;
  // 身體
  g += `<path d="M-90,70 Q-100,200 -80,205 L80,205 Q100,200 90,70 Q0,40 -90,70Z" fill="${robe}"/>`;
  g += `<rect x="-88" y="150" width="176" height="24" rx="10" fill="${o.king ? C.gold : C.apricot}"/>`;
  g += `<path d="M-30,62 L0,120 L30,62" fill="${o.king ? '#F3D6A0' : C.cream}"/>`;
  // 手臂
  g += arm(-82, 85, o.armL ?? 20, 95, o.king ? '#B8767A' : '#A8806E', s);
  g += arm(82, 85, o.armR ?? -20, 95, o.king ? '#B8767A' : '#A8806E', s);
  // 頭
  g += `<g transform="translate(0,-60) rotate(${o.tilt || 0})">`;
  g += `<path d="M-125,-10 Q-130,-130 0,-135 Q130,-130 125,-10 Q100,-80 0,-85 Q-100,-80 -125,-10Z" fill="url(#gHair)"/>`;
  g += face({ s: 1, blink: o.blink, talk: o.talk, mood: o.mood, mouth: o.mouth, brow: o.brow, look: o.look });
  g += `<path d="M-128,-20 Q-135,-135 0,-138 Q135,-135 128,-20 Q110,-70 0,-72 Q-110,-70 -128,-20Z" fill="url(#gHair)"/>` + fringe(-112, 112, -48, 34, 6) + shine(120);
  g += `<path d="M-10,-132 q-20,-40 20,-50 q-10,25 5,45" fill="${C.brown}"/>`; // 呆毛
  if (o.king) {
    g += `<path d="M-80,-95 L-70,-160 L-35,-120 L0,-175 L35,-120 L70,-160 L80,-95Z" fill="url(#gGold)" stroke="${C.goldS}" stroke-width="4"/>`;
    g += `<circle cx="0" cy="-130" r="10" fill="${C.red}"/>`;
  } else {
    // 頭帶 + 飄帶
    const w = Math.sin(t * 6) * 10;
    g += `<path d="M-122,-52 Q0,-90 122,-52 L118,-32 Q0,-70 -118,-32Z" fill="${C.red}"/>`;
    g += `<path d="M118,-45 Q170,${-60 + w} 205,${-30 + w} Q170,${-35 + w} 150,${-20 + w / 2} Q175,${0 + w} 190,${25 + w} Q150,${5 + w} 116,-35Z" fill="${C.red}"/>`;
  }
  g += `</g>`;
  if (o.bow) { const a = (o.armR ?? -20) * Math.PI / 180; g += `<g transform="translate(${82 - 95 * Math.sin(a)},${85 + 95 * Math.cos(a)}) rotate(${(o.armR ?? -20) + 90}) scale(.72)">` + bow(o.draw || 0) + `</g>`; }
  g += `</g>`;
  return g;
}

// 弓（在角色座標系，右手持弓往右上瞄準）
function bow(draw) {
  const pull = 60 * draw;
  return `<g>
  <path d="M0,-150 Q90,0 0,150" stroke="${C.cocoa}" stroke-width="16" fill="none" stroke-linecap="round"/>
  <path d="M0,-150 L${-pull},0 L0,150" stroke="${C.cream}" stroke-width="4" fill="none"/>
  ${draw > 0.05 ? `<line x1="${-pull}" y1="0" x2="${110}" y2="0" stroke="${C.brown}" stroke-width="8" stroke-linecap="round"/><path d="M110,-14 L140,0 L110,14Z" fill="${C.gold}"/><path d="M${-pull},0 l-22,-14 M${-pull},0 l-22,14" stroke="${C.pink}" stroke-width="7" stroke-linecap="round"/>` : ''}
  </g>`;
}

// ---------- 嫦娥 ----------
function change(o) {
  // o: {x,y,sc,t,blink,talk,mood,brow,fly(0~1),armL,armR}
  const t = o.t || 0, f = o.fly || 0;
  const wave = (k) => Math.sin(t * 3 + k) * (18 + 30 * f);
  let g = `<g transform="translate(${o.x},${o.y}) scale(${o.sc || 1}) rotate(${o.rot || 0})" filter="url(#fSoft)">`;
  // 飄帶（飛起來時變長）
  const L = 160 + 260 * f;
  g += `<path d="M-95,90 C-200,${150 + wave(0)} -150,${220 + wave(1)} -230,${L + wave(2)}" stroke="${C.pink}" stroke-width="18" fill="none" stroke-linecap="round" opacity=".9"/>`;
  g += `<path d="M95,90 C200,${150 + wave(2)} 150,${230 + wave(3)} 240,${L + 20 + wave(4)}" stroke="${C.peri}" stroke-width="18" fill="none" stroke-linecap="round" opacity=".9"/>`;
  // 裙擺
  const sw = Math.sin(t * 2.5) * 12 * (0.4 + f);
  g += `<path d="M-80,70 Q-150,${240 + sw} -160,${280 + sw} Q0,${320 - sw} 160,${280 - sw} Q150,${240 - sw} 80,70 Q0,45 -80,70Z" fill="url(#gLav)"/>`;
  g += `<path d="M-60,70 Q-80,200 -60,290 Q0,300 60,290 Q80,200 60,70Z" fill="url(#gPink)" opacity=".9"/>`;
  g += `<rect x="-70" y="135" width="140" height="22" rx="10" fill="${C.mauve}"/>`;
  g += `<path d="M-35,62 L0,115 L35,62" fill="${C.white}"/>`;
  // 寬袖手臂
  const sleeve = (x, ang, flip) => `<g transform="translate(${x},82) rotate(${ang})"><path d="M-22,0 Q${flip * -40},90 ${flip * -10},120 L${flip * 45},115 Q${flip * 30},60 22,0Z" fill="url(#gLav)"/><circle cx="${flip * 12}" cy="112" r="16" fill="url(#gSkin)"/></g>`;
  g += sleeve(-78, o.armL ?? 25, 1) + sleeve(78, o.armR ?? -25, -1);
  // 頭
  g += `<g transform="translate(0,-62) rotate(${o.tilt || 0})">`;
  g += `<circle cx="-95" cy="-115" r="48" fill="url(#gHair)"/><circle cx="95" cy="-115" r="48" fill="url(#gHair)"/>`;
  g += `<path d="M-128,40 Q-150,-120 0,-130 Q150,-120 128,40 L110,90 Q120,-40 0,-80 Q-120,-40 -110,90Z" fill="url(#gHair)"/>`;
  g += face({ s: 1, blink: o.blink, talk: o.talk, mood: o.mood, mouth: o.mouth, brow: o.brow, lash: true, look: o.look });
  g += `<path d="M-126,-10 Q-135,-128 0,-130 Q135,-128 126,-10 Q110,-66 0,-68 Q-110,-66 -126,-10Z" fill="url(#gHair)"/>` + fringe(-110, 110, -44, 40, 7) + shine(120);
  // 髮飾
  g += `<circle cx="-70" cy="-120" r="14" fill="${C.pink}"/><circle cx="-52" cy="-128" r="10" fill="${C.white}"/><circle cx="70" cy="-120" r="14" fill="${C.pink}"/><circle cx="88" cy="-112" r="9" fill="${C.peri}"/>`;
  g += `</g></g>`;
  return g;
}

// ---------- 小村民 ----------
function villager(o) {
  // o: {x,y,sc,t,hat,col,blink,mood,armL,armR,hop,talk,sweat,brow}
  const col = o.col || 'url(#gMocha)';
  let g = `<g transform="translate(${o.x},${o.y - (o.hop || 0)}) scale(${o.sc || 1})" filter="url(#fSoft)">`;
  g += `<ellipse cx="-30" cy="200" rx="26" ry="15" fill="${C.cocoa}"/><ellipse cx="30" cy="200" rx="26" ry="15" fill="${C.cocoa}"/>`;
  g += `<path d="M-70,60 Q-80,170 -60,195 L60,195 Q80,170 70,60 Q0,35 -70,60Z" fill="${col}"/>`;
  g += `<rect x="-70" y="130" width="140" height="18" rx="8" fill="${C.cream}" opacity=".85"/>`;
  g += arm(-64, 72, o.armL ?? 18, 75, col, 1) + arm(64, 72, o.armR ?? -18, 75, col, 1);
  g += `<g transform="translate(0,-40) scale(.82)">`;
  g += `<path d="M-120,0 Q-130,-125 0,-128 Q130,-125 120,0 Q110,-70 0,-75 Q-110,-70 -120,0Z" fill="url(#gHair)"/>`;
  g += face({ s: 1, blink: o.blink, talk: o.talk, mood: o.mood, mouth: o.mouth, brow: o.brow, look: o.look });
  g += fringe(-108, 108, -52, 32, 5) + shine(118);
  if (o.hat) g += `<path d="M-200,-40 Q-120,-80 -20,-175 Q0,-190 20,-175 Q120,-80 200,-40 Q0,-70 -200,-40Z" fill="#E7C98E"/><path d="M-200,-40 Q0,-70 200,-40 Q0,-55 -200,-40Z" fill="#C9A66A"/><path d="M-60,-120 Q0,-100 60,-120" stroke="#D0AE70" stroke-width="6" fill="none"/>`;
  if (o.bun) g += `<circle cx="0" cy="-130" r="38" fill="url(#gHair)"/><rect x="-20" y="-110" width="40" height="10" rx="5" fill="${C.pink}"/>`;
  if (o.sweat) for (let k = 0; k < 2; k++) {
    const u = ((o.t || 0) * 0.9 + k * 0.5) % 1;
    g += `<path transform="translate(${k ? 105 : -115},${-40 + u * 80})" d="M0,-18 Q14,4 0,12 Q-14,4 0,-18Z" fill="#CFE0F5" opacity="${Math.sin(u * Math.PI)}"/>`;
  }
  g += `</g></g>`;
  return g;
}

// ---------- 太陽 ----------
function sun(o) {
  // o: {x,y,r,t,i,blink,mood,sweat,alpha,rot}
  const r = o.r || 80, t = o.t || 0;
  let g = `<g transform="translate(${o.x},${o.y}) rotate(${o.rot || 0})" opacity="${o.alpha ?? 1}">`;
  g += `<circle r="${r * 2.1}" fill="url(#gGlow)"/>`;
  let rays = '';
  for (let k = 0; k < 12; k++) {
    const a = k * 30 + t * 20, rr = r * (1.28 + 0.06 * Math.sin(t * 5 + k));
    rays += `<path transform="rotate(${a})" d="M${-r * 0.22},${-r * 0.9} Q0,${-rr - r * 0.2} ${r * 0.22},${-r * 0.9}Z" fill="#FFC36B"/>`;
  }
  g += rays + `<circle r="${r}" fill="url(#gSun)"/>`;
  g += `<g transform="scale(${r / 150})">` + face({ s: 1, blink: o.blink, mood: o.mood, mouth: o.mouth, talk: o.talk, brow: o.brow }).replace('url(#gSkin)', 'none') + `</g>`;
  if (o.sweat) {
    const u = (t * 0.8 + (o.i || 0) * 0.37) % 1;
    g += `<path transform="translate(${r * 0.8},${-r * 0.2 + u * r * 0.6})" d="M0,-16 Q13,4 0,11 Q-13,4 0,-16Z" fill="#CFE0F5" opacity="${Math.sin(u * Math.PI)}"/>`;
  }
  return g + `</g>`;
}

// ---------- 玉兔 ----------
function rabbit(o) {
  const t = o.t || 0;
  let g = `<g transform="translate(${o.x},${o.y - (o.hop || 0)}) scale(${o.sc || 1})" filter="url(#fSoft)">`;
  g += `<ellipse cx="-28" cy="-120" rx="20" ry="58" fill="${C.white}" transform="rotate(${-10 + Math.sin(t * 3) * 5},-28,-70)"/><ellipse cx="-28" cy="-120" rx="9" ry="40" fill="${C.pink}" transform="rotate(${-10 + Math.sin(t * 3) * 5},-28,-70)"/>`;
  g += `<ellipse cx="28" cy="-120" rx="20" ry="58" fill="${C.white}" transform="rotate(${12 + Math.sin(t * 3 + 1) * 5},28,-70)"/><ellipse cx="28" cy="-120" rx="9" ry="40" fill="${C.pink}" transform="rotate(${12 + Math.sin(t * 3 + 1) * 5},28,-70)"/>`;
  g += `<ellipse cx="0" cy="40" rx="75" ry="65" fill="${C.white}"/><ellipse cx="0" cy="-30" rx="70" ry="60" fill="${C.white}"/>`;
  g += eye(-26, -35, 0.6, o.blink ?? 1) + eye(26, -35, 0.6, o.blink ?? 1);
  g += `<ellipse cx="-44" cy="-10" rx="12" ry="7" fill="${C.blush}" opacity=".6"/><ellipse cx="44" cy="-10" rx="12" ry="7" fill="${C.blush}" opacity=".6"/>`;
  g += `<path d="M-6,-14 Q0,-8 6,-14" stroke="${C.mauve}" stroke-width="4" fill="none" stroke-linecap="round"/>`;
  return g + `</g>`;
}

function mooncake(x, y, r, rot = 0) {
  let petals = '';
  for (let k = 0; k < 8; k++) petals += `<ellipse transform="rotate(${k * 45})" cx="0" cy="${-r * 0.45}" rx="${r * 0.14}" ry="${r * 0.26}" fill="none" stroke="${C.cocoa}" stroke-width="${r * 0.05}" opacity=".6"/>`;
  return `<g transform="translate(${x},${y}) rotate(${rot})"><ellipse cx="0" cy="${r * 0.25}" rx="${r}" ry="${r * 0.55}" fill="${C.cocoa}"/><circle r="${r}" fill="url(#gGold)"/><circle r="${r * 0.8}" fill="none" stroke="${C.goldS}" stroke-width="${r * 0.06}"/>${petals}<circle r="${r * 0.14}" fill="${C.goldS}" opacity=".7"/></g>`;
}

function lantern(x, y, sc, rot, glow = 1) {
  return `<g transform="translate(${x},${y}) rotate(${rot}) scale(${sc})"><line x1="0" y1="-200" x2="0" y2="-80" stroke="${C.cocoa}" stroke-width="4"/>
  <circle cy="0" r="170" fill="url(#gWarm)" opacity="${0.6 * glow}"/>
  <rect x="-30" y="-92" width="60" height="18" rx="6" fill="${C.goldS}"/><ellipse cx="0" cy="0" rx="80" ry="78" fill="${C.red}"/><ellipse cx="-18" cy="-18" rx="40" ry="44" fill="#F0B3A2" opacity=".55"/>
  <path d="M-40,-72 Q-60,0 -40,72 M0,-78 L0,78 M40,-72 Q60,0 40,72" stroke="#B86A62" stroke-width="4" fill="none"/>
  <rect x="-30" y="74" width="60" height="16" rx="6" fill="${C.goldS}"/><path d="M-10,90 L-14,150 M0,90 L0,160 M10,90 L14,150" stroke="${C.gold}" stroke-width="6" stroke-linecap="round"/></g>`;
}

function elixir(x, y, sc, t) {
  let sp = '';
  for (let k = 0; k < 6; k++) { const a = t * 1.8 + k * 1.05; sp += star(x + Math.cos(a) * 95 * sc, y + Math.sin(a) * 80 * sc, (12 + 6 * Math.sin(t * 6 + k)) * sc, '#FFF6D8'); }
  return `<circle cx="${x}" cy="${y}" r="${150 * sc}" fill="url(#gGlow)"/><circle cx="${x}" cy="${y}" r="${38 * sc}" fill="#FFF7E0"/><circle cx="${x}" cy="${y}" r="${30 * sc}" fill="url(#gGold)"/><circle cx="${x - 10 * sc}" cy="${y - 10 * sc}" r="${8 * sc}" fill="#fff" opacity=".9"/>` + sp;
}

function star(x, y, r, col = '#FFF1C8', op = 1) {
  const k = r * 0.3;
  return `<path d="M${x},${y - r} L${x + k},${y - k} L${x + r},${y} L${x + k},${y + k} L${x},${y + r} L${x - k},${y + k} L${x - r},${y} L${x - k},${y - k}Z" fill="${col}" opacity="${op}"/>`;
}
