// 第 2～6 幕：renderScene(i, t, d, cue) 回傳整張 1080x1920 SVG 內容
const W = 1080, H = 1920;
const clamp = (v, a = 0, b = 1) => Math.min(Math.max(v, a), b);
const seg = (t, a, b) => clamp((t - a) / (b - a));
const ease = (t) => { t = clamp(t); return t * t * (3 - 2 * t); };
const back = (t) => { t = clamp(t); const c = 1.70158; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2; };
const blinkAt = (t, ph = 0) => { const u = (t + ph) % 3.1; return u < 0.12 ? Math.abs(u - 0.06) / 0.06 : 1; };
const rnd = (i) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

function camera(inner, z, cx, cy) { // 以 (cx,cy) 為畫面中心放大 z
  return `<g transform="translate(${W / 2},${H / 2}) scale(${z}) translate(${-cx},${-cy})">${inner}</g>`;
}
function stars(t, n, ymax, seed = 0) {
  let g = '';
  for (let k = 0; k < n; k++) g += star(rnd(k + seed) * W, rnd(k + seed + 50) * ymax, 6 + 10 * rnd(k + seed + 90), '#FFF4D6', 0.35 + 0.65 * Math.abs(Math.sin(t * 1.5 + k)));
  return g;
}
function cloud(x, y, s, col, op = 1) {
  return `<g transform="translate(${x},${y}) scale(${s})" opacity="${op}"><ellipse cx="0" cy="0" rx="140" ry="55" fill="${col}"/><circle cx="-60" cy="-30" r="60" fill="${col}"/><circle cx="30" cy="-50" r="75" fill="${col}"/><circle cx="95" cy="-15" r="50" fill="${col}"/></g>`;
}
function arrowFx(x0, y0, x1, y1, k) { // 箭飛行 k∈[0,1]
  const x = x0 + (x1 - x0) * k, y = y0 + (y1 - y0) * k, a = Math.atan2(y1 - y0, x1 - x0) * 180 / Math.PI;
  return `<g transform="translate(${x},${y}) rotate(${a})"><path d="M-330,0 L-60,0" stroke="#FFF3D0" stroke-width="30" stroke-linecap="round" opacity=".45" filter="url(#fBlur)"/>
  <line x1="-120" y1="0" x2="10" y2="0" stroke="${C.brown}" stroke-width="9" stroke-linecap="round"/><path d="M8,-17 L46,0 L8,17Z" fill="${C.gold}"/><path d="M-120,0 l-26,-18 M-120,0 l-26,18 M-100,0 l-26,-18 M-100,0 l-26,18" stroke="${C.pink}" stroke-width="8" stroke-linecap="round"/></g>`;
}
function burst(x, y, k, n = 10, R = 190) {
  let g = `<circle cx="${x}" cy="${y}" r="${60 + 160 * k}" fill="url(#gGlow)" opacity="${1 - k}"/>`;
  for (let q = 0; q < n; q++) { const a = q / n * Math.PI * 2; g += star(x + Math.cos(a) * R * k, y + Math.sin(a) * R * k, 34 * (1 - k) + 6, q % 2 ? '#FFF1C8' : C.peri, 1 - k); }
  return g;
}

