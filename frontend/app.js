const md = window.markdownit();
const ws = new WebSocket(`wss://${location.host}/ws`.replace('wss://','ws://'));

ws.onmessage = e => {
  const m = JSON.parse(e.data);
  if (m.kind === "lessons") nav(m.payload);
  if (m.kind === "lesson") lesson(m.payload);
  if (m.kind === "state")  state(m.payload);
};

const nav = list => {
  const el = document.getElementById("nav");
  el.innerHTML = list.map(n=>`<button data-l="\${n}">\${n}</button>`).join("<br>");
  el.querySelectorAll("[data-l]").forEach(b =>
    b.onclick = _ => ws.send(JSON.stringify({kind:"lesson",payload:b.dataset.l})));
};

const lesson = mdText =>
  document.getElementById("lesson").innerHTML = md.render(mdText);

const state = d =>
  document.getElementById("state").innerHTML =
    `<pre>Coils     : \${JSON.stringify(d.coils)}</pre>
     <pre>Registers : \${JSON.stringify(d.registers)}</pre>`;

document.querySelectorAll("[data-coil]").forEach(b=>
  b.onclick = _ => ws.send(JSON.stringify({kind:"action",payload:{flip:b.dataset.coil}})));
