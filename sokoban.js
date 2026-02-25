const TILE = 54;
const LEVELS = [
  [
    " #########   ",
    " #   .   #   ",
    " #  $$   #   ",
    " ###  ###    ",
    " #  @   #    ",
    " #   .  #    ",
    " ########    ",
  ],
  [
    "   ##########   ",
    "   #  .  .  #   ",
    " ### $$ $$  #   ",
    " #   ##   ###   ",
    " # @      #     ",
    " #   ######     ",
    " #####          ",
  ],
  [
    "   ###########   ",
    " ###   . .   ### ",
    " #  $$ ### $$  # ",
    " # #   @   #  #  ",
    " #  $$ ### $$  # ",
    " ###   . .   ### ",
    "   ###########   ",
  ],
];

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const ui = {
  level: document.getElementById("level"),
  moves: document.getElementById("moves"),
  pushes: document.getElementById("pushes"),
};

const state = { levelIndex: 0, rows: 0, cols: 0, base: [], boxes: new Set(), player: {x:0,y:0}, history: [], moves:0, pushes:0, win:false };

function key(x,y){ return `${x},${y}`; }
function hasBox(x,y){ return state.boxes.has(key(x,y)); }

function loadLevel(idx){
  const raw = LEVELS[idx];
  state.levelIndex = idx;
  state.rows = raw.length;
  state.cols = Math.max(...raw.map(r=>r.length));
  state.base = Array.from({length:state.rows},()=>Array(state.cols).fill(" "));
  state.boxes = new Set();
  state.history = [];
  state.moves = 0; state.pushes = 0; state.win = false;
  for (let y=0;y<state.rows;y++){
    for (let x=0;x<state.cols;x++){
      const c = raw[y][x] || " ";
      if (c === "#" || c === ".") state.base[y][x] = c;
      if (c === "$" || c === "*") state.boxes.add(key(x,y));
      if (c === "*" || c === "+") state.base[y][x] = ".";
      if (c === "@" || c === "+") state.player = {x,y};
    }
  }
  syncUi();
}

function isBlocked(x,y){ return x<0||y<0||x>=state.cols||y>=state.rows||state.base[y][x]==="#"; }
function snapshot(){ return { player: {...state.player}, boxes: new Set(state.boxes), moves: state.moves, pushes: state.pushes }; }
function complete(){
  for(let y=0;y<state.rows;y++)for(let x=0;x<state.cols;x++) if(state.base[y][x]==="."&&!hasBox(x,y)) return false;
  return true;
}

function move(dx,dy){
  if (state.win) return;
  const nx=state.player.x+dx, ny=state.player.y+dy;
  if (isBlocked(nx,ny)) return;
  state.history.push(snapshot());
  if (hasBox(nx,ny)){
    const bx=nx+dx, by=ny+dy;
    if (isBlocked(bx,by) || hasBox(bx,by)) { state.history.pop(); return; }
    state.boxes.delete(key(nx,ny)); state.boxes.add(key(bx,by));
    state.pushes++;
  }
  state.player = {x:nx,y:ny};
  state.moves++;
  state.win = complete();
  syncUi();
}

function undo(){
  const h = state.history.pop(); if(!h) return;
  state.player = h.player; state.boxes = h.boxes; state.moves = h.moves; state.pushes = h.pushes; state.win = complete();
  syncUi();
}

function syncUi(){
  ui.level.textContent = `${state.levelIndex+1}/${LEVELS.length}`;
  ui.moves.textContent = state.moves;
  ui.pushes.textContent = state.pushes;
}

function draw(){
  const w = canvas.width, h = canvas.height;
  const bg = ctx.createLinearGradient(0,0,0,h);
  bg.addColorStop(0,"#121933"); bg.addColorStop(1,"#20172f");
  ctx.fillStyle = bg; ctx.fillRect(0,0,w,h);

  const gridW = state.cols*TILE, gridH = state.rows*TILE;
  const ox = (w-gridW)/2, oy = (h-gridH)/2;

  ctx.fillStyle = "#11182c";
  ctx.strokeStyle = "#4f6ca6";
  roundRect(ox-10, oy-10, gridW+20, gridH+20, 14, true, true);

  for(let y=0;y<state.rows;y++){
    for(let x=0;x<state.cols;x++){
      const tx = ox + x*TILE, ty = oy + y*TILE;
      if (state.base[y][x] === "#") {
        ctx.fillStyle="#3b4d82"; roundRect(tx,ty,TILE-2,TILE-2,9,true,false);
        ctx.fillStyle="#2b3863"; roundRect(tx+5,ty+5,TILE-12,TILE-12,7,true,false);
      } else {
        ctx.fillStyle="#252f4b"; roundRect(tx,ty,TILE-2,TILE-2,8,true,false);
        if (state.base[y][x] === ".") {
          ctx.fillStyle="#69d8ff"; circle(tx+TILE/2, ty+TILE/2, 8);
          ctx.fillStyle="#baf3ff"; circle(tx+TILE/2, ty+TILE/2, 4);
        }
      }
    }
  }

  for (const b of state.boxes){
    const [x,y] = b.split(",").map(Number);
    const tx=ox+x*TILE, ty=oy+y*TILE;
    ctx.fillStyle="#f8a14a"; roundRect(tx+5,ty+5,TILE-12,TILE-12,9,true,false);
    ctx.fillStyle="#ffd698"; roundRect(tx+15,ty+15,TILE-32,TILE-32,5,true,false);
  }

  const px = ox + state.player.x*TILE + TILE/2;
  const py = oy + state.player.y*TILE + TILE/2;
  ctx.fillStyle="#8ee87b"; circle(px,py,16);
  ctx.fillStyle="#d7ffaf"; circle(px,py-5,6);

  if (state.win){
    ctx.fillStyle="#091120bb"; ctx.fillRect(0,0,w,h);
    ctx.fillStyle="#b2ff9e"; ctx.font="bold 42px Segoe UI"; ctx.textAlign="center";
    ctx.fillText("NIVEAU TERMINÉ ✨", w/2, h/2-10);
    ctx.fillStyle="#eaf2ff"; ctx.font="24px Segoe UI";
    ctx.fillText("Appuie sur N pour continuer", w/2, h/2+32);
  }

  requestAnimationFrame(draw);
}

function roundRect(x,y,w,h,r,fill,stroke){
  ctx.beginPath();
  ctx.moveTo(x+r,y); ctx.arcTo(x+w,y,x+w,y+h,r); ctx.arcTo(x+w,y+h,x,y+h,r); ctx.arcTo(x,y+h,x,y,r); ctx.arcTo(x,y,x+w,y,r);
  if(fill) ctx.fill(); if(stroke) ctx.stroke();
}
function circle(x,y,r){ ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill(); }

document.addEventListener("keydown", (e)=>{
  const m = {ArrowLeft:[-1,0],a:[-1,0],ArrowRight:[1,0],d:[1,0],ArrowUp:[0,-1],w:[0,-1],ArrowDown:[0,1],s:[0,1]};
  if (m[e.key]) { move(...m[e.key]); e.preventDefault(); }
  else if (e.key === "z") undo();
  else if (e.key === "r") loadLevel(state.levelIndex);
  else if (e.key === "n") loadLevel((state.levelIndex + 1) % LEVELS.length);
});

loadLevel(0);
draw();