// ---------------- 2 十個太陽 ----------------
const SUN2 = [[170, 190], [450, 130], [760, 170], [960, 330], [300, 410], [610, 360], [850, 560], [140, 650], [470, 640], [720, 800]];
function scene2(t, d, cue) {
  const u = t / d;
  let g = `<rect x="-500" y="-600" width="${W+1000}" height="${H+1200}" fill="url(#sky2)"/>`;
  g += `<defs><linearGradient id="sky2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBE9D2"/><stop offset=".45" stop-color="#F6C9A0"/><stop offset=".62" stop-color="${C.apricot}"/></linearGradient>
  <linearGradient id="gnd2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D9A585"/><stop offset="1" stop-color="${C.mocha}"/></linearGradient></defs>`;
  g += `<path d="M0,1180 Q200,1060 420,1140 Q640,1030 860,1120 Q980,1080 1080,1110 L1080,1300 L0,1300Z" fill="${C.rose}" opacity=".8"/>`;
  g += `<path d="M0,1230 Q300,1180 540,1220 Q800,1170 1080,1210 L1600,1210 L1600,2600 L-500,2600 L-500,1230Z" fill="url(#gnd2)"/>`;
  // 地面龜裂（慢慢長出來）
  const cr = ease(seg(t, cue.crack ?? d * 0.45, (cue.crack ?? d * 0.45) + 1.4));
  for (let k = 0; k < 7; k++) {
    const x = 90 + k * 150 + rnd(k) * 60, y = 1330 + rnd(k + 9) * 420;
    let p = `M${x},${y}`; for (let j = 1; j <= 5; j++) p += ` L${x + j * 38 * (rnd(k * 7 + j) > .5 ? 1 : -.6)},${y + j * 34}`;
    g += `<path d="${p}" stroke="${C.cocoa}" stroke-width="7" fill="none" stroke-linecap="round" stroke-dasharray="400" stroke-dashoffset="${400 * (1 - cr)}" opacity=".8"/>`;
  }
  // 乾草、小屋
  g += `<g transform="translate(860,1190)"><path d="M-90,0 L0,-80 L90,0Z" fill="#C9A06E"/><rect x="-70" y="0" width="140" height="80" fill="#D8B592"/><rect x="-18" y="25" width="36" height="55" fill="${C.cocoa}"/></g>`;
  // 熱浪
  for (let k = 0; k < 5; k++) {
    const y = 1150 - ((t * 60 + k * 90) % 400), x = 150 + k * 190;
    g += `<path d="M${x},${y} q20,-25 0,-50 q-20,-25 0,-50" stroke="#FFF1DC" stroke-width="7" fill="none" stroke-linecap="round" opacity="${0.5 * Math.sin(((t * 60 + k * 90) % 400) / 400 * Math.PI)}"/>`;
  }
  // 太陽一個個冒出來
  const t0 = cue.suns ?? d * 0.12;
  SUN2.forEach(([x, y], i) => {
    const s = back(seg(t, t0 + i * 0.16, t0 + i * 0.16 + 0.5));
    if (s > 0) g += sun({ x, y: y + Math.sin(t * 2.4 + i) * 10, r: 100 * s, t: t + i, i, sweat: t > (cue.crack ?? d * 0.45), blink: blinkAt(t, i * 0.7), brow: t > (cue.crack ?? d * 0.45) ? 'worry' : null, mood: t < (cue.crack ?? d * 0.45) ? 'happy' : null });
  });
  // 村民熱到搧風
  const tired = seg(t, cue.hard ?? d * 0.7, (cue.hard ?? d * 0.7) + 0.6);
  g += villager({ x: 300, y: 1440 + tired * 20, sc: 1.85, t, hat: true, sweat: true, brow: 'worry', mouth: tired > .5 ? 'o' : 'worry', blink: blinkAt(t, .3), armR: -150 + Math.sin(t * 9) * 25, armL: 20 });
  g += villager({ x: 790, y: 1500 + tired * 20, sc: 1.7, t: t + .4, bun: true, col: 'url(#gPink)', sweat: true, brow: 'worry', mouth: 'worry', blink: blinkAt(t, 1.4), armL: 150 + Math.sin(t * 9 + 1) * 25, armR: -20, look: [0, -6] });
  g += `<rect width="${W}" height="${H}" fill="#F3A46F" opacity="${0.08 + 0.05 * Math.sin(t * 3)}"/>`;
  const z = 1.12 - 0.12 * ease(u);
  return camera(g, z, 540, 820 + 140 * ease(u));
}

