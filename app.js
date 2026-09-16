const ADMIN_EMAIL = "haslooytr@gmail.com";

let state = {
  currentUser: null,
  guestId: getOrCreateGuestId(),
  isPasswordVisible: false,
  logs: []
};

function getOrCreateGuestId() {
  let id = localStorage.getItem('omni_guest_id');
  if (!id) {
    const randomDigits = Math.floor(10000000000000 + Math.random() * 90000000000000);
    id = `guest-${randomDigits}`;
    localStorage.setItem('omni_guest_id', id);
  }
  return id;
}

function getCurrentIdentity() {
  return state.currentUser ? state.currentUser.email : state.guestId;
}

// AKICI GÖZ TAKİBİ
const leftPupil = document.getElementById('left-pupil');
const rightPupil = document.getElementById('right-pupil');
const leftEyelid = document.getElementById('left-eyelid');
const rightEyelid = document.getElementById('right-eyelid');

document.addEventListener('mousemove', (e) => {
  if (state.isPasswordVisible) return;
  const eyesSvg = document.getElementById('eyes-svg');
  if (!eyesSvg) return;

  const rect = eyesSvg.getBoundingClientRect();
  const eyeCenterX = rect.left + rect.width / 2;
  const eyeCenterY = rect.top + rect.height / 2;

  const angle = Math.atan2(e.clientY - eyeCenterY, e.clientX - eyeCenterX);
  const distance = Math.min(12, Math.hypot(e.clientX - eyeCenterX, e.clientY - eyeCenterY) / 12);

  const moveX = Math.cos(angle) * distance;
  const moveY = Math.sin(angle) * distance;

  leftPupil.style.transform = `translate(${moveX}px, ${moveY}px)`;
  rightPupil.style.transform = `translate(${moveX}px, ${moveY}px)`;
});

function togglePasswordVisibility() {
  const passInput = document.getElementById('password-input');
  state.isPasswordVisible = !state.isPasswordVisible;

  if (state.isPasswordVisible) {
    passInput.type = "text";
    leftPupil.style.transform = `translate(25px, -15px)`;
    rightPupil.style.transform = `translate(25px, -15px)`;
    leftEyelid.setAttribute('opacity', '1');
    rightEyelid.setAttribute('opacity', '1');
  } else {
    passInput.type = "password";
    leftPupil.style.transform = `translate(0px, 0px)`;
    rightPupil.style.transform = `translate(0px, 0px)`;
    leftEyelid.setAttribute('opacity', '0');
    rightEyelid.setAttribute('opacity', '0');
  }
}

// GERÇEK GOOGLE GİRİŞ CALLBACK'İ
function handleGoogleCallback(response) {
  try {
    const base64Url = response.credential.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    const payload = JSON.parse(jsonPayload);
    loginUser(payload.email);
  } catch (err) {
    console.error("Google Giriş Hatası:", err);
  }
}

function openAuthModal() { document.getElementById('auth-modal').classList.add('active'); }
function closeAuthModal() { 
  document.getElementById('auth-modal').classList.remove('active');
  if(state.isPasswordVisible) togglePasswordVisibility();
}

function handleLocalLogin() {
  const email = document.getElementById('email-input').value;
  loginUser(email);
}

function loginUser(email) {
  state.currentUser = { email };
  closeAuthModal();

  document.getElementById('user-name').innerText = email.split('@')[0];
  const badge = document.getElementById('user-badge');
  badge.innerText = "Üye";
  badge.className = "badge user";

  document.getElementById('auth-btn').innerText = "Çıkış Yap";
  document.getElementById('auth-btn').onclick = () => location.reload();

  if (email === ADMIN_EMAIL) {
    badge.className = "badge admin";
    badge.innerText = "Admin";
    document.getElementById('admin-sidebar-btn').classList.remove('hidden');
  }

  logActivity("Sisteme Giriş Yapıldı");
}

function filterCategory(category, element) {
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  element.classList.add('active');

  const cards = document.querySelectorAll('#tools-grid .card');
  cards.forEach(card => {
    card.style.display = (category === 'all' || card.dataset.category === category) ? "flex" : "none";
  });
}

function searchTools() {
  const query = document.getElementById('tool-search').value.toLowerCase();
  const cards = document.querySelectorAll('#tools-grid .card');
  cards.forEach(card => {
    card.style.display = card.dataset.name.includes(query) ? "flex" : "none";
  });
}

function logActivity(toolName) {
  const identity = getCurrentIdentity();
  const time = new Date().toLocaleTimeString();

  const existing = state.logs.find(l => l.identity === identity);
  if (existing) {
    existing.action = toolName;
    existing.time = time;
  } else {
    state.logs.push({ identity, status: state.currentUser ? 'Kayıtlı' : 'Misafir', action: toolName, time });
  }

  renderAdminTable();
}

function formatJSON() {
  const input = document.getElementById('json-input').value;
  try {
    document.getElementById('json-output').innerText = JSON.stringify(JSON.parse(input), null, 2);
    logActivity("JSON Biçimlendirici");
  } catch (e) {
    document.getElementById('json-output').innerText = "❌ Geçersiz JSON!";
  }
}

function processImage() {
  const input = document.getElementById('image-input');
  if (!input.files[0]) return alert("Lütfen bir resim seçin!");
  const reader = new FileReader();
  reader.onload = function(e) {
    const img = new Image();
    img.src = e.target.result;
    img.onload = function() {
      const canvas = document.createElement('canvas');
      canvas.width = img.width; canvas.height = img.height;
      canvas.getContext('2d').drawImage(img, 0, 0);
      document.getElementById('image-result').innerHTML = `<a href="${canvas.toDataURL('image/webp')}" download="converted.webp" style="color:#818cf8;">İndir (.WebP)</a>`;
      logActivity("Resim Dönüştürücü");
    };
  };
  reader.readAsDataURL(input.files[0]);
}

function generatePassword() {
  const len = document.getElementById('pass-length').value;
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()";
  let pass = "";
  for (let i = 0; i < len; i++) pass += chars.charAt(Math.floor(Math.random() * chars.length));
  document.getElementById('pass-output').value = pass;
  logActivity("Şifre Üreteci");
}

function analyzeText() {
  const text = document.getElementById('text-input').value;
  if (!state.currentUser && text.length > 100) {
    return alert("Misafirler max 100 karakter analiz edebilir!");
  }
  document.getElementById('text-output').innerHTML = `Karakter: ${text.length} | Kelime: ${text.trim() ? text.trim().split(/\s+/).length : 0}`;
  logActivity("Metin Analizörü");
}

function showPage(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(pageId).classList.add('active');
}

function renderAdminTable() {
  const tbody = document.getElementById('activity-log');
  tbody.innerHTML = "";
  let guestCount = 0, registeredCount = 0;

  state.logs.forEach(log => {
    if (log.status === 'Misafir') guestCount++; else registeredCount++;
    tbody.innerHTML += `<tr>
      <td><code>${log.identity}</code></td>
      <td>${log.status}</td>
      <td>${log.action}</td>
      <td>${log.time}</td>
    </tr>`;
  });

  document.getElementById('stat-total-users').innerText = state.logs.length;
  document.getElementById('stat-active-today').innerText = state.logs.length;
  document.getElementById('stat-registered-users').innerText = registeredCount;
  document.getElementById('stat-guest-users').innerText = guestCount;
}

logActivity("Siteye Giriş Yaptı");
