const ws = new WebSocket(`ws://${location.host}/ws`);
const statusInd = document.getElementById('statusIndicator');

const lStick = document.getElementById('leftStick');
const rStick = document.getElementById('rightStick');
const lStickVals = document.getElementById('leftStickVals');
const rStickVals = document.getElementById('rightStickVals');

const lTrigger = document.getElementById('leftTrigger');
const rTrigger = document.getElementById('rightTrigger');
const lTriggerVal = document.getElementById('leftTriggerVal');
const rTriggerVal = document.getElementById('rightTriggerVal');

const leftDz = document.getElementById('leftDeadzone');
const rightDz = document.getElementById('rightDeadzone');
const ldVal = document.getElementById('ldVal');
const rdVal = document.getElementById('rdVal');

const rLow = document.getElementById('rumbleLow');
const rHigh = document.getElementById('rumbleHigh');
const rLowVal = document.getElementById('rumbleLowVal');
const rHighVal = document.getElementById('rumbleHighVal');
const testRumbleBtn = document.getElementById('testRumbleBtn');

const buttonsGrid = document.getElementById('buttonsGrid');

const buttonNames = [
    { key: "button_a", label: "A" }, { key: "button_b", label: "B" },
    { key: "button_x", label: "X" }, { key: "button_y", label: "Y" },
    { key: "button_lb", label: "LB" }, { key: "button_rb", label: "RB" },
    { key: "button_l3", label: "LSB" }, { key: "button_r3", label: "RSB" },
    { key: "button_back", label: "SELECT" }, { key: "button_start", label: "START" }
];

buttonNames.forEach(btn => {
    const div = document.createElement('div');
    div.className = 'btn-indicator';
    div.id = `btn_${btn.key}`;
    div.innerText = btn.label;
    buttonsGrid.appendChild(div);
});

ws.onopen = () => {
    statusInd.innerHTML = 'Gamepad Motoruna Bağlı';
    statusInd.classList.add('connected');
};

ws.onclose = () => {
    statusInd.innerHTML = 'Bağlantı Koptu - Yeniden Deneniyor...';
    statusInd.classList.remove('connected');
    setTimeout(() => location.reload(), 2000);
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'init_config') {
        const cfg = data.data;
        leftDz.value = cfg.deadzone_left * 100;
        rightDz.value = cfg.deadzone_right * 100;
        ldVal.innerText = `${leftDz.value}%`;
        rdVal.innerText = `${rightDz.value}%`;
        
    } else if (data.type === 'gamepad_data') {
        updateVisuals(data.processed);
    }
};

function updateVisuals(state) {
    const [lx, ly] = state.left_joystick || [0, 0];
    const [rx, ry] = state.right_joystick || [0, 0];
    const maxOffset = 67.5;
    
    lStick.style.transform = `translate(${lx * maxOffset}px, ${ly * maxOffset}px)`;
    rStick.style.transform = `translate(${rx * maxOffset}px, ${ry * maxOffset}px)`;
    lStickVals.innerText = `X: ${lx.toFixed(2)} | Y: ${ly.toFixed(2)}`;
    rStickVals.innerText = `X: ${rx.toFixed(2)} | Y: ${ry.toFixed(2)}`;

    const lt = state.left_trigger || 0;
    const rt = state.right_trigger || 0;
    lTrigger.style.height = `${lt * 100}%`;
    rTrigger.style.height = `${rt * 100}%`;
    lTriggerVal.innerText = lt.toFixed(2);
    rTriggerVal.innerText = rt.toFixed(2);

    buttonNames.forEach(btn => {
        const el = document.getElementById(`btn_${btn.key}`);
        if (state[btn.key]) {
            el.classList.add('active');
        } else {
            el.classList.remove('active');
        }
    });
}

function sendConfig() {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'config_update',
            data: {
                deadzone_left: leftDz.value / 100,
                deadzone_right: rightDz.value / 100
            }
        }));
    }
}

leftDz.addEventListener('input', (e) => { ldVal.innerText = `${e.target.value}%`; sendConfig(); });
rightDz.addEventListener('input', (e) => { rdVal.innerText = `${e.target.value}%`; sendConfig(); });

rLow.addEventListener('input', (e) => rLowVal.innerText = `${e.target.value}%`);
rHigh.addEventListener('input', (e) => rHighVal.innerText = `${e.target.value}%`);

testRumbleBtn.addEventListener('click', function() {
    this.style.transform = 'scale(0.95)';
    setTimeout(() => this.style.transform = 'none', 100);
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'test_rumble',
            data: {
                low: rLow.value / 100,
                high: rHigh.value / 100,
                duration: 800
            }
        }));
    }
});
