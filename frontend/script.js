// ===== КОНФИГУРАЦИЯ =====
// Для локального запуска:
const API_URL = '';

// Для GitHub Codespaces (замени после запуска):
// const API_URL = 'https://ddenisovspb-source.ваш-код.app.github.dev';

let state = {
    projects: [],
    selectedProjects: [],
    columns: [],
    selectedColumns: [],
    data: []
};

async function init() {
    try {
        await loadProjects();
        await loadColumns();
        
        state.selectedProjects = [...state.projects];
        state.selectedColumns = state.columns.slice(0, 5);
        
        renderButtons();
        await updateData();
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Не удалось подключиться к серверу. Запустите backend.');
    }
}

async function loadProjects() {
    const response = await fetch(`${API_URL}/projects`);
    const data = await response.json();
    state.projects = data.projects;
}

async function loadColumns() {
    const response = await fetch(`${API_URL}/columns`);
    const data = await response.json();
    state.columns = data.columns;
}

async function updateData() {
    if (state.selectedProjects.length === 0 || state.selectedColumns.length === 0) {
        state.data = [];
        renderTable();
        updateRowCount(0);
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                projects: state.selectedProjects,
                columns: state.selectedColumns
            })
        });
        
        const data = await response.json();
        state.data = data.data;
        renderTable();
        updateRowCount(data.total_rows || 0);
    } catch (error) {
        console.error('Ошибка загрузки:', error);
    }
}

function renderButtons() {
    renderProjectButtons();
    renderColumnButtons();
}

function renderProjectButtons() {
    const container = document.getElementById('project-buttons');
    container.innerHTML = '';
    
    state.projects.forEach(project => {
        const btn = document.createElement('button');
        btn.className = `btn-select ${state.selectedProjects.includes(project) ? 'active active-project' : ''}`;
        btn.textContent = project;
        btn.onclick = () => toggleProject(project);
        container.appendChild(btn);
    });
}

function renderColumnButtons() {
    const container = document.getElementById('column-buttons');
    container.innerHTML = '';
    
    state.columns.forEach(column => {
        const btn = document.createElement('button');
        btn.className = `btn-select ${state.selectedColumns.includes(column) ? 'active active-column' : ''}`;
        btn.textContent = column;
        btn.onclick = () => toggleColumn(column);
        container.appendChild(btn);
    });
}

function toggleProject(project) {
    const index = state.selectedProjects.indexOf(project);
    if (index > -1) {
        state.selectedProjects.splice(index, 1);
    } else {
        state.selectedProjects.push(project);
    }
    renderProjectButtons();
}

function toggleColumn(column) {
    const index = state.selectedColumns.indexOf(column);
    if (index > -1) {
        state.selectedColumns.splice(index, 1);
    } else {
        state.selectedColumns.push(column);
    }
    renderColumnButtons();
}

function renderTable() {
    const thead = document.getElementById('table-header');
    const tbody = document.getElementById('table-body');
    
    if (state.data.length === 0) {
        thead.innerHTML = '';
        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="empty-state">
                    <div class="icon">📭</div>
                    <h3>Нет данных</h3>
                    <p>Выберите проекты и колонки</p>
                </td>
            </tr>
        `;
        return;
    }
    
    const headers = Object.keys(state.data[0]);
    thead.innerHTML = '';
    const headerRow = document.createElement('tr');
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        const isNumeric = state.data.some(row => typeof row[header] === 'number');
        if (isNumeric) th.classList.add('numeric');
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    
    tbody.innerHTML = '';
    state.data.forEach(row => {
        const tr = document.createElement('tr');
        headers.forEach(header => {
            const td = document.createElement('td');
            const value = row[header];
            if (value === null || value === undefined) {
                td.textContent = '—';
            } else if (typeof value === 'number') {
                td.textContent = value.toLocaleString('ru-RU', { 
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 2
                });
                td.classList.add('numeric');
            } else {
                td.textContent = value;
            }
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

function updateRowCount(count) {
    document.getElementById('row-count').textContent = `${count} строк`;
}

document.getElementById('update-btn').addEventListener('click', updateData);

init();
