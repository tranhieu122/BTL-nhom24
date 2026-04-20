/* ==============================================
   HỆ THỐNG QUẢN LÝ ĐẶT PHÒNG HỌC — Nhóm 24
   JavaScript — Interactive Logic
   ============================================== */

// ==================== NAVIGATION ====================
function handleLogin() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const role = document.getElementById('login-role').value;

    if (!username || !password) {
        showToast('Vui lòng nhập đầy đủ thông tin!', 'error');
        return;
    }

    // Simulate login
    const btn = document.getElementById('btn-login');
    btn.innerHTML = '<span>Đang xử lý...</span>';
    btn.style.opacity = '0.7';
    btn.disabled = true;

    setTimeout(() => {
        document.getElementById('login-screen').classList.remove('active');
        document.getElementById('app-screen').classList.add('active');

        // Set user info
        const roleNames = {
            'admin': 'Admin',
            'giang_vien': 'GV',
            'sinh_vien': 'SV'
        };

        document.getElementById('header-username').textContent =
            `${roleNames[role]}: Nguyễn Văn A`;

        btn.innerHTML = '<span>ĐĂNG NHẬP</span><span class="btn-arrow">→</span>';
        btn.style.opacity = '1';
        btn.disabled = false;

        // Animate stat numbers
        animateStatNumbers();
        // Draw charts
        setTimeout(drawCharts, 300);

        showToast('Đăng nhập thành công!', 'success');
    }, 800);
}

function handleLogout() {
    document.getElementById('app-screen').classList.remove('active');
    document.getElementById('login-screen').classList.add('active');
    showToast('Đã đăng xuất!', 'info');
}

function navigateTo(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

    // Show target page
    const target = document.getElementById('page-' + pageId);
    if (target) {
        target.classList.add('active');
    }

    // Update menu active state
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-page') === pageId) {
            item.classList.add('active');
        }
    });

    // Close sidebar on mobile
    if (window.innerWidth <= 768) {
        document.getElementById('sidebar').classList.remove('show');
    }

    // Re-draw charts if reports page
    if (pageId === 'reports') {
        setTimeout(drawCharts, 200);
    }

    // Generate seats if room-detail page
    if (pageId === 'room-detail') {
        generateSeats();
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (window.innerWidth <= 768) {
        sidebar.classList.toggle('show');
    } else {
        sidebar.classList.toggle('collapsed');
    }
}

// ==================== MODALS ====================
function showModal(id) {
    document.getElementById(id).classList.add('show');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('show');
}

function closeModalOverlay(event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.classList.remove('show');
    }
}

// ==================== TABS ====================
function switchTab(el, tabId) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
}

// ==================== ROOM DETAIL ====================
function selectRoom(el) {
    document.querySelectorAll('.room-item').forEach(i => i.classList.remove('active'));
    el.classList.add('active');

    // Animate selection
    const panel = document.querySelector('.room-detail-panel');
    panel.style.opacity = '0';
    panel.style.transform = 'translateY(10px)';
    setTimeout(() => {
        panel.style.transition = 'all 0.3s ease';
        panel.style.opacity = '1';
        panel.style.transform = 'translateY(0)';
    }, 50);
}

function generateSeats() {
    const grid = document.getElementById('seat-grid');
    if (!grid || grid.children.length > 0) return;
    grid.innerHTML = '';
    for (let i = 1; i <= 50; i++) {
        const seat = document.createElement('div');
        seat.className = 'seat';
        seat.textContent = i;
        seat.addEventListener('click', function() {
            this.style.background = this.style.background === 'rgb(26, 125, 232)' ? '' : '#1a7de8';
            this.style.color = this.style.color === 'white' ? '' : 'white';
        });
        grid.appendChild(seat);
    }
}

// ==================== ANIMATED COUNTERS ====================
function animateStatNumbers() {
    document.querySelectorAll('.stat-number[data-count]').forEach(el => {
        const target = parseInt(el.getAttribute('data-count'));
        let current = 0;
        const step = Math.max(1, Math.floor(target / 30));
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            el.textContent = current;
        }, 40);
    });
}

// ==================== CHARTS ====================
let barChartInstance = null;
let pieChartInstance = null;

function drawCharts() {
    drawBarChart();
    drawPieChart();
}

function drawBarChart() {
    const canvas = document.getElementById('barChart');
    if (!canvas) return;

    if (barChartInstance) {
        barChartInstance.destroy();
    }

    const ctx = canvas.getContext('2d');
    barChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15'],
            datasets: [{
                label: 'Số lượt đặt',
                data: [3, 5, 2, 7, 4, 6, 8, 5, 3, 9, 6, 4, 7, 10, 8],
                backgroundColor: 'rgba(10, 94, 176, 0.7)',
                borderColor: 'rgba(10, 94, 176, 1)',
                borderWidth: 1,
                borderRadius: 4,
                barPercentage: 0.6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1a1f36',
                    titleFont: { family: 'Inter' },
                    bodyFont: { family: 'Inter' },
                    padding: 12,
                    cornerRadius: 8,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(0,0,0,0.05)' },
                    ticks: { font: { family: 'Inter', size: 11 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { family: 'Inter', size: 11 } }
                }
            }
        }
    });
}

function drawPieChart() {
    const canvas = document.getElementById('pieChart');
    if (!canvas) return;

    if (pieChartInstance) {
        pieChartInstance.destroy();
    }

    const ctx = canvas.getContext('2d');
    pieChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['P202 – Phòng máy', 'P101 – Phòng học', 'P305 – Hội trường', 'A101 – Phòng học', 'Khác'],
            datasets: [{
                data: [32, 28, 15, 8, 4],
                backgroundColor: [
                    '#0a5eb0',
                    '#1a7de8',
                    '#f97316',
                    '#8b5cf6',
                    '#6b7280',
                ],
                borderWidth: 2,
                borderColor: '#ffffff',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '55%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { family: 'Inter', size: 11 },
                        padding: 14,
                        usePointStyle: true,
                        pointStyleWidth: 10,
                    }
                },
                tooltip: {
                    backgroundColor: '#1a1f36',
                    titleFont: { family: 'Inter' },
                    bodyFont: { family: 'Inter' },
                    padding: 12,
                    cornerRadius: 8,
                }
            }
        }
    });
}

// ==================== TOAST ====================
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️'
    };

    toast.innerHTML = `<span>${icons[type]}</span> ${message}`;
    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}

// ==================== KEYBOARD SHORTCUTS ====================
document.addEventListener('keydown', (e) => {
    // Enter to login
    if (e.key === 'Enter' && document.getElementById('login-screen').classList.contains('active')) {
        handleLogin();
    }
    // Escape to close modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.show').forEach(m => m.classList.remove('show'));
    }
});

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', () => {
    // Generate seats (pre-generate)
    generateSeats();
});