// ---------------- 3 后羿射日 ----------------
const SUN3 = [[150, 200], [400, 120], [680, 150], [930, 230], [260, 400], [540, 330], [820, 420], [130, 600], [420, 590], [700, 620]];
const KEEP = 5;
function scene3(t, d, cue) {
  const u = t / d;
  const shots = cue.shots ?? [d * .39, d * .45, d * .51];
  const hits = [[0, 3, 7], [1, 6, 8], [2, 4, 9]];
  const hitT = {}; hits.forEach((ids, v) => ids.forEach((i, j) => hitT[i] = shots[v] + 0.33 + j * 0.06));
  const lastHit = shots[2] + 0.5;
  // 上班下班：最後一顆太陽落下再升起，天色跟著變
  const work = cue.work ?? d * 0.8;
  const dip = Math.sin(Math.PI * seg(t, work, work + 1.6));
  let g = `<defs><linearGradient id="sky3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${dip > .5 ? '#9C9CC4' : '#FBEBD6'}"/><stop offset=".7" stop-color="${dip > .5 ? '#E3B0A0' : '#F7D2B0'}"/></linearGradient></defs>`;
  g += `<rect x="-500" y="-600" width="${W+1000}" height="${H+1200}" fill="url(#sky3)"/>`;
  g += `<rect x="-500" y="-600" width="${W+1000}" height="${H+1200}" fill="${C.navy}" opacity="${0.45 * dip}"/>`;
  g += stars(t, 18, 700, 3).replace(/opacity="([\d.]+)"/g, (m, v) => `opacity="${v * dip}"`);
  // 太陽們
  SUN3.forEach(([x, y], i) => {
    if (i === KEEP) {
      const k = ease(seg(t, lastHit, lastHit + 1.2));
      const bx = x + (830 - x) * k, by = y + (330 - y) * k + 820 * dip;
      g += sun({ x: bx, y: by + Math.sin(t * 2.4) * 8, r: 86 + 40 * k, t, blink: blinkAt(t, .5), mood: k > .5 ? 'happy' : null, look: [0, 0] });
      return;
    }
    const th = hitT[i];
    if (t < th) g += sun({ x, y: y + Math.sin(t * 2.4 + i) * 8, r: 80, t: t + i, i, blink: blinkAt(t, i), mouth: t > shots[0] ? 'o' : null, look: t > shots[0] - 1 ? [-5, 8] : [0, 0] });
    else if (t < th + 1.1) {
      const k = (t - th) / 1.1;
      g += sun({ x: x + 80 * k, y: y + 900 * k * k, r: 80 * (1 - 0.4 * k), t, rot: 300 * k, alpha: 1 - k, mood: 'happy' });
    }
  });
  // 山（前景）
  g += `<path d="M-50,1500 L260,980 L420,1150 L560,900 L760,1200 L900,1050 L1130,1500Z" fill="${C.rose}"/>`;
  g += `<path d="M560,900 L620,990 L590,980 L560,1020 L530,975 L505,985Z" fill="#F3E3D4"/>`;
  g += cloud(180, 1180, 1.1, '#FBEFE4', .95) + cloud(900, 1250, 1.2, '#FBEFE4', .95);
  g += `<path d="M-50,2600 L-50,1480 Q200,1380 420,1440 L540,1260 L640,1440 Q880,1380 1130,1470 L1130,2600 L-50,2600Z" fill="${C.mauve}"/>`;
  g += `<path d="M-50,2600 L-50,1680 Q540,1560 1130,1680 L1130,2600Z" fill="#7A5E62"/>`;
  g += `<ellipse cx="540" cy="1290" rx="170" ry="42" fill="#9E8083"/><ellipse cx="540" cy="1280" rx="150" ry="30" fill="#B39194"/>`;
  // 后羿爬山：跳三下到山頂
  const climbEnd = cue.climb ?? d * 0.33;
  const pts = [[200, 1640], [330, 1530], [450, 1420], [540, 1270]];
  const climbStart = cue.climbStart ?? 0;
  const cp = clamp((t - climbStart) / (climbEnd - climbStart)) * 3, ci = Math.min(Math.floor(cp), 2), ck = cp - ci;
  const [ax, ay] = pts[ci], [bx2, by2] = pts[ci + 1];
  const hx = t < climbEnd ? ax + (bx2 - ax) * ck : 540, hy = t < climbEnd ? ay + (by2 - ay) * ck - Math.sin(ck * Math.PI) * 110 : 1270;
  const aiming = t > climbEnd;
  // 拉弓：每一發前 0.4 秒拉滿、放箭
  let draw = 0, recoil = 0;
  shots.forEach(s => { draw = Math.max(draw, t < s ? ease(seg(t, s - .45, s - .05)) : 0); recoil = Math.max(recoil, 1 - Math.abs(t - s) / 0.18); });
  if (t > shots[2]) draw = 0;
  g += houyi({ x: hx, y: hy - 330 + recoil * 10, sc: 1.35, t, blink: blinkAt(t, .2), bow: aiming, draw: aiming ? draw : 0, armR: aiming ? -150 : 30 + Math.sin(t * 8) * 20, armL: aiming ? -85 : -30 - Math.sin(t * 8) * 20, look: aiming ? [8, -8] : [0, 0], mouth: t > lastHit && t < work ? 'o' : null, mood: t > work ? 'happy' : null, tilt: aiming ? -6 : 0 });
  // 箭 & 命中
  const bowX = 540 + 129.5 * 1.35, bowY = 1270 - 330 + 3 * 1.35;
  hits.forEach((ids, v) => ids.forEach((i, j) => {
    const s = shots[v] + j * 0.06, th = hitT[i];
    if (t >= s && t < th) g += arrowFx(bowX, bowY, SUN3[i][0], SUN3[i][1], (t - s) / (th - s));
    if (t >= th && t < th + .6) g += burst(SUN3[i][0], SUN3[i][1], (t - th) / .6);
  }));
  const z = 1.0 + 0.1 * ease(seg(t, 0, climbEnd)) - 0.1 * ease(seg(t, climbEnd, climbEnd + 1));
  return camera(g, z, 540, 960 + 150 * (1 - ease(seg(t, 0, climbEnd))));
}

