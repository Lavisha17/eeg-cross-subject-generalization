(function () {
  "use strict";

  const canvas = document.getElementById("scene");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const POS = {
    AF3:[-.28,.74], AF4:[.28,.74], F7:[-.72,.52], F8:[.72,.52],
    F3:[-.4,.42], F4:[.4,.42], FC5:[-.7,.2], FC6:[.7,.2],
    T7:[-.88,-.05], T8:[.88,-.05], P7:[-.7,-.5], P8:[.7,-.5],
    O1:[-.28,-.82], O2:[.28,-.82]
  };

  const CH = Object.keys(POS).sort((a,b) =>
    POS[b][1]-POS[a][1] || POS[a][0]-POS[b][0]
  );

  const CAP = {
    rest: "Resting recording: synthetic traces are drawn smoother and slower.",
    multi: "Multitasking recording: synthetic traces are drawn faster and more irregular."
  };

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const state = {
    mode: 0, target: 0, playing: !reducedMotion,
    visible: true, time: 0, width: 0, height: 0, frame: null
  };

  function hash(n) {
    const x = Math.sin(n * 127.1) * 43758.5453;
    return x - Math.floor(x);
  }

  function signal(i, t, mode) {
    const rest =
      .6 * Math.sin(6.283 * (.35 + .03*i) * t + i) +
      .4 * Math.sin(6.283 * (1.1 + .05*(i%4)) * t + i*1.7) *
      (.7 + .3*Math.sin(.4*t+i));

    const busy =
      .35 * Math.sin(6.283 * (1.6 + .12*i) * t + i) +
      .3 * Math.sin(6.283 * (3.2 + .3*(i%3)) * t + i*2.3) +
      .3 * Math.sin(6.283 * 5.1 * t + i*.9) *
      (.4 + .6*Math.sin(1.3*t+i));

    const noise = (hash(Math.floor(t*40)+i*91)-.5)*.35*mode;
    return rest*(1-mode) + busy*mode + noise;
  }

  function size() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const width = canvas.parentElement.clientWidth;
    const height = width >= 720 ? 380 : 570;

    state.width = width;
    state.height = height;

    canvas.width = Math.round(width*dpr);
    canvas.height = Math.round(height*dpr);
    canvas.style.height = height + "px";

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw();
  }

  function draw() {
    const W = state.width, H = state.height;
    if (!W || !H) return;

    const wide = W >= 720;
    const m = state.mode, t = state.time;
    const styles = getComputedStyle(document.documentElement);
    const ink = styles.getPropertyValue("--ink").trim() || "#1a2430";
    const teal = styles.getPropertyValue("--teal").trim() || "#3f7f86";
    const ochre = styles.getPropertyValue("--ochre").trim() || "#a8782f";
    const rule = styles.getPropertyValue("--rule").trim() || "#d5d0c3";
    const mute = styles.getPropertyValue("--muted").trim() ||
                 styles.getPropertyValue("--text-muted").trim() || "#78818a";

    ctx.clearRect(0, 0, W, H);
    ctx.font = "11px system-ui, sans-serif";

    const x0 = wide ? 44 : 36;
    const x1 = wide ? W*.52 : W-12;
    const top = wide ? 18 : 24;
    const bottom = wide ? H-18 : 300;
    const rowHeight = (bottom-top)/14;
    const pixelsPerSecond = (x1-x0)/6;

    const head = wide ? [W*.78,H/2] : [W/2,425];
    const radius = wide ? Math.min(H*.4,W*.17) : Math.min(W*.3,120);
    const colour = m > .5 ? ochre : teal;

    // Four-second window guides
    ctx.setLineDash([3,4]);
    ctx.lineWidth = 1;
    const first = Math.floor((t-6)/4)*4;

    for (let k=first; k<=t; k+=4) {
      const x = x1-(t-k)*pixelsPerSecond;
      if (x < x0 || x > x1) continue;

      ctx.strokeStyle = mute;
      ctx.globalAlpha = .55;
      ctx.beginPath();
      ctx.moveTo(x,top-8);
      ctx.lineTo(x,bottom);
      ctx.stroke();

      const end = Math.min(x+4*pixelsPerSecond,x1);
      if (end-x > 70) {
        ctx.fillStyle = mute;
        ctx.globalAlpha = .9;
        ctx.textAlign = "center";
        ctx.fillText("4 s window",(x+end)/2,top-10);
      }
    }

    ctx.setLineDash([]);
    ctx.globalAlpha = 1;

    // EEG traces and moving pulses
    CH.forEach((channel,i) => {
      const y = top+(i+.5)*rowHeight;
      const amplitude = rowHeight*.42;

      ctx.fillStyle = mute;
      ctx.textAlign = "right";
      ctx.fillText(channel,x0-6,y+4);

      ctx.strokeStyle = colour;
      ctx.lineWidth = 1.3;
      ctx.globalAlpha = .9;
      ctx.beginPath();

      for (let x=x0; x<=x1; x+=3) {
        const time = t-(x1-x)/pixelsPerSecond;
        const yy = y-signal(i,time,m)*amplitude;
        if (x===x0) ctx.moveTo(x,yy);
        else ctx.lineTo(x,yy);
      }
      ctx.stroke();

      const point = POS[channel];
      const ex = head[0]+point[0]*radius;
      const ey = head[1]-point[1]*radius;
      const cx = (x1+ex)/2;
      const startY = y-signal(i,t,m)*amplitude;

      ctx.globalAlpha = .28;
      ctx.strokeStyle = rule;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x1,startY);
      ctx.quadraticCurveTo(cx,startY,ex,ey);
      ctx.stroke();

      const p = ((t*(.35+.35*m)+i*.137)%1);
      const a = 1-p;
      const qx = a*a*x1+2*a*p*cx+p*p*ex;
      const qy = a*a*startY+2*a*p*startY+p*p*ey;

      ctx.globalAlpha = .95;
      ctx.fillStyle = colour;
      ctx.beginPath();
      ctx.arc(qx,qy,2.4,0,6.283);
      ctx.fill();

      point.arr = [ex,ey,p];
    });

    // Schematic head outline
    ctx.globalAlpha = .7;
    ctx.strokeStyle = ink;
    ctx.lineWidth = 1.4;
    ctx.beginPath();
    ctx.arc(head[0],head[1],radius*1.08,0,6.283);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(head[0]-radius*.14,head[1]-radius*1.07);
    ctx.lineTo(head[0],head[1]-radius*1.25);
    ctx.lineTo(head[0]+radius*.14,head[1]-radius*1.07);
    ctx.stroke();

    [-1,1].forEach(side => {
      ctx.beginPath();
      ctx.ellipse(head[0]+side*radius*1.1,head[1],
        radius*.07,radius*.16,0,0,6.283);
      ctx.stroke();
    });

    // Connections between nearby electrodes
    ctx.globalAlpha = .16;
    ctx.strokeStyle = colour;
    ctx.lineWidth = 1;

    for (let a=0; a<14; a++) {
      for (let b=a+1; b<14; b++) {
        const A=POS[CH[a]], B=POS[CH[b]];
        const distance=Math.hypot(A[0]-B[0],A[1]-B[1]);

        if (distance < .62) {
          ctx.beginPath();
          ctx.moveTo(head[0]+A[0]*radius,head[1]-A[1]*radius);
          ctx.lineTo(head[0]+B[0]*radius,head[1]-B[1]*radius);
          ctx.stroke();
        }
      }
    }

    // Electrode points and labels
    CH.forEach(channel => {
      const point=POS[channel], q=point.arr;
      const pulse=q[2]>.9 ? (q[2]-.9)*10 : 0;

      if (pulse>0) {
        ctx.globalAlpha=.5*(1-pulse);
        ctx.strokeStyle=colour;
        ctx.beginPath();
        ctx.arc(q[0],q[1],5+pulse*9,0,6.283);
        ctx.stroke();
      }

      ctx.globalAlpha=1;
      ctx.fillStyle=colour;
      ctx.beginPath();
      ctx.arc(q[0],q[1],4,0,6.283);
      ctx.fill();

      ctx.fillStyle=mute;
      ctx.textAlign="center";
      ctx.fillText(channel,q[0],q[1]+(point[1]<-.6?16:-9));
    });

    ctx.globalAlpha=1;
  }

  const restButton = document.getElementById("b-rest");
  const multiButton = document.getElementById("b-multi");
  const playButton = document.getElementById("b-play");
  const caption = document.getElementById("scene-cap");

  function sync() {
    playButton.textContent = state.playing ? "Pause" : "Play";
    playButton.setAttribute("aria-pressed",String(state.playing));
  }

  function stop() {
    if (state.frame !== null) cancelAnimationFrame(state.frame);
    state.frame = null;
  }

  function animate(timestamp) {
    if (!state.playing || !state.visible) {
      stop();
      return;
    }

    if (!animate.last) animate.last=timestamp;
    const dt=Math.min((timestamp-animate.last)/1000,.05);
    animate.last=timestamp;

    state.time += dt;
    state.mode += (state.target-state.mode)*Math.min(dt*4,1);
    draw();

    state.frame=requestAnimationFrame(animate);
  }

  function start() {
    if (state.playing && state.visible && state.frame===null) {
      animate.last=0;
      state.frame=requestAnimationFrame(animate);
    }
  }

  function setMode(mode) {
    state.target=mode==="multi"?1:0;
    caption.textContent=CAP[mode];

    restButton.setAttribute("aria-pressed",String(mode==="rest"));
    multiButton.setAttribute("aria-pressed",String(mode==="multi"));

    if (!state.playing) {
      state.mode=state.target;
      draw();
    }
  }

  restButton.addEventListener("click",()=>setMode("rest"));
  multiButton.addEventListener("click",()=>setMode("multi"));

  playButton.addEventListener("click",()=>{
    state.playing=!state.playing;
    sync();
    if (state.playing) start();
    else {
      stop();
      draw();
    }
  });

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(entries=>{
      state.visible=entries[0].isIntersecting;
      if (state.visible) start();
      else stop();
    }).observe(canvas);
  }

  document.addEventListener("visibilitychange",()=>{
    if (document.hidden) stop();
    else start();
  });

  window.addEventListener("resize",size);

  sync();
  setMode("rest");
  size();
  start();
})();
