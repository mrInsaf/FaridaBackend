const teacherId = 5061328116;  // Известный заранее teacher_id
const groupsSelect = document.getElementById("groups");
const studentsTable = document.getElementById("studentsTable").getElementsByTagName('tbody')[0];
const deleteButton = document.getElementById('deleteButton');
const baseUrl = 'http://185.50.202.243:8000';  // Выделенный baseUrl

// Функция для получения групп
async function fetchGroups() {
    try {
        const response = await fetch(`${baseUrl}/groups/${teacherId}`);
        if (!response.ok) {
            throw new Error("Не удалось получить группы");
        }

        const groups = await response.json();
        groupsSelect.innerHTML = '';

        groups.forEach(group => {
            const option = document.createElement("option");
            option.value = group[1];
            option.textContent = group[0];
            groupsSelect.appendChild(option);
        });
        console.log(groups);
    } catch (error) {
        console.error("Ошибка при получении групп:", error);
        groupsSelect.innerHTML = '<option value="">Не удалось загрузить группы</option>';
    }
}

// Функция для получения студентов по выбранной группе
async function fetchStudents(groupId) {
    try {
        const response = await fetch(`${baseUrl}/students/group/${groupId}`);
        if (!response.ok) {
            throw new Error("Не удалось получить студентов");
        }

        const students = await response.json();
        studentsTable.innerHTML = '';

        if (students.length === 0) {
            studentsTable.innerHTML = '<tr><td colspan="3">Студенты не найдены</td></tr>';
        } else {
            console.log(students);
            students.forEach(student => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td><input type="checkbox" class="student-checkbox" data-student-id="${student[0]}"></td>
                    <td>${student[0]}</td>
                    <td>${student[1]}</td>
                `;
                studentsTable.appendChild(row);
            });
            // После добавления чекбоксов, добавляем обработчики событий
            updateDeleteButtonVisibility();
            addCheckboxEventListeners();
        }
    } catch (error) {
        console.error("Ошибка при получении студентов:", error);
        studentsTable.innerHTML = '<tr><td colspan="3">Не удалось загрузить студентов</td></tr>';
    }
}

// Функция для удаления выбранных студентов
async function deleteSelected() {
    const checkboxes = document.querySelectorAll('#studentsTable tbody input[type="checkbox"]:checked');
    const idsToDelete = Array.from(checkboxes).map(checkbox => checkbox.dataset.studentId);

    if (idsToDelete.length === 0) {
        alert("Не выбраны студенты для удаления");
        return;
    }

    try {
        const response = await fetch(`${baseUrl}/students/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ student_ids: idsToDelete })
        });

        if (!response.ok) {
            throw new Error("Не удалось удалить студентов");
        }

        const result = await response.json();

        idsToDelete.forEach(id => {
            const row = document.querySelector(`#studentsTable tbody input[data-student-id="${id}"]`).closest('tr');
            row.remove();
        });

        alert(result.message);
        updateDeleteButtonVisibility(); // Обновляем видимость кнопки после удаления
    } catch (error) {
        console.error("Ошибка при удалении студентов:", error);
        alert("Не удалось удалить выбранных студентов");
    }
}

// Функция для управления видимостью кнопки
function updateDeleteButtonVisibility() {
    const checkboxes = document.querySelectorAll('#studentsTable tbody input[type="checkbox"]');
    const hasChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
    deleteButton.style.display = hasChecked ? 'block' : 'none';
}

// Функция для добавления обработчиков событий к чекбоксам
function addCheckboxEventListeners() {
    const checkboxes = document.querySelectorAll('#studentsTable tbody input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateDeleteButtonVisibility);
    });
}

// Вызов функции для получения групп при загрузке страницы
window.onload = fetchGroups;

// Обработка отправки выбранной группы
function submitGroup() {
    const selectedGroupId = groupsSelect.value;
    if (selectedGroupId) {
        fetchStudents(selectedGroupId);
    } else {
        alert("Пожалуйста, выберите группу");
    }
}

// Добавляем обработчик события к кнопке "Удалить"
deleteButton.addEventListener('click', deleteSelected);

// Функция для добавления студента
async function addStudent(event) {
    event.preventDefault(); // Предотвратить стандартное поведение формы

    const studentName = document.getElementById('studentName').value;
    const selectedGroupId = groupsSelect.value;

    if (!studentName || !selectedGroupId) {
        alert("Пожалуйста, заполните все поля и выберите группу");
        return;
    }

    try {
        const response = await fetch(`${baseUrl}/students/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: studentName,
                group_id: selectedGroupId
            })
        });

        if (!response.ok) {
            throw new Error("Не удалось добавить студента");
        }

        const result = await response.json();
        alert(result.message);

        // Очистка формы
        document.getElementById('studentForm').reset();

        // Обновление таблицы студентов
        fetchStudents(selectedGroupId);
    } catch (error) {
        console.error("Ошибка при добавлении студента:", error);
        alert("Не удалось добавить студента");
    }
}

// Добавляем обработчик события к форме
document.getElementById('studentForm').addEventListener('submit', addStudent);