// ---------------- 4 當國王、變兇、拿仙丹 ----------------
function scene4(t, d, cue) {
  const crownT = cue.crown ?? d * 0.12, angryT = cue.angry ?? d * 0.38, pillT = cue.pill ?? d * 0.62;
  const king = t > crownT + 0.6, angry = seg(t, angryT, angryT + .4);
  const shake = Math.sin(t * 45) * 10 * angry * (1 - seg(t, angryT + .5, angryT + 1));
  let g = `<defs><linearGradient id="wall4" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9C2AE"/><stop offset="1" stop-color="${C.rose}"/></linearGradient></defs>`;
  g += `<rect x="-500" y="-600" width="${W+1000}" height="${H+1200}" fill="url(#wall4)"/>`;
  // 窗格、柱子、布幔
  for (let k = 0; k < 3; k++) g += `<rect x="${200 + k * 250}" y="330" width="170" height="520" rx="85" fill="#F6DCC6" opacity=".7"/><path d="M${285 + k * 250},340 L${285 + k * 250},840 M${210 + k * 250},590 L${360 + k * 250},590" stroke="${C.mocha}" stroke-width="6" opacity=".5"/>`;
  g += `<rect x="40" y="-600" width="90" height="3200" fill="${C.cocoa}"/><rect x="950" y="-600" width="90" height="3200" fill="${C.cocoa}"/>`;
  g += `<path d="M0,0 L540,0 Q300,160 0,380Z" fill="${C.mauve}"/><path d="M1080,0 L540,0 Q780,160 1080,380Z" fill="${C.mauve}"/>`;
  g += `<path d="M-500,1450 L1600,1450 L1600,2600 L-500,2600Z" fill="#B98A7C"/><path d="M280,1450 L800,1450 L920,1920 L160,1920Z" fill="#C98A86"/>`;
  // 寶座
  g += `<g transform="translate(540,1080) scale(1.3)"><path d="M-240,280 L-240,-280 Q-240,-380 -120,-400 Q0,-470 120,-400 Q240,-380 240,-280 L240,280Z" fill="url(#gGold)" stroke="${C.goldS}" stroke-width="8"/><path d="M-170,250 L-170,-230 Q0,-330 170,-230 L170,250Z" fill="${C.red}" opacity=".85"/><circle cx="0" cy="-330" r="28" fill="${C.pink}"/></g>`;
  // 后羿 / 國王
  g += houyi({ x: 540 + shake, y: 1100, sc: 1.6, t, king, blink: blinkAt(t, .4), brow: angry > .3 ? 'angry' : null, mouth: angry > .3 ? 'frown' : (king ? null : 'o'), mood: !king && t > .3 ? 'happy' : null, armL: angry > .3 ? 60 : 20, armR: t > pillT ? -150 : (angry > .3 ? -60 : -20), look: t > pillT + .4 ? [10, -8] : [0, 0] });
  // 皇冠從天而降
  if (!king) { const k = ease(seg(t, crownT - .6, crownT + .6)); g += `<g transform="translate(540,${-150 + (812 + 150) * k})"><g transform="scale(1.6)"><path d="M-80,35 L-70,-30 L-35,10 L0,-45 L35,10 L70,-30 L80,35Z" fill="url(#gGold)" stroke="${C.goldS}" stroke-width="4"/></g></g>`; }
  // 百姓歡呼 → 被兇到退開
  const scared = ease(seg(t, angryT + .2, angryT + 1));
  [[170, 1560, 0], [540, 1640, 1], [910, 1560, 2]].forEach(([x, y, i]) => {
    const hop = scared > 0 ? 0 : Math.abs(Math.sin(t * 6 + i)) * 40;
    g += villager({ x: x + (i === 1 ? 0 : (i ? 1 : -1) * 260 * scared), y: y + 700 * scared, sc: 1.45, t, hop, hat: i === 0, bun: i === 2, col: i === 2 ? 'url(#gPink)' : (i === 1 ? 'url(#gLav)' : 'url(#gMocha)'), mood: scared > .1 ? null : 'happy', mouth: scared > .1 ? 'o' : null, brow: scared > .1 ? 'worry' : null, armL: scared > .1 ? 20 : 150, armR: scared > .1 ? -20 : -150, blink: blinkAt(t, i) });
  });
  g += `<rect width="${W}" height="${H}" fill="#5A2E3A" opacity="${0.18 * angry}"/>`;
  // 仙丹
  const e = back(seg(t, pillT, pillT + .6));
  if (e > 0) g += elixir(770, 980 + Math.sin(t * 3) * 18, 1.4 * e, t);
  const z = 1.0 + 0.08 * ease(seg(t, angryT, angryT + 1.5));
  return camera(g, z, 540, 960 + 40 * ease(seg(t, angryT, angryT + 1.5)));
}

