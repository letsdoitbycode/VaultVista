// Get the to-do list container and input field
const todoItems = document.getElementById('todoItems');
const todoInput = document.getElementById('todoInput');
const addTodoBtn = document.getElementById('addTodoBtn');

// Load existing to-do list from localStorage
document.addEventListener('DOMContentLoaded', function() {
    loadTodos();
});

// Add new task
addTodoBtn.addEventListener('click', function() {
    const taskText = todoInput.value.trim();
    if (taskText) {
        const todos = getTodosFromStorage();
        todos.push(taskText);
        saveTodosToStorage(todos);
        todoInput.value = ''; 
        loadTodos(); 
    }
});

// Remove a task
function removeTodo(index) {
    const todos = getTodosFromStorage();
    todos.splice(index, 1);
    saveTodosToStorage(todos);
    loadTodos();
}

// Load to-do list from localStorage
function loadTodos() {
    const todos = getTodosFromStorage();
    todoItems.innerHTML = '';
    todos.forEach((todo, index) => {
        const todoItem = document.createElement('li');
        todoItem.classList.add('list-group-item');
        todoItem.innerHTML = `
            ${todo}
            <button 
            class="btn btn-danger btn-sm float-right delete-btn" 
            onclick="removeTodo(${index})">Delete</button>
        `;
        todoItems.appendChild(todoItem);
    });
}

// Get to-do list from localStorage
function getTodosFromStorage() {
    const todos = localStorage.getItem('todos');
    return todos ? JSON.parse(todos) : [];
}

// Save to-do list to localStorage
function saveTodosToStorage(todos) {
    localStorage.setItem('todos', JSON.stringify(todos));
}