// ---------------- 5 嫦娥吃仙丹飛上月亮 ----------------
function scene5(t, d, cue) {
  const eatT = cue.eat ?? d * 0.3, flyT = cue.fly ?? d * 0.5;
  const f = ease(seg(t, flyT, d - 0.3));
  let g = `<defs><linearGradient id="sky5" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2E3558"/><stop offset=".5" stop-color="${C.navy}"/><stop offset="1" stop-color="${C.lav}"/></linearGradient></defs>`;
  g += `<rect x="-500" y="-1900" width="${W+1000}" height="${H + 2600}" fill="url(#sky5)"/>`;
  g += stars(t, 30, 1300, 7).replace(/<path/g, '<path transform="translate(0,-1200)"');
  g += stars(t, 20, 1000, 20);
  // 月亮在高處
  g += `<circle cx="720" cy="-760" r="480" fill="url(#gGlow)"/><circle cx="720" cy="-760" r="260" fill="url(#gMoon)"/><circle cx="640" cy="-820" r="40" fill="#F1DDC0" opacity=".6"/><circle cx="800" cy="-700" r="28" fill="#F1DDC0" opacity=".6"/>`;
  g += cloud(200, 600, 1.4, '#6E6A92', .7) + cloud(900, 380, 1.1, '#7B77A0', .6);
  // 宮殿屋頂與窗光
  g += `<path d="M-40,1500 Q200,1380 540,1360 Q880,1380 1120,1500 L1080,1540 L0,1540Z" fill="#3A3150"/><rect x="60" y="1540" width="960" height="400" fill="#4A3F5E"/>`;
  for (let k = 0; k < 4; k++) g += `<rect x="${130 + k * 230}" y="1600" width="120" height="170" rx="60" fill="${C.lamp}" opacity="${0.75 + 0.2 * Math.sin(t * 2 + k)}"/>`;
  g += `<rect x="-500" y="1780" width="2100" height="900" fill="#5B4B6A"/>`;
  // 嫦娥
  const worry = t < eatT;
  const sneak = t > eatT - 1.2 && t < eatT ? Math.sin(t * 7) * 14 : 0;
  const ex = 840 + (540 - 840) * ease(seg(t, eatT, eatT + .5)), ey = 1120 + (1281 - 1120) * ease(seg(t, eatT, eatT + .5));
  const cy = 1300 + (-640 - 1300) * f, cx = 540 + 150 * f + Math.sin(t * 2) * 40 * (1 - f);
  if (t < eatT + .55) g += elixir(ex, ey, 0.9 * (1 - seg(t, eatT + .35, eatT + .55)), t);
  // 星光拖尾
  if (f > 0) for (let q = 0; q < 16; q++) { const v = q / 16, kk = ease(seg(t - v * .8, flyT, d - .3)); g += star(540 + 150 * kk + Math.sin(t * 3 + q) * 70, 1360 + (-640 - 1360) * kk + 330, 22 * (1 - v) + 5, q % 2 ? C.peri : '#FFF1C8', 1 - v); }
  if (t > eatT + .3 && t < eatT + 1.1) g += burst(540, 1250, (t - eatT - .3) / .8, 12, 260);
  g += change({ x: cx, y: cy, sc: 1.6 - 0.9 * f, t, fly: seg(t, flyT - .3, flyT + .5), blink: blinkAt(t, .8), brow: worry ? 'worry' : null, mouth: worry ? (t > eatT - 1.2 ? null : 'worry') : (t < flyT + .8 ? 'o' : null), mood: t > flyT + .8 ? 'happy' : null, look: [sneak, 0], armL: t > flyT ? 110 : (worry ? 60 : 25), armR: t > flyT ? -110 : (worry ? -60 : -25), rot: Math.sin(t * 2) * 5 * f });
  const camY = 1000 + (-500 - 1000) * ease(seg(t, flyT + .3, d));
  return camera(g, 1.0, 540, camY);
}

// ---------------- 6 賞月吃月餅 ----------------
function scene6(t, d, cue) {
  const u = t / d;
  let g = `<defs><linearGradient id="sky6" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#343B60"/><stop offset=".55" stop-color="${C.lav}"/><stop offset=".8" stop-color="#D9B3B0"/></linearGradient></defs>`;
  g += `<rect x="-500" y="-600" width="${W+1000}" height="${H+1200}" fill="url(#sky6)"/>` + stars(t, 26, 900, 40);
  // 大月亮 + 嫦娥玉兔剪影
  const mp = 1 + 0.02 * Math.sin(t * 2);
  g += `<circle cx="540" cy="560" r="${560 * mp}" fill="url(#gGlow)"/><circle cx="540" cy="560" r="300" fill="url(#gMoon)"/>`;
  const cm = ease(seg(t, cue.thank ?? d * .55, (cue.thank ?? d * .55) + 1));
  g += `<g opacity="${0.25 + 0.6 * cm}">` + change({ x: 500, y: 560 + Math.sin(t * 1.5) * 10, sc: .55, t, fly: .3, mood: 'happy', armL: 40, armR: -120 }) + rabbit({ x: 660, y: 700, sc: .45, t, hop: Math.abs(Math.sin(t * 3)) * 16 }) + `</g>`;
  // 燈籠串
  g += `<path d="M-20,260 Q540,420 1100,260" stroke="${C.cocoa}" stroke-width="5" fill="none"/>`;
  [[120, 300], [330, 360], [750, 360], [960, 300]].forEach(([x, y], i) => g += lantern(x, y + 90, .95, Math.sin(t * 1.8 + i * 1.3) * 8, 0.8 + 0.2 * Math.sin(t * 3 + i)));
  // 地面、屋頂
  g += `<path d="M-40,1250 L150,1130 L330,1250Z M750,1250 L930,1130 L1120,1250Z" fill="#4A3F5E"/>`;
  g += `<path d="M0,1250 Q540,1190 1080,1250 L1600,1250 L1600,2600 L-500,2600 L-500,1250Z" fill="#7C6474"/><path d="M0,1420 Q540,1380 1080,1420 L1600,1420 L1600,2600 L-500,2600 L-500,1420Z" fill="#8F7073"/>`;
  g += `<circle cx="540" cy="1400" r="700" fill="url(#gWarm)" opacity=".35"/>`;
  // 桌子 + 月餅
  g += `<ellipse cx="540" cy="1560" rx="330" ry="80" fill="${C.cocoa}"/><ellipse cx="540" cy="1545" rx="330" ry="75" fill="#B98068"/><rect x="510" y="1600" width="60" height="200" fill="${C.cocoa}"/>`;
  g += mooncake(430, 1520, 58, 10) + mooncake(560, 1540, 58, -8) + mooncake(680, 1515, 52, 20);
  // 村民圍坐：看月亮、吃月餅、歡呼
  const bite = Math.sin(t * 5) > 0.3;
  g += villager({ x: 165, y: 1400, sc: 1.4, t, hat: true, mood: 'happy', armL: 20, armR: -160 + Math.sin(t * 5) * 15, blink: blinkAt(t, .1), hop: Math.abs(Math.sin(t * 4)) * 14 * seg(t, d * .75, d) });
  g += villager({ x: 915, y: 1400, sc: 1.4, t, bun: true, col: 'url(#gPink)', look: [-4, -10], armR: -150, armL: 150, mouth: cm > .5 ? 'o' : null, mood: cm > .5 ? null : 'happy', blink: blinkAt(t, 1.1) });
  g += villager({ x: 540, y: 1520, sc: 1.5, t, col: 'url(#gLav)', mouth: bite ? 'o' : null, talk: bite ? .6 : 0, armR: -130, armL: 30, blink: blinkAt(t, 2), look: [0, -8] });
  g += mooncake(640, 1480 - (bite ? 14 : 0), 44, 0);
  const z = 1.06 - 0.06 * ease(u);
  g = camera(g, z, 540, 960);
  g += `<rect width="${W}" height="${H}" fill="${C.moon}" opacity="${seg(t, d - .8, d)}"/>`;
  return g;
}

const SCENES = [null, null, scene2, scene3, scene4, scene5, scene6];
function renderScene(i, t, d, cue) {
  document.getElementById('s').innerHTML = defs() + SCENES[i](t, d, cue || {});
}
